# Author: Jinghao Liu, Zihan Zhou
# revised by Zhihao Cao
# Description: This module provides a search API using CLIP embeddings for text-based clothing retrieval.

import os
import numpy as np
import torch
from flask import Blueprint, request, jsonify, abort
from sqlalchemy.orm import sessionmaker
from transformers import CLIPProcessor, CLIPModel
from backend.utils.helpers import format_image_url
from backend.utils.caption_utils import generate_title
from backend.utils.static_serve import serve_clothing_image
from models import Clothing
from exts import db

# Register Blueprint
search_bp = Blueprint("search", __name__)

# Set base directory for consistent file paths
BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
# Load precomputed embeddings and similarity matrix
try:
    image_embeddings = np.load(os.path.join(BASE_DIR, "image_embeddings.npy"))
    similarity_matrix = np.load(os.path.join(BASE_DIR, "similarity_matrix.npy"))
except Exception as e:
    print(f"[SearchBP] Error loading embeddings: {str(e)}")
    image_embeddings, similarity_matrix = None, None

# Load CLIP model
local_model_path = os.path.join(BASE_DIR, "models", "clip-vit-large-patch14")
# Convert Windows paths to forward slashes (crucial for Hugging Face)
local_model_path = os.path.normpath(local_model_path).replace("\\", "/")


device = "cuda" if torch.cuda.is_available() else "cpu"
try:
    # Force local rather than remote calls, local_files_only=True
    model = CLIPModel.from_pretrained(local_model_path,local_files_only=True).to(device)
    processor = CLIPProcessor.from_pretrained(local_model_path,local_files_only=True)
    
except Exception as e:
    print(f"[SearchBP] Error loading CLIP model: {str(e)}")
    model, processor = None, None

text_cache = {}

def text_embedding(text):
    if text in text_cache:
        return text_cache[text]
    if not model or not processor:
        raise RuntimeError("CLIP model is not loaded.")
    inputs = processor(text=[text], return_tensors="pt", padding=True).to(device)
    with torch.no_grad():
        embedding = model.get_text_features(**inputs)
    text_cache[text] = embedding.cpu().numpy()
    return text_cache[text]

def calculate_similarity(query):
    query_embedding = text_embedding(query).squeeze()
    image_norms = np.linalg.norm(image_embeddings, axis=1)
    query_norm = np.linalg.norm(query_embedding)
    denom = image_norms * query_norm
    denom[denom == 0] = 1e-6  # Prevent division by zero
    similarity_scores = np.dot(image_embeddings, query_embedding) / denom
    return similarity_scores


@search_bp.route('/data/clothes/<path:filename>')
def get_clothing_image(filename):
    """
    API endpoint to serve clothing images.

    Args:
        filename (str): The relative path of the image file.

    Returns:
        Flask response: The requested image file if found; otherwise, a 404 error.
    """
    return serve_clothing_image(filename)

# fixed by Zixin 
@search_bp.route('/search', methods=['GET'])
def search():
    """
    Search clothing items based on text query using CLIP embeddings.
    
    Query Parameters:
        query (str): Required search query text
        top_n (int): Number of results to return (default: 20)
    
    Returns:
        JSON: A list of matched clothing items with metadata

    Errors:
        400: If the query is missing.
        500: If there is an error in similarity computation or database query.

    """

    query = request.args.get('query')
    top_n = int(request.args.get('top_n', 20))

    if not query:
        return jsonify({"error": "Query parameter is required"}), 400

    try:
        similarity_scores = calculate_similarity(query)
        top_indices = similarity_scores.argsort()[-top_n:][::-1]
    except Exception as e:
        return abort(500, description=f"Error processing query: {str(e)}")

    Session = sessionmaker(bind=db.engine)
    session = Session()

    try:
        # Get matched items from database
        items = []
        for idx in top_indices:
            clothing = session.query(Clothing).filter(Clothing.cid == idx + 1).first()
            if clothing:
                items.append({
                    "id": clothing.cid,
                    "title": generate_title(clothing.caption),
                    "category": clothing.category,
                    "image_path": format_image_url(clothing.cloth_path),
                    "closet_users": clothing.closet_users
                })
        if not items:
            return jsonify({"message": "No matching items found", "items": []})
    finally:
        session.close()

    return jsonify({"items": items})

