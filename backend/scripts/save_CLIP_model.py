from transformers import CLIPModel, CLIPProcessor

# Use the local path model
model_name = "openai/clip-vit-large-patch14"
local_path = "../models/clip-vit-large-patch14"

# Download and save the model
model = CLIPModel.from_pretrained(model_name)
model.save_pretrained(local_path)

# Download and save the processor
processor = CLIPProcessor.from_pretrained(model_name)
processor.save_pretrained(local_path)

print(f"Models and processors have been downloaded and saved to：{local_path}")

