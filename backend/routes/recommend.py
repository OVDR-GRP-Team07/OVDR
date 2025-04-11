# Author: Jinghao Liu, Zihan Zhou
import os
import numpy as np
import pandas as pd
from flask import Blueprint, request, jsonify, send_from_directory
from sqlalchemy.orm import sessionmaker
from sqlalchemy import func
from models import Clothing, History
from exts import db
from utils.helpers import format_image_url

recommend_bp = Blueprint("recommend", __name__)

# Set base directory for consistent file paths
BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))

# Load similarity matrix
try:
    image_embeddings = np.load(os.path.join(BASE_DIR, "image_embeddings.npy"))
    similarity_matrix = np.load(os.path.join(BASE_DIR, "similarity_matrix.npy"))
    image_names = [f"{i:06d}_top.jpg" for i in range(1, 301)] + \
                  [f"{i:06d}_bottom.jpg" for i in range(1, 301)] + \
                  [f"{i:06d}_dress.jpg" for i in range(1, 301)]
    image_similarity_df = pd.DataFrame(similarity_matrix, index=image_names, columns=image_names)
except Exception as e:
    image_similarity_df = pd.DataFrame()

# 1. Similarity-based recommendation
@recommend_bp.route('/recommend/<int:clothing_id>', methods=['GET'])
def recommend_images(clothing_id):
    """
        Recommend visually and semantically similar clothing items based on CLIP similarity.

        Path Parameters:
            clothing_id (int): The ID of the clothing item to find similar items for.

        Query Parameters:
            top_n (int, optional): Number of top similar items to return (default=3).

        Returns:
            JSON: A list of recommended clothing items with ID and image URL.
        """
    top_n = int(request.args.get("top_n", 3))
    Session = sessionmaker(bind=db.engine)
    session = Session()
    try:
        # edit by ps: debugging
        print(f"Received request for clothing_id: {clothing_id}")

        clothing = session.query(Clothing).filter(Clothing.cid == clothing_id).first()
        if not clothing:
            return jsonify({"error": "Clothing item not found"}), 404

        image_name = os.path.basename(clothing.cloth_path)
        if image_name not in image_similarity_df.index:
            return jsonify({"error": "Image not found in similarity matrix"}), 404

        similar_image_names = image_similarity_df[image_name].nlargest(top_n + 1).iloc[1:].index.tolist()

        # fix cloth_path here using same logic as stored in DB
        similar_images = [
            os.path.join(os.path.dirname(clothing.cloth_path), name).replace("\\", "/")
            for name in similar_image_names
        ]
        print(f"Resolved similar image full paths: {similar_images}")

        recommended_items = session.query(Clothing).filter(Clothing.cloth_path.in_(similar_images)).all()
        print(f"Recommended clothing items: {[item.cid for item in recommended_items]}")

        # edit by peinishe: add clothing img url for frontend display
        return jsonify({
            # "recommended_clothing_ids": [item.cid for item in recommended_items]
            "recommendations": [
                {"id": item.cid, "url": format_image_url(item.cloth_path)}
                for item in recommended_items
            ]
        }), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500
    finally:
        session.close()

# 2. Popularity-based recommendation
@recommend_bp.route('/recommend/popular', methods=['GET'])
def recommend_popular():
    """
        Recommend the most popular clothing items based on interaction frequency.

        Query Parameters:
            top_n (int, optional): Number of most popular items to return (default=5).

        Returns:
            JSON: A list of popular clothing items with ID, category, and image URL.
        """
    top_n = int(request.args.get("top_n", 5))
    Session = sessionmaker(bind=db.engine)
    session = Session()
    try:
        results = (
            session.query(History.clothing_id, func.count(History.clothing_id).label("clicks"))
            .group_by(History.clothing_id)
            .order_by(func.count(History.clothing_id).desc())
            .limit(top_n)
            .all()
        )
        clothing_ids = [r.clothing_id for r in results]
        popular_items = session.query(Clothing).filter(Clothing.cid.in_(clothing_ids)).all()
        clothing_dict = {item.cid: item for item in popular_items}
        ordered_items = [clothing_dict[cid] for cid in clothing_ids if cid in clothing_dict]
        return jsonify({
            "recommended_popular": [
                {
                    "id": item.cid,
                    "category": item.category,
                    "url": format_image_url(item.cloth_path)
                } for item in ordered_items
            ]
        }), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500
    finally:
        session.close()

# 3. User-based collaborative filtering
@recommend_bp.route('/recommend/user/<int:user_id>', methods=['GET'])
def recommend_by_user(user_id):
    """
        Recommend clothing items to a user based on similar users' preferences (collaborative filtering).

        Path Parameters:
            user_id (int): The ID of the current user.

        Query Parameters:
            top_n (int, optional): Number of recommended items to return (default=5).

        Returns:
            JSON: A list of personalized recommendations including ID, category, and image URL.
        """
    top_n = int(request.args.get("top_n", 5))
    Session = sessionmaker(bind=db.engine)
    session = Session()
    try:
        user_history = session.query(History.clothing_id).filter(History.user_id == user_id).all()
        user_clicked_ids = [row.clothing_id for row in user_history]
        if not user_clicked_ids:
            return jsonify({"error": "No history found for this user."}), 404
        similar_users = (
            session.query(History.user_id)
            .filter(History.clothing_id.in_(user_clicked_ids), History.user_id != user_id)
            .distinct()
            .all()
        )
        similar_user_ids = [u.user_id for u in similar_users]
        if not similar_user_ids:
            return jsonify({"message": "No similar users found."}), 200
        candidate_items = (
            session.query(History.clothing_id, func.count().label("popularity"))
            .filter(History.user_id.in_(similar_user_ids), ~History.clothing_id.in_(user_clicked_ids))
            .group_by(History.clothing_id)
            .order_by(func.count().desc())
            .limit(top_n)
            .all()
        )
        candidate_ids = [c.clothing_id for c in candidate_items]
        recommended_items = session.query(Clothing).filter(Clothing.cid.in_(candidate_ids)).all()
        return jsonify({
            "personalized_recommendations": [
                {
                    "id": item.cid,
                    "category": item.category,
                    "url": format_image_url(item.cloth_path)
                } for item in recommended_items
            ]
        }), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500
    finally:
        session.close()

@recommend_bp.route('/data/clothes/<path:filename>')
def serve_clothes_image(filename):
    """
        Serve clothing images from the local file system for frontend rendering.

        Path Parameters:
            filename (str): The relative path to the image file under /data/clothes/.

        Returns:
            File: The image file to be displayed in the frontend.
        """
    base_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '../..'))
    clothes_dir = os.path.join(base_dir, 'data/clothes')
    return send_from_directory(clothes_dir, filename)
