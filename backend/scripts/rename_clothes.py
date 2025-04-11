"""
Batch Image Renaming Utility for OVDR Dataset
Author: Zixin Ding

This script renames all clothing-related images in the OVDR project.
It processes the folders: cloth/, cloth-mask/, and model-tryon/
under each clothing category (tops, bottoms, dresses), 
renaming the files to a unified format: 000001_top.jpg, etc.

Usage:
    Just run this script. It will rename all files under ../data/clothes/
"""
import os

def get_category(folder_path):
    """
    Determine the clothing category based on the folder path(top, bottom, dress)

    Args:
        folder_path (str): Full path to category folder.

    Returns:
        str: 'top', 'bottom', or 'dress'; None if not recognized.
    """
    if "tops" in folder_path:
        return "top"
    elif "bottoms" in folder_path:
        return "bottom"
    elif "dresses" in folder_path:
        return "dress"
    return None  # No matching category


def rename_images_in_folder(base_folder):
    """
    Batch rename all images inside cloth/, cloth-mask/, and model-tryon/ folders.

    Args:
        base_folder (str): Absolute path to category folder (e.g. tops/, bottoms/)
    """
    category = get_category(base_folder)  # Get category name
    if category is None:
        print(f"Unknown category: {base_folder}, Skip the rename step")
        return
    
    # Traverse sub-folder: cloth, cloth-mask, model-tryon
    for subfolder in ["cloth", "cloth-mask", "model-tryon"]:
        folder_path = os.path.join(base_folder, subfolder)

        if not os.path.exists(folder_path):
            print(f" The folder {folder_path} does not exist, skip")
            continue

        # Get all image
        files = sorted([f for f in os.listdir(folder_path) if f.lower().endswith(('.jpg', '.png', '.jpeg'))])

        # Rename image
        for idx, file in enumerate(files, start=1):  # idx starts at 1 and loops +1 each time
            ext = os.path.splitext(file)[1]  # Get ext (.jpg / .png)
            new_name = f"{idx:06d}_{category}{ext}"  # Format the new image name, e.g., 000001_top.jpg
            old_path = os.path.join(folder_path, file)
            new_path = os.path.join(folder_path, new_name)
            
            os.rename(old_path, new_path)
            print(f"Successfully renamed: {file} → {new_name}")

    print(f"Process is complete: {base_folder}")

# Set base data directory (relative to this script)
base_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "../data/clothes/"))

# Loop through each clothing category and rename
for category_folder in ["tops", "bottoms", "dresses"]:
    rename_images_in_folder(os.path.join(base_dir, category_folder))

print("Batch renaming completed!")