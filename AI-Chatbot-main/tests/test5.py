from tensorflow.keras.applications.densenet import preprocess_input
from tensorflow.keras.models import load_model
import cv2
import numpy as np

loaded_model = load_model("F:\\internship\\AI-Chatbot-main\\AI-Chatbot-main\\model\\chest_xray\\vgg16_adam.h5")
def preprocess_image(img_path, img_size=(320, 320)):
    img = cv2.imread(img_path)  # Read image
    img = cv2.resize(img, img_size)  # Resize to 320x320
    img = np.expand_dims(img, axis=0)  # Add batch dimension
    img = preprocess_input(img)  # Normalize
    return img

def predict_image(img_path, model):
    img = preprocess_image(img_path)
    preds = model.predict(img)
    return preds

# Example usage
image_path = "F:\\internship\\AI-Chatbot-main\\AI-Chatbot-main\\images\\Cardiomegaly.jpg"  # Replace with actual image path
prediction = list(predict_image(image_path, loaded_model))
print(prediction.index(max(prediction)))