"""
Static Route Registration Utility
Author: Zixin Ding

This module registers static image/file serving routes and provides
functions to serve clothing and user-uploaded images.
"""

import os
from flask import send_from_directory, jsonify

# Base directory definitions
BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "../../"))  # Return to the project root directory
BASE_DATA_DIR = os.path.join(BASE_DIR, 'data')
CLOTHES_DIR = os.path.join(BASE_DATA_DIR, "clothes")  # absolute path
USER_DIR = os.path.join(BASE_DATA_DIR, "users")  # absolute path

def register_static_routes(app):
    """
    Register static routes for serving image and file assets from the /data folder.
    Includes:
        - /data/<filename>: For accessing user uploads, clothing, try-on images, etc.
        - / : Health check root route.
    """
    @app.route('/data/<path:filename>')
    def serve_data(filename):
        """
        Serve static file given a relative path from /data/
        Example: /data/users/image/1.jpg
        """
        full_path = os.path.join(BASE_DATA_DIR, filename)
        print(f"Serving file from: {full_path}")

        if not os.path.exists(full_path):
            print("File not found:", full_path)
            os.abort(404)

        return send_from_directory(BASE_DATA_DIR, filename)

    @app.route('/')
    def index():
        """
        Root route for health checking or pinging the backend.
        """
        return "Flask Backend Running"



def serve_clothing_image(filename):
    """
    Serve clothing images stored in the 'data/clothes/' directory.

    Args:
        filename (str): Relative path of the image file.

    Returns:
        Flask response: Returns the image file if found, else a 404 error.

    TODO:
    -  (Add pagination support)
    -  (Allow filtering by multiple categories)
    """

    # Make sure filename contains only 'tops/model-tryon/000001_top.jpg' format
    filename = filename.replace("data/clothes/", "").lstrip("/")

    # Calculate file integrity path
    file_path = os.path.normpath(os.path.join(CLOTHES_DIR, filename))  

    # Determine whether the file exists
    if not os.path.exists(file_path):
        return jsonify({"error": f"File not found: {file_path}"}), 404  
    
    return send_from_directory(CLOTHES_DIR, filename)

def serve_user_image(filename):
    """
    Serve user images stored in the 'data/users/' directory.

    Args:
        filename (str): Relative path of the image file.

    Returns:
        Flask response: Returns the image file if found, else a 404 error.
    """

    # Make sure filename contains only 'tops/model-tryon/000001_top.jpg' format
    # filename = filename.replace("data/clothes/", "").lstrip("/")

    # Calculate file integrity path
    file_path = os.path.normpath(os.path.join(USER_DIR, filename))  

    # Determine whether the file exists
    if not os.path.exists(file_path):
        return jsonify({"error": f"File not found: {file_path}"}), 404  
    
    return send_from_directory(USER_DIR, filename)