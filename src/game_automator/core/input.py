import time
import random
import pyautogui


# Safety settings
pyautogui.FAILSAFE = True  # Move mouse to corner to abort
pyautogui.PAUSE = 0.1  # Small pause between actions


def click(x: int, y: int, delay_after: float = 0.3) -> None:
    """
    Click at absolute screen coordinates.
    Uses explicit mouseDown/mouseUp for better Wine compatibility.
    """
    pyautogui.moveTo(x, y)
    time.sleep(0.05)
    pyautogui.mouseDown()
    time.sleep(0.05)
    pyautogui.mouseUp()
    time.sleep(delay_after)


def click_in_window(window: dict, x: int, y: int, delay_after: float = 0.3) -> None:
    """
    Click at coordinates relative to window top-left.
    """
    abs_x = window["x"] + x
    abs_y = window["y"] + y
    click(abs_x, abs_y, delay_after)


def click_region_center(window: dict, region: tuple, delay_after: float = 0.3) -> None:
    """
    Click the center of a region (x, y, width, height) relative to window.
    """
    rx, ry, rw, rh = region
    center_x = rx + rw // 2
    center_y = ry + rh // 2
    click_in_window(window, center_x, center_y, delay_after)


def humanized_click(x: int, y: int, delay_after: float = 0.3) -> None:
    """
    Click with slight randomization to appear more human.
    """
    offset_x = random.randint(-3, 3)
    offset_y = random.randint(-3, 3)
    pyautogui.moveTo(x + offset_x, y + offset_y)
    time.sleep(0.05)
    pyautogui.mouseDown()
    time.sleep(0.05)
    pyautogui.mouseUp()
    time.sleep(delay_after + random.uniform(0, 0.1))


def humanized_click_in_window(window: dict, x: int, y: int, delay_after: float = 0.3) -> None:
    """
    Click at window-relative coordinates with humanization.
    """
    abs_x = window["x"] + x
    abs_y = window["y"] + y
    humanized_click(abs_x, abs_y, delay_after)


def press_key(key: str, delay_after: float = 0.3) -> None:
    """
    Press a keyboard key.
    """
    pyautogui.press(key)
    time.sleep(delay_after)