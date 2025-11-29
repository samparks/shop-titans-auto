from typing import Optional, List
import Quartz


def find_window(title_substring: str) -> Optional[dict]:
    """
    Find a window by title substring.
    Returns dict with window info or None if not found.
    """
    window_list = Quartz.CGWindowListCopyWindowInfo(
        Quartz.kCGWindowListOptionOnScreenOnly | Quartz.kCGWindowListExcludeDesktopElements,
        Quartz.kCGNullWindowID
    )
    
    for window in window_list:
        name = window.get(Quartz.kCGWindowName, "")
        owner = window.get(Quartz.kCGWindowOwnerName, "")
        
        if title_substring.lower() in (name or "").lower():
            bounds = window.get(Quartz.kCGWindowBounds)
            return {
                "id": window.get(Quartz.kCGWindowNumber),
                "title": name,
                "owner": owner,
                "x": int(bounds["X"]),
                "y": int(bounds["Y"]),
                "width": int(bounds["Width"]),
                "height": int(bounds["Height"]),
            }
    
    return None


def list_windows() -> List[dict]:
    """List all visible windows with titles."""
    window_list = Quartz.CGWindowListCopyWindowInfo(
        Quartz.kCGWindowListOptionOnScreenOnly | Quartz.kCGWindowListExcludeDesktopElements,
        Quartz.kCGNullWindowID
    )
    
    windows = []
    for window in window_list:
        name = window.get(Quartz.kCGWindowName, "")
        if name:
            bounds = window.get(Quartz.kCGWindowBounds)
            windows.append({
                "id": window.get(Quartz.kCGWindowNumber),
                "title": name,
                "owner": window.get(Quartz.kCGWindowOwnerName, ""),
                "x": int(bounds["X"]),
                "y": int(bounds["Y"]),
                "width": int(bounds["Width"]),
                "height": int(bounds["Height"]),
            })
    
    return windows