from typing import Optional, Tuple
import mss
from PIL import Image


def capture_window(window: dict) -> Image.Image:
    """
    Capture a screenshot of the specified window.
    Returns a PIL Image.
    """
    with mss.mss() as sct:
        monitor = {
            "left": window["x"],
            "top": window["y"],
            "width": window["width"],
            "height": window["height"],
        }
        screenshot = sct.grab(monitor)
        return Image.frombytes("RGB", screenshot.size, screenshot.bgra, "raw", "BGRX")


def capture_region(window: dict, region: Tuple[int, int, int, int]) -> Image.Image:
    """
    Capture a specific region within a window.
    Region is (x, y, width, height) relative to window top-left.
    Returns a PIL Image.
    """
    x, y, width, height = region
    with mss.mss() as sct:
        monitor = {
            "left": window["x"] + x,
            "top": window["y"] + y,
            "width": width,
            "height": height,
        }
        screenshot = sct.grab(monitor)
        return Image.frombytes("RGB", screenshot.size, screenshot.bgra, "raw", "BGRX")