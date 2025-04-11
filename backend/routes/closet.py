"""
Clothing Closet Management Routes
Author: Zixin Ding

This module provides API endpoints for managing all closet and user's virtual clothing closet.

Current Features:
    1. View all clothing items by category.
    2. View clothing details.
    3. Add clothing items to the closet.
    4. Display closet items by category.
    5. Remove clothing items from the closet.
    
    Version 1: Used pymysql for raw SQL operations.
    Version 2: Refactored to use SQLAlchemy ORM for cleaner database management.
"""

import json
from exts import db
from utils.caption_utils import generate_title
from utils.helpers import format_image_url
from utils.static_serve import serve_clothing_image
from flask import Blueprint, request, jsonify
from models import Clothing, Closet  # Import SQLAlchemy models

# Create a blueprint for closet-related routes
closet_bp = Blueprint("closet", __name__)  

@closet_bp.route('/data/clothes/<path:filename>')
def get_clothing_image(filename):
    """
    Serve clothing image from the /data/clothes/ directory.
    Used for displaying individual images dynamically.

    Args:
        filename (str): The relative path of the image file.

    Returns:
        Flask response: The requested image file if found; otherwise, a 404 error.
    """
    return serve_clothing_image(filename)

## API endpoint: View All Clothes
@closet_bp.route("/api/clothes", methods=["GET"])
def get_all_clothing():
    """
    Retrieve all clothing items based on category.

    Query Parameters:
        category (str): The clothing category to filter by "tops", "bottoms", "dresses" (default: "tops").

    Returns:
        JSON response containing clothing items with metadata (title, image URL, etc.).
    """
    category = request.args.get("category", "tops")  # Default category is "tops"

    try:
        # Query using SQLAlchemy
        data = Clothing.query.filter_by(category=category).all()

        if not data:
            return jsonify({"message": "No items found", "items": []}) 
     
        items = [
            {
                "id": item.cid,
                "title": generate_title(item.caption),
                "image_path": format_image_url(item.model_tryon_path),
                "closet_users": item.closet_users,
            }
            for item in data
        ] 

        return jsonify({"message": "Success", "items": items})

    except Exception as e:
        return jsonify({"error": str(e)}), 500


@closet_bp.route('/detail/<int:clothing_id>', methods=['GET'])
def get_clothing_detail(clothing_id):
    """
    Retrieve detailed information of a clothing item.

    Args:
        clothing_id (int): ID of the clothing item to retrieve.

    Returns:
        JSON: Labels, generated title, and image path of the clothing.
    """
    try:
        item = Clothing.query.get(clothing_id)

        if not item:
            return jsonify({"error": "Clothing item not found"}), 404
        
        # Handle caption field which may be stored as JSON string or dict
        if isinstance(item.caption, str):
            caption_dict = json.loads(item.caption)  # Convert string to dict
        elif isinstance(item.caption, dict):
            caption_dict = item.caption  # Already a dictionary
        else:
            caption_dict = {}  # Fallback to an empty dict if invalid

        item_data = {
            "id": item.cid,
            "labels": list(caption_dict.values()) if isinstance(caption_dict, dict) else [],
            "title": generate_title(caption_dict),
            "cloth_path": format_image_url(item.cloth_path)
        }
   
        return jsonify({"message": "Success", "item": item_data})

    except Exception as e:
        return jsonify({"error": str(e)}), 500



# Action for clicking "Add to Closet"
@closet_bp.route('/add-to-closet', methods=['POST'])
def add_to_closet():
    """
    Add a clothing item to the user's closet.

    Constraints:
    - A user can have a maximum of 5 items per category.
    - Avoid adding duplicates.

    Args:
        - user_id (int)
        - clothing_id (int)

    Returns:
        JSON response indicating success or failure.
    """
    user_id = request.json.get("user_id")  
    clothing_id = request.json.get("clothing_id")

    if not user_id or not clothing_id:
        return jsonify({"error": "Missing user_id or clothing_id"}), 400

    try:
        ## 1. Prevents duplicate additions
        # Check if item is already in the user's closet
        existing_item = Closet.query.filter_by(user_id=user_id, clothing_id=clothing_id).first()
        if existing_item:
            return jsonify({"error": "Item already in closet!"}), 400

        ## 2. Check category limit (max 5 per category)
        # Step 1: Gets category of the current clothing item
        clothing_item = Clothing.query.get(clothing_id)
        if not clothing_item:
            return jsonify({"error": "Clothing item not found"}), 400

        category = clothing_item.category  # Get clothing category（tops, bottoms, dresses）

        # Step 2: Count how many items the user has in this category
        user_items = Closet.query.join(Clothing).filter(
            Closet.user_id == user_id, Clothing.category == category
        ).count()

        if user_items >= 5:
            return jsonify({"error": f"Max 5 {category} items allowed. Remove one to add new."}), 400

        # 3. Insert new clothing item into the Closet
        new_entry = Closet(user_id=user_id, clothing_id=clothing_id)
        db.session.add(new_entry)
        
        # 4. Increase `closet_users` count in the Clothing table
        clothing_item.closet_users += 1
        db.session.commit()

        return jsonify({"message": "Item added to closet successfully!"}), 201

    except Exception as e:
        return jsonify({"error": str(e)}), 500


## View own closet
@closet_bp.route('/get-closet', methods=['GET'])
def get_closet():
    """
    Retrieve all clothing items in the user's closet, optionally filtered by category.

    Query Parameters:
        user_id (int): User ID.
        category (str): Clothing category (optional).

    Returns:
        JSON: List of clothing items in the user's closet.
    """
    user_id = request.args.get("user_id")  # Get 'user_id' from frontend request
    category = request.args.get("category", "tops")  # Default category is "tops"

    if not user_id:
        return jsonify({"error": "Missing user_id"}), 400
    
    try:
        query = Closet.query.join(Clothing).filter(Closet.user_id == user_id)

        if category:
            query = query.filter(Clothing.category == category)

        query = query.order_by(Closet.added_at.desc())
        items = query.all()

        data = [
            {
                "id": item.clothing_id,
                "category": item.clothing.category,
                "url": format_image_url(item.clothing.cloth_path)
            }
            for item in items
        ]
        return jsonify({"message": "Success", "closet": data})

    except Exception as e:
        return jsonify({"error": str(e)}), 500


@closet_bp.route('/remove-from-closet', methods=['POST'])
def remove_from_closet():
    """
    Remove a clothing item from the user's closet.

    Args:
        user_id (int): User ID.
        clothing_id (int): Clothing item ID.

    Returns:
        JSON: Success or error message.
    """
    user_id = request.json.get("user_id")
    clothing_id = request.json.get("clothing_id")

    if not user_id or not clothing_id:
        return jsonify({"error": "Invalid request"}), 400

    try:
        item = Closet.query.filter_by(user_id=user_id, clothing_id=clothing_id).first()
        if item:
            db.session.delete(item)

            # Decrement closet_users count
            clothing_item = Clothing.query.get(clothing_id)
            if clothing_item and clothing_item.closet_users > 0:
                clothing_item.closet_users -= 1

            db.session.commit()
        
        return jsonify({"message": "Item removed from closet successfully."}), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500
