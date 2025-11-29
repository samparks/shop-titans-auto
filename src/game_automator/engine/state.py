from typing import Dict, Optional
from PIL import Image

from game_automator.core.ocr import extract_text, find_text
from game_automator.core.capture import capture_window, capture_region
from game_automator.engine.models import Screen, Region


def identify_screen(window: dict, screens: Dict[str, Screen]) -> Optional[str]:
    """
    Identify which screen we're currently on by checking landmarks.
    Returns screen name or None if no match.
    """
    image = capture_window(window)
    
    for screen_name, screen in screens.items():
        if _screen_matches(image, window, screen):
            return screen_name
    
    return None


def _screen_matches(image: Image.Image, window: dict, screen: Screen) -> bool:
    """Check if all landmarks for a screen are present."""
    for landmark in screen.landmarks:
        if landmark.region:
            # Search within specific region
            region_img = image.crop((
                landmark.region.x,
                landmark.region.y,
                landmark.region.x + landmark.region.width,
                landmark.region.y + landmark.region.height,
            ))
            text = extract_text(region_img)
        else:
            # Search entire screen
            text = extract_text(image)
        
        if landmark.text.lower() not in text.lower():
            return False
    
    return True


def wait_for_screen(
    window: dict, 
    screens: Dict[str, Screen], 
    target: str, 
    timeout: float = 5.0,
    poll_interval: float = 0.5
) -> bool:
    """
    Wait for a specific screen to appear.
    Returns True if screen appeared, False if timeout.
    """
    import time
    
    start = time.time()
    while time.time() - start < timeout:
        current = identify_screen(window, screens)
        if current == target:
            return True
        time.sleep(poll_interval)
    
    return False