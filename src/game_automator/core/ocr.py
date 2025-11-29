from typing import List, Tuple, Optional
import easyocr
from PIL import Image
import numpy as np

# Global reader instance (expensive to initialize)
_reader: Optional[easyocr.Reader] = None


def get_reader() -> easyocr.Reader:
    """Get or create the EasyOCR reader instance."""
    global _reader
    if _reader is None:
        _reader = easyocr.Reader(["en"], gpu=False)
    return _reader


def extract_text(image: Image.Image) -> str:
    """
    Extract all text from an image.
    Returns concatenated text.
    """
    reader = get_reader()
    img_array = np.array(image)
    results = reader.readtext(img_array)
    
    # Results are list of (bbox, text, confidence)
    return " ".join([text for _, text, _ in results])


def extract_text_with_positions(image: Image.Image) -> List[dict]:
    """
    Extract text with bounding box positions.
    Returns list of {text, confidence, bbox} dicts.
    bbox is (x, y, width, height) relative to image.
    """
    reader = get_reader()
    img_array = np.array(image)
    results = reader.readtext(img_array)
    
    extracted = []
    for bbox, text, confidence in results:
        # bbox is list of 4 corner points, convert to x, y, width, height
        x_coords = [p[0] for p in bbox]
        y_coords = [p[1] for p in bbox]
        x = int(min(x_coords))
        y = int(min(y_coords))
        width = int(max(x_coords) - x)
        height = int(max(y_coords) - y)
        
        extracted.append({
            "text": text,
            "confidence": confidence,
            "bbox": (x, y, width, height),
        })
    
    return extracted


def find_text(image: Image.Image, search_text: str, min_confidence: float = 0.5) -> Optional[dict]:
    """
    Find specific text in an image.
    Returns the first match with bbox, or None if not found.
    """
    results = extract_text_with_positions(image)
    search_lower = search_text.lower()
    
    for result in results:
        if search_lower in result["text"].lower() and result["confidence"] >= min_confidence:
            return result
    
    return None