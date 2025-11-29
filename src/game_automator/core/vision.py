import asyncio
import base64
import os
from io import BytesIO
from typing import Optional, List, Dict
from PIL import Image
import anthropic
import aiohttp


def image_to_base64(image: Image.Image) -> str:
    """Convert PIL Image to base64 string."""
    buffer = BytesIO()
    image.save(buffer, format="PNG")
    return base64.standard_b64encode(buffer.getvalue()).decode("utf-8")


def extract_building_info(image: Image.Image, api_key: Optional[str] = None) -> Optional[dict]:
    """
    Use Claude to extract building name, level, and investment progress from screenshot.
    Returns dict with 'name', 'level', 'current', 'max' or None if extraction failed.
    """
    if api_key is None:
        api_key = os.environ.get("ANTHROPIC_API_KEY")
    
    if not api_key:
        raise ValueError("ANTHROPIC_API_KEY not set. Export it or pass api_key parameter.")
    
    client = anthropic.Anthropic(api_key=api_key)
    
    image_data = image_to_base64(image)
    
    message = client.messages.create(
        model="claude-sonnet-4-20250514",
        max_tokens=256,
        messages=[
            {
                "role": "user",
                "content": [
                    {
                        "type": "image",
                        "source": {
                            "type": "base64",
                            "media_type": "image/png",
                            "data": image_data,
                        },
                    },
                    {
                        "type": "text",
                        "text": """Look at this game screenshot and extract:
1. The building name (e.g., "Laboratory", "Academy", "Wizard Tower", "Tailor Workshop")
2. The building level (the number in the purple/pink shield icon next to the building name, e.g., "17")
3. The investment progress shown on the progress bar (e.g., "19/2,000")

Respond with ONLY a single line in this exact format:
BUILDING_NAME|LEVEL|CURRENT|MAX

For example:
Tailor Workshop|17|19|2000

If you cannot find the information, respond with:
NOT_FOUND"""
                    }
                ],
            }
        ],
    )
    
    response_text = message.content[0].text.strip()
    
    if response_text == "NOT_FOUND":
        return None
    
    try:
        parts = response_text.split("|")
        if len(parts) == 4:
            return {
                "name": parts[0].strip(),
                "level": parts[1].strip(),
                "current": parts[2].strip().replace(",", ""),
                "max": parts[3].strip().replace(",", ""),
            }
    except Exception:
        pass
    
    return None


async def extract_building_info_async(
    session: aiohttp.ClientSession,
    image: Image.Image,
    index: int,
    api_key: str
) -> Dict:
    """
    Async version - extract building info from a single image.
    Returns dict with index, and either data or error.
    """
    image_data = image_to_base64(image)
    
    headers = {
        "Content-Type": "application/json",
        "x-api-key": api_key,
        "anthropic-version": "2023-06-01"
    }
    
    payload = {
        "model": "claude-sonnet-4-20250514",
        "max_tokens": 256,
        "messages": [
            {
                "role": "user",
                "content": [
                    {
                        "type": "image",
                        "source": {
                            "type": "base64",
                            "media_type": "image/png",
                            "data": image_data,
                        },
                    },
                    {
                        "type": "text",
                        "text": """Look at this game screenshot and extract:
1. The building name (e.g., "Laboratory", "Academy", "Wizard Tower", "Tailor Workshop")
2. The building level (the number in the purple/pink shield icon next to the building name, e.g., "17")
3. The investment progress shown on the progress bar (e.g., "19/2,000")

Respond with ONLY a single line in this exact format:
BUILDING_NAME|LEVEL|CURRENT|MAX

For example:
Tailor Workshop|17|19|2000

If you cannot find the information, respond with:
NOT_FOUND"""
                    }
                ],
            }
        ],
    }
    
    try:
        async with session.post(
            "https://api.anthropic.com/v1/messages",
            headers=headers,
            json=payload
        ) as response:
            if response.status != 200:
                error_text = await response.text()
                return {"index": index, "error": f"API error {response.status}: {error_text}"}
            
            data = await response.json()
            response_text = data["content"][0]["text"].strip()
            
            if response_text == "NOT_FOUND":
                return {"index": index, "error": "NOT_FOUND"}
            
            parts = response_text.split("|")
            if len(parts) == 4:
                return {
                    "index": index,
                    "data": {
                        "name": parts[0].strip(),
                        "level": parts[1].strip(),
                        "current": parts[2].strip().replace(",", ""),
                        "max": parts[3].strip().replace(",", ""),
                    }
                }
            
            return {"index": index, "error": f"Parse error: {response_text}"}
            
    except Exception as e:
        return {"index": index, "error": str(e)}


async def extract_all_buildings_async(
    images: List[Image.Image],
    api_key: Optional[str] = None,
    max_concurrent: int = 10
) -> List[Optional[Dict]]:
    """
    Extract building info from multiple images concurrently.
    Returns list of results in same order as input images.
    """
    if api_key is None:
        api_key = os.environ.get("ANTHROPIC_API_KEY")
    
    if not api_key:
        raise ValueError("ANTHROPIC_API_KEY not set.")
    
    semaphore = asyncio.Semaphore(max_concurrent)
    
    async def limited_extract(session, image, index):
        async with semaphore:
            return await extract_building_info_async(session, image, index, api_key)
    
    async with aiohttp.ClientSession() as session:
        tasks = [
            limited_extract(session, img, i) 
            for i, img in enumerate(images)
        ]
        results = await asyncio.gather(*tasks)
    
    results.sort(key=lambda x: x["index"])
    
    output = []
    for r in results:
        if "data" in r:
            output.append(r["data"])
        else:
            print(f"[WARNING] Image {r['index']}: {r.get('error', 'Unknown error')}")
            output.append(None)
    
    return output


def extract_all_buildings(images: List[Image.Image], api_key: Optional[str] = None) -> List[Optional[Dict]]:
    """
    Synchronous wrapper for async batch extraction.
    """
    return asyncio.run(extract_all_buildings_async(images, api_key))