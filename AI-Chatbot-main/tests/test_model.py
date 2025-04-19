import numpy as np
import tensorflow as tf
from tensorflow.keras.models import load_model
from tensorflow.keras.preprocessing import image
import os

# Load the trained model
model = load_model("F:\\internship\\AI-Chatbot-main\\AI-Chatbot-main\\model\\effnet.h5")  # Ensure correct file path

# Define class labels based on your dataset
CLASS_LABELS = ["glioma", "meningioma", "notumor", "pituitary"]

# Function to preprocess images before prediction
def preprocess_image(img_path, target_size=(150, 150)):
    img = image.load_img(img_path, target_size=target_size, color_mode="rgb")
    img_array = image.img_to_array(img)  
    img_array = np.expand_dims(img_array, axis=0)  # Add batch dimension
    img_array = img_array / 255.0  # Normalize to match training data
    return img_array

# Function to predict tumor type
def predict_tumor(img_path):
    img_array = preprocess_image(img_path)
    prediction = model.predict(img_array)  # Get probabilities for all classes
    predicted_class = np.argmax(prediction)  # Get the class index with highest probability
    confidence = np.max(prediction) * 100  # Get confidence percentage
    print(f"Prediction: {CLASS_LABELS[predicted_class]} ({confidence:.2f}%)")

image_dir = "F:\\internship\\AI-Chatbot-main\\AI-Chatbot-main\\brain_tumor_dataset\\yes"

image_files = [f for f in os.listdir(image_dir) if f.lower().endswith(('.png', '.jpg', '.jpeg'))]

# Process each image
for img_file in image_files:
    img_path = os.path.join(image_dir, img_file)  # Get full path
    predict_tumor(img_path)