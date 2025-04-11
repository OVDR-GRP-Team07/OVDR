###############################################
# Module: process.py
# Author: Zhihao Cao
# Maintainer: Zixin Ding, Zhihao Cao
# Description:
#   This module handles the virtual try-on process.
#   It includes endpoints for:
#     - Serving static clothing images
#     - Processing user image + clothing to generate try-on result
#     - (Optionally) transitioning to using Clothing DB instead of cloth_url
#
# Usage:
#   POST /process_image with {user_id, cloth_url, item_category}
#   Returns the path to generated try-on image
#
# Dependencies:
#   - StableVITON (external model)
#   - User image managed under data/users/image/
#   - Output image saved to data/combinations/user_<user_id>/
###############################################

# genereate image after costume change from the origin image and closet 
# authored by Zhihao Cao
# modified by Zixin Ding
import sys
from flask import Blueprint, request, jsonify, current_app
import os
import time
import shutil
from backend.utils.static_serve import serve_user_image
from exts import db
from models import User, Clothing, Closet
from pathlib import Path
from utils.download_utils import download_cloth_image
from utils.image_utils import delete_user_image_if_exists, get_user_image_path, save_user_image, rename_output_image
from utils.stableviton_runner import run_stableviton

# Define the path to the StableVITON model directory
stableviton_path = Path(__file__).resolve().parent.parent / "models" / "StableVITON"

# Create a blueprint for the process route
process_bp = Blueprint("process", __name__)  

# Register a static route to serve clothing images from local disk
sys.path.insert(0,str(stableviton_path))
@process_bp.route('/data/clothes/<path:filename>')
def get_user_image(filename):
    """
    API endpoint to serve clothing images.

    Args:
        filename (str): The relative path of the image file.

    Returns:
        Flask response: The requested image file if found; otherwise, a 404 error.
    """
    return serve_user_image(filename)




@process_bp.route("/process_image", methods=["GET","POST"])
def process_image():
    """
    Main entry point for generating virtual try-on results.
    Combines a user image with a selected clothing image (from DB or URL)
    and returns the resulting image path.
    """
        
    # Retrieve the POSTed JSON data
    data = request.get_json()
    if not data:
        return jsonify({"error": "No data provided"}), 400

    # Extract basic fields 
    item_id = data.get("item_id")
    user_id = data.get("user_id")
    cloth_url = data.get("cloth_url")
    item_category = data.get("item_category")
    
    # Lookup user and image path
    user = User.query.get(user_id)
    if not user or not user.image_path:
        return jsonify({"error": "User image not found"}), 404

    # Load the full path to the user's image
    image_url = get_user_image_path(user)
    if not os.path.exists(image_url):
        return jsonify({"error": "Image file not found on disk"}), 404

    print(f"Using image for processing: {image_url}")
    

    # Prepare directory to save downloaded clothing
    closet = Closet.query.get(item_id)
    if closet:
        cloth = Clothing.query.get(closet.clothing_id)
        if cloth:
            cloth_url = cloth.cloth_path
            print(f"clothing from closet: {cloth_url}")
    
    input_cloth_path = "./store_data/input_clothes/"+str(user_id)
    os.makedirs(input_cloth_path, exist_ok=True) #create the input directory
    cloth_name = str(user_id)+str(time.time())+".jpg"
    save_path = os.path.join(input_cloth_path, cloth_name)
    download_cloth_image(cloth_url, save_path)
    
    # Download clothing image from Clothing DB query
    cloth_url = f"./store_data/input_clothes/{str(user_id)}/{cloth_name}"
    print(f"Cloth path saved to: {cloth_url}")


    # Call StableVITON model for try-on generation
    try:
        run_stableviton(image_url, cloth_url, item_category)
    except RuntimeError as e:
        return jsonify({"error": str(e)}), 500

    # Prepare output image
    gene_image_path = stableviton_path / "output_images"
    output_dir = f"./data/combinations/user_{user_id}"
    os.makedirs(output_dir, exist_ok=True)
    
    print(f"Gene image path: {gene_image_path}")
    print(f"Output directory: {output_dir}")
    
    files = [f for f in os.listdir(gene_image_path) if f.endswith('.jpg')]
    if not files:
        return jsonify({"error": "No image found"}), 500

    new_name = rename_output_image(gene_image_path)
    last = sorted(files)[-1]
    shutil.copy(os.path.join(gene_image_path, last), os.path.join(output_dir, new_name))

    # #TODO: add the top_id/bottom_id/dress_id to the database---> in future work
    # new_combination = Combination(
    #     user_id = user_id,
    #     outfit_path = "../data/combinations/user_"+str(user_id)+"/"+new_name,
    # )
    # db.session.add(new_combination)
    # db.session.commit()

    # Compose final output path
    relative_output_path = f"./data/combinations/user_{user_id}/{new_name}"
    print(f"Final output path: {relative_output_path}")

    return jsonify({
        "message": "success",
        "image_path": new_name,
    })




