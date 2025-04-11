"""
Caption Utilities
Author: Zixin Ding

Contains functions to generate human-readable titles from structured JSON-style clothing metadata.
"""


def generate_title(caption_dict):
    """
    Convert clothing metadata JSON to a readable title string.

    Args:
        caption_dict (dict): Dictionary containing clothing metadata.

    Returns:
        str: A human-friendly caption title.
    """
    if "upper cloth category" in caption_dict:
        category = caption_dict.get("upper cloth category", "")
    elif "lower cloth category" in caption_dict:
        category = caption_dict.get("lower cloth category", "")
    elif "dresses category" in caption_dict:
        category = caption_dict.get("dresses category", "")
    else:
        category = ""

    # Different details of different categories
    color = caption_dict.get("color", "").capitalize()
    pattern = caption_dict.get("pattern", "").capitalize() if caption_dict.get("pattern", "").lower() != "solid" else ""
    material = caption_dict.get("material", "").capitalize()
    neckline = caption_dict.get("neckline", "").capitalize()
    sleeve = caption_dict.get("sleeve", "").capitalize()
    length = caption_dict.get("length", "").capitalize()

    title_parts = [color, pattern, material, category.capitalize()]

    if "upper cloth category" in caption_dict:
        if neckline:
            title_parts.append(f"with {neckline.lower()} neckline")
        if sleeve:
            title_parts.append(f"and {sleeve.lower()} sleeves")

    elif "lower cloth category" in caption_dict:
        if length:
            title_parts.append(f"({length.lower()} length)")

    elif "dresses category" in caption_dict:
        if length:
            title_parts.append(f"({length.lower()} length)")
        if neckline:
            title_parts.append(f"with {neckline.lower()} neckline")

    return " ".join(filter(None, title_parts))
