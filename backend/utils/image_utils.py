"""
Image Utility Functions
Author: Zhihao Cao
Modifier: Zixin Ding

This module provides utility functions for managing user-uploaded images and generated try-on images.
It handles saving, deleting, and renaming image files used throughout the OVDR backend.

Functions:
    - get_user_image_path(user): Return the absolute path of a user's full-body image.
    - save_user_image(file, user_id): Save uploaded image and return both absolute and relative paths.
    - delete_user_image_if_exists(image_path): Delete an existing user image from disk if it exists.
    - rename_output_image(dir_path): Auto-generate the next image filename in sequence (e.g., 0000001.jpg).
"""

import os
from flask import current_app

def get_user_image_path(user):
    """
    Get the absolute file path of a user's uploaded image.

    Args:
        user (User): SQLAlchemy user object.

    Returns:
        str or None: Absolute image path or None if not found.
    """
    if not user.image_path:
        return None
    return os.path.abspath(os.path.join(current_app.root_path, "..", user.image_path))

def save_user_image(file, user_id):
    """
    Save a user's uploaded image to the data/users/image/ directory.

    Args:
        file (FileStorage): The uploaded file from Flask's request.files.
        user_id (int): The ID of the user uploading the image.

    Returns:
        tuple: (absolute_path, relative_path)
    """
    storage_dir = os.path.join(current_app.root_path, '..', 'data', 'users', 'image')
    os.makedirs(storage_dir, exist_ok=True)
    filename = f"{user_id}.jpg"
    filepath = os.path.join(storage_dir, filename)
    file.save(filepath)
    relative_path = os.path.join('data', 'users', 'image', filename).replace("\\", "/")
    return filepath, relative_path

def delete_user_image_if_exists(image_path):
    """
    Delete a user image from disk if it exists.

    Args:
        image_path (str): Relative path to the user's image.
    """
    if not image_path:
        return
    abs_path = os.path.abspath(os.path.join(current_app.root_path, "..", image_path))
    if os.path.exists(abs_path):
        os.remove(abs_path)
        print(f"Deleted old image: {abs_path}")

def rename_output_image(dir_path):
    """
    Rename the newly generated try-on image to a unique 7-digit name.

    Args:
        dir_path (str): Path to the directory containing output images.

    Returns:
        str: New filename in the format '0000001.jpg', '0000002.jpg', ...
    """
    files = os.listdir(dir_path)
    filenames = [f for f in files if f.endswith('.jpg') and f[:7].isdigit()]
    if not filenames:
        return "0000001.jpg"
    numbers = [int(f[:7]) for f in filenames]  # get the 7-bit digit
    next_number = max(numbers) + 1 # search the max number
    return f"{next_number:07d}.jpg" # ensure 7-bit digits
