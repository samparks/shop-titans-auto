from dataclasses import dataclass, field
from typing import Dict, List, Optional, Tuple


@dataclass
class Region:
    """A rectangular region relative to window top-left."""
    x: int
    y: int
    width: int
    height: int
    
    def as_tuple(self) -> Tuple[int, int, int, int]:
        return (self.x, self.y, self.width, self.height)
    
    def center(self) -> Tuple[int, int]:
        return (self.x + self.width // 2, self.y + self.height // 2)


@dataclass
class Landmark:
    """A text landmark used to identify a screen."""
    text: str
    region: Optional[Region] = None  # If None, search entire screen


@dataclass
class Screen:
    """Definition of a game screen."""
    landmarks: List[Landmark]
    data_regions: Dict[str, Region] = field(default_factory=dict)


@dataclass 
class Transition:
    """How to navigate from one screen to another."""
    click_landmark: Optional[str] = None  # Text to find and click
    click_region: Optional[Region] = None  # Or click a fixed region
    wait_for: Optional[str] = None  # Screen name to wait for
    timeout: float = 5.0