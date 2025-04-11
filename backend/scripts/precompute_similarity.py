# Author:Jinghao Liu, Zihan Zhou

import os
import numpy as np
import torch
from transformers import CLIPProcessor, CLIPModel
from PIL import Image
from concurrent.futures import ThreadPoolExecutor

# Setup Device
device = torch.device("cuda" if torch.cuda.is_available() else "cpu")

# Loading CLIP model
local_path = "../models/clip-vit-large-patch14"
model = CLIPModel.from_pretrained(local_path).to(device)
processor = CLIPProcessor.from_pretrained(local_path)

# Picture storage path
base_path = os.path.join("..", "data", "clothes")
image_folders = {
    "bottoms": os.path.join(base_path, "bottoms", "cloth"),
    "dresses": os.path.join(base_path, "dresses", "cloth"),
    "tops": os.path.join(base_path, "tops", "cloth"),
}

# Get all picture paths
def get_all_image_paths():
    image_paths = []

    # Process bottoms
    bottoms_folder = image_folders["bottoms"]
    bottoms_files = set(os.listdir(bottoms_folder))  # List all files in bottoms folder
    for i in range(1, 301):
        filename = f"{i:06d}_bottom.jpg"
        if filename in bottoms_files:
            full_path = os.path.join(bottoms_folder, filename)
            image_paths.append(full_path)

    # Process tops
    tops_folder = image_folders["tops"]
    tops_files = set(os.listdir(tops_folder))  # List all files in tops folder
    for i in range(1, 301):
        filename = f"{i:06d}_top.jpg"
        if filename in tops_files:
            full_path = os.path.join(tops_folder, filename)
            image_paths.append(full_path)

    # Process dresses
    dresses_folder = image_folders["dresses"]
    dresses_files = set(os.listdir(dresses_folder))  # List all files in dresses folder
    for i in range(1, 301):
        filename = f"{i:06d}_dress.jpg"
        if filename in dresses_files:
            full_path = os.path.join(dresses_folder, filename)
            image_paths.append(full_path)

    return image_paths


# Calculate image embedding
def get_image_embedding(image_path):
    try:
        image = Image.open(image_path).convert("RGB")
        inputs = processor(images=image, return_tensors="pt").to(device)
        with torch.no_grad():
            embedding = model.get_image_features(**inputs)

        embedding_np = embedding.cpu().numpy().squeeze()
        if embedding_np.shape != (768,):  # Make sure the shape is correct
            raise ValueError(f"Unexpected embedding shape: {embedding_np.shape}")

        return embedding_np
    except Exception as e:
        print(f"Error loading image: {image_path}, Error: {e}")
        return None


# Calculate and store the similarity matrix
def precompute_similarity():
    image_paths = get_all_image_paths()
    num_images = len(image_paths)

    # Using thread pools to parallel processing of images
    with ThreadPoolExecutor() as executor:
        image_embeddings = list(executor.map(get_image_embedding, image_paths))

    # Filter None value (images can not load correctly)
    image_embeddings = [emb for emb in image_embeddings if emb is not None]
    image_embeddings = np.array(image_embeddings, dtype=np.float32)

    # Store image embedding
    np.save("image_embeddings.npy", image_embeddings)

    # Normalization
    norms = np.linalg.norm(image_embeddings, axis=1, keepdims=True)
    norms[norms == 0] = 1  # Avoid dividing by zero
    normalized_embeddings = image_embeddings / norms

    # Calculate the cosine similarity matrix
    similarity_matrix = np.dot(normalized_embeddings, normalized_embeddings.T)

    # Store the similarity matrix
    np.save("similarity_matrix.npy", similarity_matrix)
    print(f"Similarity matrix saved successfully. Shape: {similarity_matrix.shape}")


if __name__ == "__main__":
    precompute_similarity()
