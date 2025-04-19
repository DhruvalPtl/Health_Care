import numpy as np
import cv2
from PIL import Image
from tensorflow.keras.models import load_model
import os

def img_pred(img_path, model):
    # Open image directly from file path
    img = Image.open(img_path)

    # Convert to OpenCV format
    opencvImage = cv2.cvtColor(np.array(img), cv2.COLOR_RGB2BGR)

    # Resize image to match model input
    img = cv2.resize(opencvImage, (299, 299))

    # Reshape for model input
    img = img.reshape(1, 299, 299, 3)

    # Make prediction
    p = model.predict(img)
    p = np.argmax(p, axis=1)[0]

    # Map prediction to label
    labels = {0: 'Glioma Tumor', 1: 'Notumor', 2: 'meningioma', 3: 'Pituitary Tumor'}
    # labels = ['glioma','meningioma','notumor','pituitary']
    prediction_label = labels.get(p, 'Unknown')

    # Print result
    print(f'The model predicts: {prediction_label}')

    return prediction_label

# Load model
model = load_model("F:\\internship\\AI-Chatbot-main\\AI-Chatbot-main\\model\\Xception\\Xception(1,299,299,3).keras")

# Image directory
image_dir = "F:\\internship\\AI-Chatbot-main\\AI-Chatbot-main\\brain_tumor_dataset\\yes"

# List image files
image_files = [f for f in os.listdir(image_dir) if f.lower().endswith(('.png', '.jpg', '.jpeg'))]

# Process each image
for img_file in image_files:
    img_path = os.path.join(image_dir, img_file)  # Get full path
    img_pred(img_path, model)
