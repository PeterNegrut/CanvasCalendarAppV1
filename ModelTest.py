from fastai.vision.all import *
from pathlib import Path
from pathlib import Path


def is_cat(x): return x[0].isupper()  # Must match exactly what was used during training

# Load model
learn = load_learner('model (1).pkl')

# Get user input
img_path = input("Path to your image: ")

# Confirm the file exists
if not Path(img_path).exists():
    print("❌ Image not found. Please check the file path.")
    exit()

    

# Predict
pred_class, pred_idx, probs = learn.predict(img_path)

# Map label
animal = "Dog" if pred_class == "False" else "Cat"

# Output result
print(f"Prediction: {animal}, Confidence: {probs[pred_idx]:.4f}")

