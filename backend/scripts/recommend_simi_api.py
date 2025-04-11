# Author:Jinghao Liu, Zihan Zhou
import os
import numpy as np
import pandas as pd
from fastapi import FastAPI, HTTPException, Depends
from sqlalchemy.orm import Session
from models import Clothing, SessionLocal

# Load the pre_calculate data
image_embeddings = np.load("image_embeddings.npy", allow_pickle=True)
similarity_matrix = np.load("similarity_matrix.npy", allow_pickle=True)
image_names = [f"{i:06d}_top.jpg" for i in range(1, 301)] + \
              [f"{i:06d}_bottom.jpg" for i in range(1, 301)] + \
              [f"{i:06d}_dress.jpg" for i in range(1, 301)]
image_similarity_df = pd.DataFrame(similarity_matrix, index=image_names, columns=image_names)

# FastAPI instance
app = FastAPI()

# Get the database connection
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@app.get("/recommend/{clothing_id}")
def recommend_images(clothing_id: int, db: Session = Depends(get_db), top_n: int = 3):
    # Query the database for clothing information
    clothing = db.query(Clothing).filter(Clothing.cid == clothing_id).first()
    if not clothing:
        raise HTTPException(status_code=404, detail="Clothing item not found")

    # Get image name
    image_name = os.path.basename(clothing.cloth_path)

    # Make sure the image exists in the similarity matrix
    if image_name not in image_similarity_df.index:
        raise HTTPException(status_code=404, detail="Image not found in similarity matrix")

    # Get the most similar images
    similar_images = image_similarity_df[image_name].nlargest(top_n + 1).iloc[1:].index.tolist()

    # Query the database to find the corresponding 'clothing_id'
    recommended_items = db.query(Clothing).filter(Clothing.cloth_path.in_(similar_images)).all()

    return {"recommended_clothing_ids": [item.cid for item in recommended_items]}