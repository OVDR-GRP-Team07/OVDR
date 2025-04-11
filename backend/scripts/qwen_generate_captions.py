# Finally used verion

"""
Clothing Image Caption Generator using Qwen-VL
Author: Zixin Ding

This script is used in the OVDR system to generate structured captions for clothing items
(top, bottom, dress) using Alibaba's Qwen-VL large vision-language model. It processes all
images under `data/clothes/[category]/cloth/` and outputs category-wise caption JSON files.

Features:
- Load CLIP ViT-B/32 for feature consistency
- Call Qwen-VL via Aliyun API (base64 encoded image input)
- Parse response into structured JSON (color, material, neckline, etc.)
- Automatically saves outputs in: `data/clothes/captions/`

Dependencies:
- OpenAI SDK for Aliyun's compatible interface
- tqdm, torch, clip, PIL, requests, base64
"""

import os
import json
import base64
import torch
import clip
from openai import OpenAI
from tqdm import tqdm
from PIL import Image

# OpenAI API Key
ALIYUN_API_KEY = "sk-554f2247d9974560844c8de9ed493a3e"
CLIENT = OpenAI(
    api_key=ALIYUN_API_KEY,
    base_url="https://dashscope.aliyuncs.com/compatible-mode/v1"
)

# Loading CLIP model
device = "cuda" if torch.cuda.is_available() else "cpu"
model, preprocess = clip.load("ViT-B/32", device=device)

# Clothing categories and their JSON files
CATEGORIES = {
    "tops": {
        "output_file": "tops_captions.json",
        "prompt": """
        You are a fashion expert. Describe the clothing item with these features:
        JSON output:
        {
            "upper cloth category": "1-word description",
            "color": "1 or 2 words",
            "pattern": "solid, striped, floral, etc.",
            "material": "1-word",
            "neckline": "1-word",
            "sleeve": "1-word"
        }
        """,
    },
    "bottoms": {
        "output_file": "bottoms_captions.json",
        "prompt": """
        You are a fashion expert. Describe the clothing item with these features:
        JSON output:
        {
            "lower cloth category": "1-word",
            "color": "1 or 2 words",
            "pattern": "solid, striped, floral, etc.",
            "material": "1-word",
            "length": "short, knee-length, long, etc."
        }
        """,
    },
    "dresses": {
        "output_file": "dresses_captions.json",
        "prompt": """
        You are a fashion expert. Describe the clothing item with these features:
        JSON output:
        {
            "dresses category": "1-word",
            "color": "1 or 2 words",
            "pattern": "solid, striped, floral, etc.",
            "material": "1-word",
            "length": "short, knee-length, long, etc.",
            "neckline": "1-word"
        }
        """,
    }
}

# Cloth data base directory
BASE_DIR = "data/clothes"

# Store all caption results
captions = {category: {} for category in CATEGORIES.keys()}


# Image Base64 encoding
def encode_image(image_path):
    """Convert image to base64 encoding for OpenAI API call."""
    with open(image_path, "rb") as image_file:
        return base64.b64encode(image_file.read()).decode("utf-8")


# Call Qwen-VL to generate Caption
def generate_caption_qwen(image_path, prompt):
    """
    Send a base64-encoded image to Qwen-VL with a structured prompt.

    Returns:
        dict: A parsed JSON response from the model.
    """
    base64_image = encode_image(image_path)

    response = CLIENT.chat.completions.create(
        model="qwen-vl-max-latest",
        messages=[
            {"role": "system", "content": [{"type": "text", "text": prompt}]},
            {
                "role": "user",
                "content": [
                    {
                        "type": "image_url",
                        "image_url": {"url": f"data:image/png;base64,{base64_image}"},
                    },
                    {"type": "text", "text": "Describe this clothing item in JSON format."},
                ],
            },
        ],
    )

    try:
        raw_response = response.choices[0].message.content.strip()

        # If there is an error in the JSON structure, try to fix it manually
        if not raw_response.startswith("{"):
            raw_response = raw_response[raw_response.index("{"):]

        if not raw_response.endswith("}"):
            raw_response = raw_response[:raw_response.rindex("}")+1]

        return json.loads(raw_response) 
    except json.JSONDecodeError:
        return {"error": "Invalid JSON response from Qwen-VL"}


# Traverse each category
for category, config in CATEGORIES.items():
    cloth_dir = os.path.join(BASE_DIR, category, "cloth")
    output_file = config["output_file"]
    prompt_text = config["prompt"]

    if not os.path.exists(cloth_dir):
        print(f"Skipping {category}, directory not found: {cloth_dir}")
        continue

    print(f"Processing category: {category} ...")

    # Get all images
    image_files = sorted([f for f in os.listdir(cloth_dir) if f.endswith((".jpg", ".png"))])

    for img_file in tqdm(image_files):
        img_path = os.path.join(cloth_dir, img_file)

        # Preprocessed image
        image = preprocess(Image.open(img_path).convert("RGB")).unsqueeze(0).to(device)

        # CLIP feature extraction
        with torch.no_grad():
            image_features = model.encode_image(image)

        # Generate Caption using Qwen-VL
        try:
            caption_text = generate_caption_qwen(img_path, prompt_text)
            captions[category][img_file] = caption_text
            print(f"[{category}] {img_file} → {caption_text}")

        except Exception as e:
            captions[category][img_file] = {"error": str(e)}
            print(f"Error processing {img_file}: {e}")

    # Store caption results
    output_folder = os.path.join(BASE_DIR, "captions")
    os.makedirs(output_folder, exist_ok=True)
    output_file_path = os.path.join(output_folder, output_file)

    with open(output_file_path, "w", encoding="utf-8") as f:
        json.dump(captions[category], f, indent=4, ensure_ascii=False)

    print(f" Captions for {category} saved to {output_file_path}")

print("All caption generation complete!")
