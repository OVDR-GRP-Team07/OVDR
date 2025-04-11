import os
import json
import pymysql
from tqdm import tqdm  # Show progress bar

# Connecting to the MySQL Database
db_config = {
    "host": "localhost",
    "user": "root",
    "password": "123456",
    "database": "ovdr",
    "charset": "utf8mb4"
}
conn = pymysql.connect(**db_config)
cursor = conn.cursor()

# Clothing classification information
# Version 2 (2025.3.13) Change `table` to `category`
CATEGORIES = {
    "tops": {
        "folder": "tops",
        "category": "tops",
        "json_file": "captions/tops_captions.json"
    },
    "bottoms": {
        "folder": "bottoms",
        "category": "bottoms",
        "json_file": "captions/bottoms_captions.json"
    },
    "dresses": {
        "folder": "dresses",
        "category": "dresses",
        "json_file": "captions/dresses_captions.json"
    }
}

# Go through each category
for category, config in CATEGORIES.items():
    folder = os.path.join("data/clothes", config["folder"])
    category_name = config["category"]
    json_path = os.path.join("data/clothes", config["json_file"])

    # # Read JSON Caption file (temporarily disabled)
    captions_data = {}
    if os.path.exists(json_path):
        with open(json_path, "r", encoding="utf-8") as f:
            captions_data = json.load(f)
    else:
        print(f"Warning: {json_path} not found, captions will be 'No caption available'.")

    print(f"Processing category: {category} ...")

    # Get all the cloth files (make sure they are in the same order)
    cloth_dir = os.path.join(folder, "cloth")
    
    if not os.path.exists(cloth_dir):
        print(f"Skipping {category}, directory not found: {cloth_dir}")
        continue
    
    image_files = sorted([f for f in os.listdir(cloth_dir) if f.endswith((".jpg", ".png"))])

    for img_file in tqdm(image_files):  
        file_id = img_file.split("_")[0]  # Extract file number, such as 000001
        
        # Uniformly converts path format to '/' (compatible with Windows/Linux)
        cloth_path = os.path.normpath(os.path.join(folder, "cloth", img_file)).replace("\\", "/")
        cloth_mask_path = os.path.normpath(os.path.join(folder, "cloth-mask", img_file)).replace("\\", "/")
        model_tryon_path = os.path.normpath(os.path.join(folder, "model-tryon", img_file)).replace("\\", "/")


        ## Gets the corresponding captions (temporarily disabled)
        caption_text = captions_data.get(img_file, "No caption available")   # JSON key is filename 
        caption_text = json.dumps(caption_text, ensure_ascii=False)  # JSON format
        # Insert into database
        # version 2: change {table_name} to Clothing
        try:
            sql = f"""
            INSERT INTO Clothing (category, caption, cloth_path, cloth_mask_path, model_tryon_path)
            VALUES (%s, %s, %s, %s, %s)
            """
            cursor.execute(sql, (category_name, caption_text, cloth_path, cloth_mask_path, model_tryon_path))
            conn.commit()
        except Exception as e:
            print(f"Data insertion failure: {e}")
            conn.rollback()

    print(f"Data in {category} has been successfully inserted into Clothing table")

# Close the database connection
cursor.close()
conn.close()
print("Finish!")