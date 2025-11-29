import time
import random
from typing import Dict, List, Tuple, Optional
from abc import ABC, abstractmethod

from game_automator.core.window import find_window
from game_automator.core.capture import capture_window, capture_region
from game_automator.core.ocr import extract_text, extract_text_with_positions, find_text
from game_automator.core.input import click_in_window, humanized_click_in_window, click_region_center
from game_automator.core.storage import CSVStorage
from game_automator.engine.models import Screen, Transition, Region
from game_automator.engine.state import identify_screen, wait_for_screen
from game_automator.engine.navigator import navigate, click_landmark


class BaseWorkflow(ABC):
    """Base class for all workflows."""
    
    # Subclasses must define these
    name: str = "base"
    description: str = "Base workflow"
    csv_columns: List[str] = []
    window_title: str = "Shop Titans"
    
    # Screen and transition definitions
    screens: Dict[str, Screen] = {}
    transitions: Dict[Tuple[str, str], Transition] = {}
    
    def __init__(self):
        self.window: Optional[dict] = None
        self.storage: Optional[CSVStorage] = None
    
    def setup(self) -> bool:
        """Initialize the workflow. Returns True if successful."""
        # Find game window
        self.window = find_window(self.window_title)
        if not self.window:
            print(f"[ERROR] Could not find window '{self.window_title}'")
            return False
        
        print(f"[INFO] Found window: {self.window['title']} ({self.window['width']}x{self.window['height']})")
        
        # Initialize CSV storage
        if self.csv_columns:
            self.storage = CSVStorage(self.name, self.csv_columns)
            print(f"[INFO] Output file: {self.storage.get_filepath()}")
        
        return True
    
    @abstractmethod
    def run(self) -> None:
        """Main workflow logic. Subclasses must implement this."""
        pass
    
    def execute(self) -> bool:
        """Run the full workflow with setup and teardown."""
        print(f"[INFO] Starting workflow: {self.name}")
        
        if not self.setup():
            return False
        
        try:
            self.run()
            print(f"[INFO] Workflow complete")
            return True
        except KeyboardInterrupt:
            print(f"\n[INFO] Workflow interrupted by user")
            return False
        except Exception as e:
            print(f"[ERROR] Workflow failed: {e}")
            self.save_debug_screenshot()
            raise
    
    # Helper methods for subclasses
    
    def current_screen(self) -> Optional[str]:
        """Identify the current screen."""
        return identify_screen(self.window, self.screens)
    
    def wait_for(self, screen_name: str, timeout: float = 5.0) -> bool:
        """Wait for a specific screen to appear."""
        return wait_for_screen(self.window, self.screens, screen_name, timeout)
    
    def navigate_to(self, target: str) -> bool:
        """Navigate to a target screen."""
        print(f"[NAV] Navigating to '{target}'...")
        return navigate(self.window, self.screens, self.transitions, target)
    
    def capture(self) -> "Image":
        """Capture the full game window."""
        return capture_window(self.window)
    
    def capture_region(self, region: Region) -> "Image":
        """Capture a specific region."""
        return capture_region(self.window, region.as_tuple())
    
    def get_text(self, region: Optional[Region] = None) -> str:
        """Extract text from region or full screen."""
        if region:
            img = self.capture_region(region)
        else:
            img = self.capture()
        return extract_text(img)
    
    def get_text_with_positions(self, region: Optional[Region] = None) -> List[dict]:
        """Extract text with bounding boxes."""
        if region:
            img = self.capture_region(region)
        else:
            img = self.capture()
        return extract_text_with_positions(img)
    
    def find_and_click(self, text: str) -> bool:
        """Find text on screen and click it."""
        return click_landmark(self.window, text)
    
    def click(self, x: int, y: int) -> None:
        """Click at window-relative coordinates."""
        humanized_click_in_window(self.window, x, y)
    
    def click_region(self, region: Region) -> None:
        """Click the center of a region."""
        click_region_center(self.window, region.as_tuple())
    
    def write_row(self, **data) -> None:
        """Write a row to the CSV output."""
        if self.storage:
            self.storage.write_row(**data)
    
    def sleep(self, seconds: float, randomize: bool = True) -> None:
        """Sleep with optional randomization."""
        if randomize:
            seconds = seconds + random.uniform(0, seconds * 0.2)
        time.sleep(seconds)
    
    def save_debug_screenshot(self) -> None:
        """Save a screenshot for debugging."""
        try:
            img = self.capture()
            path = f"output/debug-{self.name}-{int(time.time())}.png"
            img.save(path)
            print(f"[DEBUG] Screenshot saved: {path}")
        except Exception:
            pass