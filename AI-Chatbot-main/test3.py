import tensorflow as tf
from tensorflow.keras.models import load_model
import numpy as np
from PIL import Image
import os

# Load the trained model
model = load_model("F:\\internship\\AI-Chatbot-main\\AI-Chatbot-main\\model\\tumor_notumor\\mobilenetv2\\brain_tumor_classifier_mobilenet.keras")

# Define label mapping
labels = {0: 'Healthy', 1: 'Brain tumor'}

def preprocess_image(img_path):
    """Preprocess image for TensorFlow model"""
    img = Image.open(img_path).convert("RGB")  # Open image
    img = img.resize((224, 224))  # Resize to model input size
    img = np.array(img)  # Convert to NumPy array
    img = img.astype(np.float32) / 255.0  # Normalize (0-1 scale)
    img = np.expand_dims(img, axis=0)  # Add batch dimension
    return img

def img_pred(img_path, model):
    """Predict the class of an image using a TensorFlow model"""
    img_tensor = preprocess_image(img_path)
    prediction = model.predict(img_tensor)[0][0]  # Get probability
    
    predicted_label = 'Brain tumor' if prediction >= 0.5 else 'Healthy'
    return predicted_label

# Initialize counters
correct = 0
total = 0

# Image directory for test dataset
test_image_dir = "F:\\internship\\AI-Chatbot-main\\AI-Chatbot-main\\brain_tumor_mri\\Testing"

# Loop through both classes (Brain tumor & Healthy)
for label, folder in enumerate(["notumor", "tumor"]):  # 'notumor' -> Healthy (0), 'tumor' -> Brain Tumor (1)
    image_folder = os.path.join(test_image_dir, folder)
    
    # Get all image files
    image_files = [f for f in os.listdir(image_folder) if f.lower().endswith(('.png', '.jpg', '.jpeg'))]

    for img_file in image_files:
        img_path = os.path.join(image_folder, img_file)
        predicted_label = img_pred(img_path, model)  # Get prediction

        # Compare prediction with actual label
        if predicted_label == labels[label]:  
            correct += 1
        total += 1

# Calculate accuracy
accuracy = (correct / total) * 100
print(f"Model Accuracy: {accuracy:.2f}%")
