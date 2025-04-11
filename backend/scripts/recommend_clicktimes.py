# Author:Jinghao Liu, Zihan Zhou
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
image_embeddings = np.load("image_embeddings.npy", allow_pickle=True)
similarity_matrix = np.load("similarity_matrix.npy", allow_pickle=True)

# Assuming image_embeddings.npy is an array where each row corresponds to an image's embedding
# For example, the embeddings for each image could be indexed in the same order as image_names
image_names = [f"{i:06d}_top.jpg" for i in range(1, 301)] + \
              [f"{i:06d}_bottom.jpg" for i in range(1, 301)] + \
              [f"{i:06d}_dress.jpg" for i in range(1, 301)]

# Create a DataFrame to hold image similarity (if not pre-computed)
image_similarity_df = pd.DataFrame(similarity_matrix, index=image_names, columns=image_names)

# A dictionary to track user clicks on images (for a specific user)
user_clicks = {}


# Function to simulate a user click (for demonstration)
def record_user_click(user_id, image_name):
    if user_id not in user_clicks:
        user_clicks[user_id] = {image_name: 1}  # Initialize if it's the user's first click
    else:
        user_clicks[user_id][image_name] = user_clicks[user_id].get(image_name, 0) + 1


# Function to recommend images based on user's click history
def recommend_images_based_on_user_history(user_id, image_name, user_clicks, top_n=3):
    # Ensure the user has a history
    if user_id not in user_clicks:
        print(f"Error: User {user_id} has no click history.")
        return []

    # Retrieve the user's click history
    user_history = user_clicks[user_id]

    # Sort the user's clicked images by the number of clicks in descending order
    sorted_user_history = sorted(user_history.items(), key=lambda x: x[1], reverse=True)

    # Get the top N most clicked images by this user
    most_clicked_by_user = [image for image, _ in sorted_user_history[:top_n]]

    # If the input image is in the list, find the most similar images to it
    if image_name in most_clicked_by_user:
        similar_images = image_similarity_df[image_name].sort_values(ascending=False)[1:top_n + 1]
        return similar_images.index.tolist()
    else:
        return most_clicked_by_user  # Otherwise, recommend the most clicked ones


# Example: Simulate user clicks
record_user_click('user1', '000001_top.jpg')
record_user_click('user1', '000002_top.jpg')
record_user_click('user1', '000002_top.jpg')  # Second click on '000002_top.jpg'
record_user_click('user1', '000003_bottom.jpg')
record_user_click('user1', '000004_top.jpg')

# Example: Get recommendations for a given image based on user history
image_to_recommend = '000001_top.jpg'
user_id = 'user1'
recommended_images = recommend_images_based_on_user_history(user_id, image_to_recommend, user_clicks, top_n=3)

# Output recommendation result
print(f"Recommended similar images for {image_to_recommend} based on user history: {recommended_images}")
