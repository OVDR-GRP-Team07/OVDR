"""
Browsing History Management Routes
Author: Zixin Ding

This module provides RESTful API endpoints for managing user browsing history in the virtual try-on system.

Features:
    - Add a clothing item to browsing history.
    - Maintain only the latest 20 records per user.
    - Retrieve history with clothing details (title, image, timestamp, etc.).
"""

import json
from exts import db
from models import History, Clothing
from flask import Blueprint, request, jsonify
from utils.caption_utils import generate_title
from utils.helpers import format_image_url
from sqlalchemy import desc

# Create a blueprint for history-related operations
history_bp = Blueprint("history", __name__)

@history_bp.route("/add-history", methods=["POST"])
def add_history():
    """
    Add a record to the user's browsing history.
    
    Rules:
        - Removes any duplicate history (same clothing_id for the same user).
        - Only retains the latest 20 records per user (oldest will be deleted).

    Args (JSON):
        - user_id (int): ID of the user.
        - clothing_id (int): ID of the clothing being viewed.

    Returns:
        JSON: Success message or error.
    """
    if not request.is_json:
        return jsonify({"error": "Invalid request: Expected JSON"}), 400
    
    user_id = request.json.get("user_id")
    clothing_id = request.json.get("clothing_id")

    if not user_id or not clothing_id:
        return jsonify({"error": "Missing user_id or clothing_id"}), 400

    try:
        # Step 1: Remove any duplicate record for this (user_id, clothing_id) if exists
        History.query.filter_by(user_id=user_id, clothing_id=clothing_id).delete()

        # Step 2: Insert new history record with the latest timestamp
        new_history = History(user_id=user_id, clothing_id=clothing_id)
        db.session.add(new_history)
        db.session.commit()

        # Step 3: Keep only the latest 20 records per user
        history_to_delete = (
            History.query.filter_by(user_id=user_id)
            .order_by(desc(History.created_at))
            .offset(20)
            .all()
        )
        for record in history_to_delete:
            db.session.delete(record)

        db.session.commit()
        return jsonify({"message": "History recorded successfully."}), 201

    except Exception as e:
        db.session.rollback()
        print("Error in add_history:", e)
        return jsonify({"error": str(e)}), 500

@history_bp.route("/get-history", methods=["GET"])
def get_history():
    """
    Retrieve the latest 20 clothing items from a user's browsing history.

    Query Parameters:
        - user_id (int): ID of the user.

    Returns:
        JSON:
            - List of clothing items with metadata including:
                - id, image URL, title, created_at, closet_users, category
    """
    user_id = request.args.get("user_id")

    if not user_id:
        return jsonify({"error": "Missing user_id"}), 400

    try:
        # Join History with Clothing table and retrieve 20 most recent records
        history_records = (
            db.session.query(History)
            .join(Clothing, History.clothing_id == Clothing.cid)
            .filter(History.user_id == user_id)
            .order_by(desc(History.created_at))
            .limit(20)
            .all()
        )

        if not history_records:
            return jsonify({"message": "No items found", "items": []})

        # Process records and format response
        history_list = []
        for record in history_records:
            caption_dict = record.clothing.caption
            if isinstance(caption_dict, str):  # Ensure proper parsing
                caption_dict = json.loads(caption_dict)
            elif not isinstance(caption_dict, dict):
                caption_dict = {}

            history_list.append(
                {
                    "id": record.clothing_id,
                    "image": format_image_url(record.clothing.cloth_path),
                    "title": generate_title(caption_dict),
                    "created_at": record.created_at.strftime("%Y-%m-%d %H:%M:%S"),
                    "closet_users": record.clothing.closet_users,
                    "category": record.clothing.category,
                }
            )

        return jsonify({"message": "Success", "history": history_list})

    except Exception as e:
        return jsonify({"error": str(e), "history": []}), 500