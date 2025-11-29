from typing import Dict, Tuple, Optional

from game_automator.core.capture import capture_window
from game_automator.core.ocr import find_text
from game_automator.core.input import click_in_window, click_region_center
from game_automator.engine.models import Screen, Transition
from game_automator.engine.state import identify_screen, wait_for_screen


def navigate(
    window: dict,
    screens: Dict[str, Screen],
    transitions: Dict[Tuple[str, str], Transition],
    target: str
) -> bool:
    """
    Navigate from current screen to target screen.
    Returns True if successful, False otherwise.
    """
    current = identify_screen(window, screens)
    
    if current is None:
        print("[NAV] Could not identify current screen")
        return False
    
    if current == target:
        return True
    
    transition_key = (current, target)
    if transition_key not in transitions:
        print(f"[NAV] No transition defined from '{current}' to '{target}'")
        return False
    
    transition = transitions[transition_key]
    
    # Execute the click
    if transition.click_landmark:
        if not click_landmark(window, transition.click_landmark):
            print(f"[NAV] Could not find landmark '{transition.click_landmark}'")
            return False
    elif transition.click_region:
        click_region_center(window, transition.click_region.as_tuple())
    
    # Wait for target screen
    if transition.wait_for:
        target_screen = transition.wait_for
    else:
        target_screen = target
    
    if wait_for_screen(window, screens, target_screen, transition.timeout):
        return True
    else:
        print(f"[NAV] Timeout waiting for screen '{target_screen}'")
        return False


def click_landmark(window: dict, text: str) -> bool:
    """
    Find text on screen and click it.
    Returns True if found and clicked, False otherwise.
    """
    image = capture_window(window)
    result = find_text(image, text)
    
    if result is None:
        return False
    
    # Click center of the found text
    bbox = result["bbox"]
    center_x = bbox[0] + bbox[2] // 2
    center_y = bbox[1] + bbox[3] // 2
    
    click_in_window(window, center_x, center_y)
    return True