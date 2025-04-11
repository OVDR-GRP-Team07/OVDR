"""
General Helper Utilities
Author: Zixin Ding

This module contains utility functions for formatting and converting image paths.
"""

import os

BASE_URL = "http://localhost:5000/data/clothes/"

def format_image_url(image_path):
    """
    Convert a local image path to a full accessible URL.

    Args:
        image_path (str): The relative or local path to the image.

    Returns:
        str: A full URL to access the image from the frontend.
    """
    path = os.path.normpath(image_path).replace(os.sep, '/')
    if path.startswith("data/clothes/"):
        path = path[len("data/clothes/"):]  # Strip prefix to get relative URL path
    return f"{BASE_URL}{path}"

