import os
import time
from typing import List, Optional, Dict

from PIL import Image

from game_automator.workflows.base import BaseWorkflow
from game_automator.engine.models import Screen, Landmark, Region
from game_automator.core.input import press_key
from game_automator.core.vision import extract_all_buildings
from game_automator.core.discord import post_table_to_discord


class CityInvestmentScanWorkflow(BaseWorkflow):
    """Scans all city buildings and records their investment progress."""
    
    name = "city-investment-scan"
    description = "Extracts investment progress from all city buildings"
    csv_columns = ["building_name", "current_investment", "max_investment"]
    window_title = "Shop Titans"
    
    # All building names from the game
    BUILDING_NAMES = [
        "Academy", "Apothecary", "Emerald Inn", "Ether Well", "Garden",
        "Iron Mine", "Ironwood Sawmill", "Jewel Storehouse", "Jewel Workshop",
        "Laboratory", "Lumberyard", "Master Lodge", "Mausoleum", "Oil Press",
        "Smelter", "Smithy", "Summoner's Tent", "Tailor Workshop", "Tannery",
        "Tavern", "Temple", "Town Hall", "Training Hall", "Weaver Mill",
        "Wizard Tower", "Wood Workshop",
    ]
    
    # Screen definitions
    screens = {
        "shop": Screen(
            landmarks=[Landmark(text="City", region=Region(80, 900, 100, 80))]
        ),
        "city": Screen(
            landmarks=[Landmark(text="Shop", region=Region(180, 900, 100, 80))]
        ),
        "building_detail": Screen(
            landmarks=[Landmark(text="Investment", region=Region(200, 640, 150, 50))]
        ),
    }
    
    def __init__(self):
        super().__init__()
        self.collected_data: List[Dict] = []
    
    def run(self):
        self.collected_data = []
        screenshots: List[Image.Image] = []
        
        # Step 1: Navigate to city
        print("[WORKFLOW] Attempting to navigate to City...")
        
        if not self.click_until_screen_changes("City", "Shop", max_retries=4):
            print("[ERROR] Failed to navigate to City after all retries")
            return
        
        print("[WORKFLOW] Successfully navigated to City!")
        self.sleep(1)
        
        # Step 2: Click on any character to open the panel
        print("[WORKFLOW] Looking for a character to click...")
        if not self.click_any_character_with_retry(max_retries=4):
            print("[ERROR] Could not click any character")
            return
        
        print("[WORKFLOW] Panel is open, collecting screenshots...")
        self.sleep(1)
        
        # Step 3: Capture first screenshot and detect building name
        first_screenshot = self.capture()
        first_building_name = self.detect_building_name_fast(first_screenshot)
        
        if not first_building_name:
            print("[WARNING] Could not detect first building name, will collect max 35 screenshots")
            first_building_name = None
        else:
            print(f"[WORKFLOW] First building: {first_building_name}")
        
        screenshots.append(first_screenshot.copy())
        print(f"[WORKFLOW] Captured screenshot 1")
        
        # Step 4: Press right arrow and capture screenshots until we loop back
        max_buildings = 35  # Safety limit
        
        for i in range(max_buildings - 1):
            press_key("right")
            self.sleep(1.0)  # Wait for animation
            
            screenshot = self.capture()
            
            # Check if we've looped back to first building
            if first_building_name:
                current_building = self.detect_building_name_fast(screenshot)
                if current_building == first_building_name:
                    print(f"[WORKFLOW] Detected loop back to '{first_building_name}' at screenshot {i+2}")
                    break
            
            screenshots.append(screenshot.copy())
            print(f"[WORKFLOW] Captured screenshot {len(screenshots)}")
        
        # Step 5: Close panel and return to shop
        print("[WORKFLOW] Closing panel...")
        self.close_building_panel()
        self.sleep(1)
        
        print("[WORKFLOW] Returning to shop...")
        self.find_and_click("Shop")
        self.sleep(1)
        
        # Step 6: Process all screenshots with Claude (async/parallel)
        print(f"[WORKFLOW] Processing {len(screenshots)} screenshots with Claude...")
        results = extract_all_buildings(screenshots)
        
        # Step 7: Record results (already deduplicated by loop detection)
        seen_buildings = set()
        for i, result in enumerate(results):
            if result is None:
                print(f"[WARNING] Could not extract data from screenshot {i+1}")
                continue
            
            # Extra deduplication in case loop detection missed something
            if result["name"] in seen_buildings:
                print(f"[WORKFLOW] Skipping duplicate: {result['name']}")
                continue
            
            seen_buildings.add(result["name"])
            self.record_building(result)
        
        print(f"[WORKFLOW] Complete! Recorded {len(self.collected_data)} buildings.")
        
        # Step 8: Post to Discord
        self.post_results_to_discord()
    
    def detect_building_name_fast(self, image: Image.Image) -> Optional[str]:
        """
        Use local OCR to quickly detect building name.
        This is faster than Claude and used for loop detection.
        """
        from game_automator.core.ocr import extract_text
        
        text = extract_text(image).lower()
        
        for name in self.BUILDING_NAMES:
            if name.lower() in text:
                return name
            # Also check first word for multi-word names
            first_word = name.split()[0].lower()
            if len(first_word) > 4 and first_word in text:
                return name
        
        return None
    
    def record_building(self, building_data: Dict):
        """Record building data to CSV and memory."""
        self.write_row(
            building_name=building_data["name"],
            current_investment=building_data["current"],
            max_investment=building_data["max"],
        )
        self.collected_data.append({
            "building_name": building_data["name"],
            "current_investment": building_data["current"],
            "max_investment": building_data["max"],
        })
        print(f"[WORKFLOW] Recorded: {building_data['name']} - {building_data['current']}/{building_data['max']}")
    
    def post_results_to_discord(self):
        """Post collected results to Discord."""
        webhook_url = os.environ.get("DISCORD_WEBHOOK_URL")
        
        if not webhook_url:
            print("[INFO] DISCORD_WEBHOOK_URL not set, skipping Discord post")
            return
        
        if not self.collected_data:
            print("[INFO] No data collected, skipping Discord post")
            return
        
        print("[WORKFLOW] Posting results to Discord...")
        
        sorted_data = sorted(
            self.collected_data, 
            key=lambda x: int(x["current_investment"])
        )
        
        success = post_table_to_discord(
            webhook_url=webhook_url,
            title="🏰 City Investment Report",
            data=sorted_data,
            columns=["building_name", "current_investment", "max_investment"],
            column_headers=["Building", "Current", "Max"]
        )
        
        if success:
            print("[WORKFLOW] Posted to Discord successfully!")
        else:
            print("[ERROR] Failed to post to Discord")
    
    def click_until_screen_changes(self, click_text: str, expect_text: str, max_retries: int = 4) -> bool:
        for attempt in range(1, max_retries + 1):
            print(f"[WORKFLOW] Attempt {attempt}/{max_retries}: clicking '{click_text}'...")
            
            if not self.find_and_click(click_text):
                print(f"[WORKFLOW] Could not find '{click_text}' on screen")
                self.sleep(1)
                continue
            
            self.sleep(1.5)
            
            screen_text = self.get_text()
            if expect_text.lower() in screen_text.lower():
                return True
            
            print(f"[WORKFLOW] Screen did not change ('{expect_text}' not found), retrying...")
            self.sleep(0.5)
        
        return False
    
    def is_panel_open(self) -> bool:
        screen_text = self.get_text().lower()
        return any(term in screen_text for term in ["investment", "nvestment", "invest", "investors"])
    
    def click_any_character_with_retry(self, max_retries: int = 4) -> bool:
        for attempt in range(1, max_retries + 1):
            print(f"[WORKFLOW] Attempt {attempt}/{max_retries}: looking for character...")
            
            results = self.get_text_with_positions()
            
            char_found = False
            for result in results:
                text = result["text"].lower()
                if ("lv" in text or "lu" in text) and "hire" not in text:
                    bbox = result["bbox"]
                    center_x = bbox[0] + bbox[2] // 2
                    center_y = bbox[1] + bbox[3] // 2
                    
                    print(f"[WORKFLOW] Found '{result['text']}' - clicking at ({center_x}, {center_y})")
                    
                    self.click(center_x, center_y)
                    char_found = True
                    break
            
            if not char_found:
                print("[WORKFLOW] No character found on screen")
                self.sleep(1)
                continue
            
            self.sleep(2)
            
            if self.is_panel_open():
                print("[WORKFLOW] Panel opened successfully!")
                return True
            else:
                print("[WORKFLOW] Panel did not open, retrying...")
        
        return False
    
    def close_building_panel(self):
        if not self.find_and_click("X"):
            self.click(680, 610)