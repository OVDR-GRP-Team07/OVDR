# Author:Jinghao Liu, Zihan Zhou
import numpy as np
import torch
from transformers import CLIPProcessor, CLIPModel
import os

# Load the precomputed embeddings and similarity matrix
image_embeddings = np.load("image_embeddings.npy")  # Shape: (900, 768)
similarity_matrix = np.load("similarity_matrix.npy")  # Shape: (900, 900)

# Define the image folder path
base_path = os.path.join("..", "data", "clothes")
image_folders = {
    "bottoms": os.path.join(base_path, "bottoms", "cloth"),
    "dresses": os.path.join(base_path, "dresses", "cloth"),
    "tops": os.path.join(base_path, "tops", "cloth"),
}

# Load the CLIP model and processor (only if needed for text queries)
local_path = "./clip-vit-large-patch14"
model = CLIPModel.from_pretrained(local_path).to("cuda" if torch.cuda.is_available() else "cpu")
processor = CLIPProcessor.from_pretrained(local_path)

# Cache for text query results to avoid redundant computations
text_cache = {}

# Precompute the mapping from index to image path, ensuring correct file numbering (1-300)
image_paths = []
for idx in range(900):
    idx_str = f"{(idx % 300) + 1:06d}"  # 6-digit format, ensuring range from 000001 to 000300
    if idx < 300:
        image_paths.append(os.path.join(image_folders["bottoms"], f"{idx_str}_bottom.jpg"))
    elif idx < 600:
        image_paths.append(os.path.join(image_folders["tops"], f"{idx_str}_top.jpg"))
    else:
        image_paths.append(os.path.join(image_folders["dresses"], f"{idx_str}_dress.jpg"))

# Compute and cache text embeddings
def text_embedding(text):
    if text in text_cache:
        return text_cache[text]

    inputs = processor(text=[text], return_tensors="pt", padding=True).to(model.device)
    with torch.no_grad():
        embedding = model.get_text_features(**inputs)

    text_cache[text] = embedding.cpu().numpy()
    return text_cache[text]

# Compute similarity between text query and all images
def calculate_similarity(query, query_type="text"):
    if query_type == "text":
        query_embedding = text_embedding(query).squeeze()  # Shape: (768,)
    else:
        raise ValueError("query_type currently supports only 'text'. Implement `get_image_embedding` for image queries.")

    # Compute similarity scores
    similarities = np.dot(image_embeddings, query_embedding)  # Shape: (900,)

    # Compute dynamic threshold (top 3% most similar results)
    threshold = np.percentile(similarities, 97)

    # Filter indices that meet the threshold and sort by similarity in descending order
    filtered_indices = np.where(similarities >= threshold)[0]
    filtered_results = sorted([(idx, similarities[idx]) for idx in filtered_indices], key=lambda x: x[1], reverse=True)

    return {
        "similarities": filtered_results,
        "best_match": filtered_results[0][0] if filtered_results else None,
        "best_similarity_score": filtered_results[0][1] if filtered_results else None,
        "threshold_used": threshold
    }

# Example query
query = "I want a red t-shirt."
query_type = "text"

# Compute similar images
similarity_result = calculate_similarity(query, query_type)

# Output matched results
print("Query:", query)
print(f"Dynamic Threshold: {similarity_result['threshold_used']:.4f}")
print("Matched images:")
for idx, score in similarity_result["similarities"]:
    print(f" Image: {image_paths[idx]}, Similarity: {score:.4f}")
