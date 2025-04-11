## Module: combinations.py
## Author: Peini She
## Modified by: Zixin Ding (logic enhancement, bug fixing), Zhihao Cao
## Description:
##   This module manages storage and retrieval of outfit combinations generated
##   by the virtual try-on system (StableVITON). It also supports deletion and static file serving.
##
##   Features include:
##     - Saving new outfit combinations (top/bottom/dress + try-on image)
##         - Prevents storing duplicate combinations per user
##     - Retrieving all combinations saved by a user
##     - Deleting existing combinations by ID
##     - Serving local try-on result images to frontend

import os
from flask import send_from_directory
from flask import Blueprint, request, jsonify
from exts import db
from models import Combination
from urllib.parse import unquote
combinations_bp = Blueprint("combinations", __name__)

@combinations_bp.route('/save-combination', methods=['POST'])
def save_combination():
    """
    Save a new try-on outfit combination to the database.

    Prevents saving duplicate combinations with the same clothing IDs for the same user.

    Request JSON:
        - user_id (int): ID of the user
        - top_id (int): ID of the top clothing item (optional)
        - bottom_id (int): ID of the bottom clothing item (optional)
        - dress_id (int): ID of the dress item (optional)
        - resultImage (str): Path to the generated outfit image (required)

    Returns:
        JSON: Success or error message
    """
    data = request.get_json()
    user_id = data.get("user_id")
    top_id = data.get("top_id")
    bottom_id = data.get("bottom_id")
    dress_id = data.get("dress_id")
    result_image = data.get("resultImage")
   
    if not user_id or not result_image:
        return jsonify({"error": "Missing user_id or resultImage"}), 400

    try:
        # Ding: Check if the combination already exists for this user
        existing = Combination.query.filter_by(
            user_id=user_id,
            top_id=top_id,
            bottom_id=bottom_id,
            dress_id=dress_id
        ).first()

        if existing:
            return jsonify({"message": "This combination already exists."}), 200
        
        new_combination = Combination(
            user_id=user_id,
            top_id=top_id,
            bottom_id=bottom_id,
            dress_id=dress_id,
            outfit_path=result_image,
        )
        db.session.add(new_combination)
        db.session.commit()

        return jsonify({"message": "Combination saved!"}), 201

    except Exception as e:
        return jsonify({"error": str(e)}), 500
    
@combinations_bp.route('/get-combinations', methods=['GET'])
def get_combinations():
    """
    Retrieve all saved combinations for a specific user.

    Query Parameters:
        - user_id (int): ID of the user

    Returns:
        JSON: List of saved combinations including top/bottom/dress IDs and image paths
    """
    user_id = request.args.get("user_id")

    if not user_id:
        return jsonify({"error": "Missing user_id"}), 400

    try:
        combinations = Combination.query.filter_by(user_id=user_id).all()

        result = [
            {
                "id": c.id,
                "top_id": c.top_id,
                "bottom_id": c.bottom_id,
                "dress_id": c.dress_id,
                "url": c.outfit_path
            }
            for c in combinations
        ]

        return jsonify({"message": "Success", "combinations": result}), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500
    
## Ding
@combinations_bp.route('/delete-combination', methods=['DELETE'])
def delete_combination():
    """
    Delete a saved outfit combination.

    Request JSON:
        - id (int): ID of the combination to delete

    Returns:
        JSON: Success or error message
    """
    data = request.get_json()
    combination_id = data.get("id")

    if not combination_id:
        return jsonify({"error": "Missing combination ID"}), 400

    try:
        combination = Combination.query.get(combination_id)
        if not combination:
            return jsonify({"error": "Combination not found"}), 404

        db.session.delete(combination)
        db.session.commit()
        return jsonify({"message": "Combination deleted successfully."}), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500

    
@combinations_bp.route('/show_image/<userid>/<path:filename>')
def serve_combination_image(userid, filename):
    """
    Serve the generated try-on result image from the local directory.

    Args:
        userid (int): User ID used in the directory structure
        filename (str): Filename of the image (may include URL-encoded chars)

    Returns:
        Flask Response: The requested image if it exists
    """    
    #The file name contains special characters that need to be converted to URL encoding.
    filename = unquote(filename)
        
    # Construct the full directory path    
    base_dir = os.path.abspath("./data/combinations")
    user_dir = os.path.join(base_dir, f"user_{userid}")    
        
    return send_from_directory(user_dir, filename)
