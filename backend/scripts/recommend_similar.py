# Author:Jinghao Liu, Zihan Zhou
# dependency: pip install fastapi uvicorn sqlalchemy pymysql numpy pandas

import os
import numpy as np
import pandas as pd

# Base folder path and folder for image storage
base_path = os.path.join("..", "data", "clothes")
image_folders = {
    "bottoms": os.path.join(base_path, "bottoms", "cloth"),
    "dresses": os.path.join(base_path, "dresses", "cloth"),
    "tops": os.path.join(base_path, "tops", "cloth"),
}

# Load pre-computed image embeddings and similarity matrix
image_embeddings = np.load("image_embeddings.npy", allow_pickle=True)  # No need to call .item()
similarity_matrix = np.load("similarity_matrix.npy", allow_pickle=True)

# Assuming image_embeddings.npy is an array where each row corresponds to an image's embedding
# For example, the embeddings for each image could be indexed in the same order as image_names
image_names = [f"{i:06d}_top.jpg" for i in range(1, 301)] + \
              [f"{i:06d}_bottom.jpg" for i in range(1, 301)] + \
              [f"{i:06d}_dress.jpg" for i in range(1, 301)]

# Create a DataFrame to hold image similarity (if not pre-computed)
image_similarity_df = pd.DataFrame(similarity_matrix, index=image_names, columns=image_names)


# Recommend similar images based on pre-computed similarity matrix
def recommend_similar_images(image_name, image_similarity_df, top_n=3):
    similar_images = image_similarity_df[image_name].sort_values(ascending=False)[1:top_n + 1]
    return similar_images.index.tolist()


# For a given image, recommend similar ones
image_to_recommend = '000008_top.jpg'  # Example image
recommended_images = recommend_similar_images(image_to_recommend, image_similarity_df, top_n=10)

# Output recommendation result
print(f"Recommended similar images for {image_to_recommend}: {recommended_images}")
