import requests
from typing import List, Dict, Optional


def post_to_discord(webhook_url: str, content: str) -> bool:
    """Post a simple text message to Discord."""
    try:
        response = requests.post(webhook_url, json={"content": content})
        return response.status_code == 204
    except Exception as e:
        print(f"[ERROR] Failed to post to Discord: {e}")
        return False


def post_table_to_discord(
    webhook_url: str, 
    title: str,
    data: List[Dict], 
    columns: List[str],
    column_headers: Optional[List[str]] = None
) -> bool:
    """
    Post a formatted table to Discord.
    """
    if not column_headers:
        column_headers = columns
    
    # Build the table as a code block for monospace formatting
    lines = []
    lines.append(f"**{title}**")
    lines.append("```")
    
    # Calculate column widths
    widths = []
    for i, col in enumerate(columns):
        header_width = len(column_headers[i])
        data_width = max((len(str(row.get(col, ""))) for row in data), default=0)
        widths.append(max(header_width, data_width))
    
    # Header row
    header = " | ".join(h.ljust(widths[i]) for i, h in enumerate(column_headers))
    lines.append(header)
    lines.append("-" * len(header))
    
    # Data rows
    for row in data:
        line = " | ".join(str(row.get(col, "")).ljust(widths[i]) for i, col in enumerate(columns))
        lines.append(line)
    
    lines.append("```")
    
    content = "\n".join(lines)
    
    # Discord has a 2000 character limit
    if len(content) > 2000:
        return post_table_chunked(webhook_url, title, data, columns, column_headers)
    
    return post_to_discord(webhook_url, content)


def post_table_chunked(
    webhook_url: str,
    title: str, 
    data: List[Dict],
    columns: List[str],
    column_headers: List[str]
) -> bool:
    """Post a large table in multiple messages."""
    chunk_size = 15  # Buildings per message
    success = True
    
    for i in range(0, len(data), chunk_size):
        chunk = data[i:i + chunk_size]
        chunk_title = f"{title} (Part {i//chunk_size + 1})"
        
        if not post_table_to_discord(webhook_url, chunk_title, chunk, columns, column_headers):
            success = False
    
    return success