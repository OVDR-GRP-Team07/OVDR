# Author:Jinghao Liu, Zihan Zhou
# Description: This Flask app provides a text-based image retrieval API using a pretrained CLIP model and precomputed image embeddings.
#              The API allows searching clothing items by natural language queries.

from flask import Flask, request, jsonify, abort
from flask_cors import CORS
import numpy as np
import torch
from transformers import CLIPProcessor, CLIPModel
import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from models import Clothing  # Import Clothing model

app = Flask(__name__)
CORS(app)  # Allow cross-origin requests for frontend integration

# Use environment variables to store database credentials to prevent exposure
DATABASE_URL = os.getenv("DATABASE_URL", "mysql+mysqlconnector://ovdr_developer:123456@172.19.108.9/OVDR")
engine = create_engine(DATABASE_URL)
Session = sessionmaker(bind=engine)

# Preload embeddings and similarity matrix
try:
    image_embeddings = np.load("image_embeddings.npy")  # Shape: (900, 768)
    similarity_matrix = np.load("similarity_matrix.npy")  # Shape: (900, 900)
except Exception as e:
    print(f"Error loading embeddings: {str(e)}")
    image_embeddings, similarity_matrix = None, None

# Load CLIP model
local_path = "../models/clip-vit-large-patch14"
device = "cuda" if torch.cuda.is_available() else "cpu"

try:
    model = CLIPModel.from_pretrained(local_path).to(device)
    processor = CLIPProcessor.from_pretrained(local_path)
except Exception as e:
    print(f"Error loading CLIP model: {str(e)}")
    model, processor = None, None

# Cache for storing text query results
text_cache = {}

# Compute text embeddings
def text_embedding(text):
    """
    Compute the text embedding of a query using CLIP.

    Args:
        text (str): The input natural language query.

    Returns:
        np.ndarray: The 768-dimensional vector.
    """
    if text in text_cache:
        return text_cache[text]

    if not model or not processor:
        raise RuntimeError("CLIP model not loaded.")

    inputs = processor(text=[text], return_tensors="pt", padding=True).to(device)
    with torch.no_grad():
        embedding = model.get_text_features(**inputs)

    text_cache[text] = embedding.cpu().numpy()
    return text_cache[text]

# Compute similarity between text query and image embeddings
def calculate_similarity(query):
    """
    Compute cosine similarity between the query embedding and image embeddings.

    Args:
        query (str): Natural language description.

    Returns:
        np.ndarray: Similarity scores to all images.
    """
    if not query:
        raise ValueError("Query parameter is required.")

    query_embedding = text_embedding(query).squeeze()

    # Avoid division by zero
    image_norms = np.linalg.norm(image_embeddings, axis=1)
    query_norm = np.linalg.norm(query_embedding)
    denom = image_norms * query_norm
    denom[denom == 0] = 1e-6  # Prevent NaN values

    similarity_scores = np.dot(image_embeddings, query_embedding) / denom
    return similarity_scores

# Search API
@app.route('/search', methods=['GET'])
def search():
    """
    Search API endpoint that returns top N matching clothing images based on a text query.
    """
    query = request.args.get('query')
    top_n = int(request.args.get('top_n', 20))

    if not query:
        return jsonify({"error": "Query parameter is required"}), 400

    try:
        similarity_scores = calculate_similarity(query)
        top_indices = similarity_scores.argsort()[-top_n:][::-1]  # Get top N similar images
    except Exception as e:
        return abort(500, description=f"Error processing query: {str(e)}")

    # Retrieve clothing information from the database
    session = Session()
    result_images = []
    try:
        for idx in top_indices:
            clothing = session.query(Clothing).filter(Clothing.cid == idx + 1).first()  # Database IDs start from 1
            if clothing:
                result_images.append({
                    'clothing_id': clothing.cid,
                    'category': clothing.category,
                    'image_path': clothing.cloth_path
                })
    except Exception as e:
        return abort(500, description=f"Database query error: {str(e)}")
    finally:
        session.close()  # Ensure database connection is closed

    return jsonify({"matched_images": result_images})

if __name__ == '__main__':
    app.run(debug=True)
