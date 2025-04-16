import tensorflow as tf
from tensorflow.keras.models import load_model
import numpy as np
import cv2
from PIL import Image
import os

# Load the TensorFlow model
model = load_model("F:\\internship\\AI-Chatbot-main\\AI-Chatbot-main\\model\\tumor_type\\effnet\\effnet(1,150,150,3).keras")
# print(model.summary())
# # Define label mapping
# labels = {0: 'Brain tumor', 1: 'Healthy'}

def preprocess_image(img_path):
    """Preprocess image for TensorFlow model"""
    img = Image.open(img_path).convert('RGB')  # Ensure 3 channels
    img = img.resize((150, 150))  # Resize to model input size
    img = np.array(img, dtype=np.float32) / 255.0  # Normalize (0-1 scale)
    
    # Ensure shape is (1, 240, 240, 3)
    img = np.expand_dims(img, axis=0)  # Add batch dimension
    return img

def img_pred(img_path, model):
    """Predict the class of an image using a TensorFlow model"""
    img_tensor = preprocess_image(img_path)  # Preprocess image
    
    predictions = model.predict(img_tensor)  # Get model output
    predicted_class = np.argmax(predictions, axis=1)[0]  # Get class index
    
    prediction_label = labels.get(predicted_class, 'Unknown')  # Map index to label
    print(f'The model predicts: {prediction_label}')
    
    return prediction_label

# Initialize counters
correct = 0
total = 0

# Updated label mapping
# labels = {0: 'glioma', 1: 'notumor', 2: 'meningioma', 3: 'pituitary'}
labels = {0: 'glioma',1: 'meningioma', 2: 'notumor', 3: 'pituitary'}

# Image directory for test dataset
test_image_dir = "F:\\internship\\AI-Chatbot-main\\AI-Chatbot-main\\brain_tumor_mri\\Testing"

# Loop through all four classes
for label, folder in labels.items():  # Folder names should match class labels
    image_folder = os.path.join(test_image_dir, folder)
    image_files = [f for f in os.listdir(image_folder) if f.lower().endswith(('.png', '.jpg', '.jpeg'))]

    for img_file in image_files:
        img_path = os.path.join(image_folder, img_file)
        predicted_label = img_pred(img_path, model)  # Get prediction

        if predicted_label == folder:  # Compare with actual label
            correct += 1
        total += 1

# Calculate accuracy
accuracy = (correct / total) * 100 if total > 0 else 0
print(f"Model Accuracy: {accuracy:.2f}%")
