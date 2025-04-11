"""
User Image Upload and Retrieval Routes
Author: Zixin Ding

This module provides RESTful APIs for uploading user full-body photos and retrieving user information.
It also serves static user image files from the /data/users/image directory.
"""

# routes/user_image.py
from flask import Blueprint, request, jsonify
from exts import db
from models import User
from utils.image_utils import save_user_image, get_user_image_path, delete_user_image_if_exists
from backend.utils.static_serve import serve_user_image

# Blueprint for user image-related endpoints
user_image_bp = Blueprint("user_image", __name__)

@user_image_bp.route('/upload_image', methods=['POST'])
def upload_image():
    """
    Upload a new user image and update the path in the database.

    Form Data:
        - user_id (int): ID of the user.
        - file (image): Uploaded image file.

    Returns:
        JSON: Success message and saved image path.
    """
    user_id = request.form.get("user_id")
    if not user_id:
        return jsonify({"error": "Missing user_id"}), 400    
    if 'file' not in request.files:
        return jsonify({"error": "No file part"}), 400
    
    file = request.files['file']
    if not file:
        return jsonify({"error": "Empty file"}), 400
    
    user = User.query.get(user_id)
    if not user:
        return jsonify({"error": "User not found"}), 404

    # Delete old image before saving new one
    delete_user_image_if_exists(user.image_path)

    # Save new image to disk
    filepath, relative_path = save_user_image(file, user_id)
    print(f"Saving file to: {filepath}")

    # Update user image path in DB
    user.image_path = relative_path
    db.session.commit()

    return jsonify({
        "message": "Image uploaded and path updated successfully",
        "image_path": relative_path
    })


@user_image_bp.route('/get_user_info', methods=['GET'])
def get_user_info():
    """
    Get user profile information including image path.

    Query Parameters:
        - user_id (int): ID of the user.

    Returns:
        JSON: user_id, username, image_path
    """
    user_id = request.args.get('user_id')
    if not user_id:
        return jsonify({"error": "Missing user_id"}), 400

    user = User.query.get(user_id)
    if not user:
        return jsonify({"error": "User not found"}), 404
    
    print(user.image_path)

    return jsonify({
        "user_id": user.user_id,
        "username": user.username,
        "image_path": user.image_path
    })

@user_image_bp.route('/data/users/<path:filename>')
def serve_uploaded_user_image(filename):
    return serve_user_image(filename)
