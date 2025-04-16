import torch
import torch.nn as nn
import torchvision.transforms as transforms
import torchvision.models as models
from PIL import Image
import streamlit as st
import tensorflow as tf
import numpy as np

# Load Chest X-ray Model (CheXNet)
@st.cache_resource
def load_chest_xray_model():
    model = models.densenet121(pretrained=False)
    num_ftrs = model.classifier.in_features
    model.classifier = torch.nn.Linear(num_ftrs, 14)  
    state_dict = torch.load("F:\\internship\\AI-Chatbot-main\\AI-Chatbot-main\\pages\\model.pth.tar", map_location=torch.device('cpu'))
    model.load_state_dict(state_dict, strict=False)
    model.eval()
    return model

# Load Brain Tumor Binary Classifier
@st.cache_resource
def load_brain_tumor_binary_model():
    return tf.keras.models.load_model("F:\\internship\\AI-Chatbot-main\\AI-Chatbot-main\\pages\\brain_tumor_classifier_mobilenet.keras")

# Load Brain Tumor Type Classifier
@st.cache_resource
def load_brain_tumor_type_model():
    return tf.keras.models.load_model("F:\\internship\\AI-Chatbot-main\\AI-Chatbot-main\\pages\\Xception1_1,299,299,3.keras")

# Image Transformations (for PyTorch models)
transform = transforms.Compose([
    transforms.Resize((224, 224)),
    transforms.ToTensor(),
    transforms.Normalize([0.485, 0.456, 0.406], [0.229, 0.224, 0.225])
])

# Chest X-ray Disease Labels
chest_xray_labels = [
    "Atelectasis", "Cardiomegaly", "Effusion", "Infiltration", "Mass", "Nodule",
    "Pneumonia", "Pneumothorax", "Consolidation", "Edema", "Emphysema", "Fibrosis",
    "Pleural Thickening", "Hernia"
]

# Brain Tumor Labels (Binary Classification)
brain_tumor_labels = ["No Tumor", "Tumor"]

# Brain Tumor Type Labels (Multi-class Classification)
brain_tumor_types = ['glioma', 'meningioma','notumor', 'pituitary']

# Streamlit UI
st.title("🩺 Medical Image Diagnosis AI")

# Sidebar for selecting the diagnosis type
diagnosis_type = st.sidebar.selectbox("Select Diagnosis Type", ["Chest X-ray", "Brain Tumor"])

# Image uploader
uploaded_file = st.file_uploader(f"Upload a {diagnosis_type} Image", type=["png", "jpg", "jpeg"])

if uploaded_file is not None:
    image = Image.open(uploaded_file).convert("RGB")
    st.image(image, caption="Uploaded Image", use_container_width=True)

    # Chest X-ray Diagnosis
    if diagnosis_type == "Chest X-ray":
        model = load_chest_xray_model()
        img_tensor = transform(image).unsqueeze(0)

        with torch.no_grad():
            output = model(img_tensor)
        
        probabilities = torch.sigmoid(output[0])
        results = {disease: prob.item() for disease, prob in zip(chest_xray_labels, probabilities)}
        sorted_results = sorted(results.items(), key=lambda x: x[1], reverse=True)

        st.subheader("🩻 Chest X-ray Disease Predictions & Confidence Scores")
        for disease, confidence in sorted_results:
            st.write(f"**{disease}**: {confidence:.2%}")

    # Brain Tumor Diagnosis
    elif diagnosis_type == "Brain Tumor":
        binary_model = load_brain_tumor_binary_model()
        type_model = load_brain_tumor_type_model()

        # Preprocess for TensorFlow Model
        img_array = tf.keras.preprocessing.image.img_to_array(image)
        img_array = tf.image.resize(img_array, (224, 224))
        img_array = img_array / 255.0  # Normalize
        img_array = np.expand_dims(img_array, axis=0)  # Add batch dimension

        # **Step 1: Binary Classification (Tumor / No Tumor)**
        tumor_prediction = binary_model.predict(img_array)
        is_tumor = tumor_prediction[0] > 0.5
        tumor_class = brain_tumor_labels[int(is_tumor)]
        confidence = tumor_prediction[0] if is_tumor else 1 - tumor_prediction[0]

        st.subheader("🧠 Brain Tumor Diagnosis")
        st.write(f"**Diagnosis**: {tumor_class}")
        st.write(f"**Confidence**: {confidence[0]:.2%}")

        # **Step 2: Tumor Type Classification (if Tumor is detected)**
        if is_tumor:
            img = image.resize((299, 299))  # Resize to model input size
            img = np.array(img, dtype=np.float32) / 255.0  # Normalize (0-1 scale)
            
            # Ensure shape is (1, 240, 240, 3)
            img = np.expand_dims(img, axis=0)  # Add batch dimension
            
            type_prediction = type_model.predict(img)
            tumor_type = brain_tumor_types[np.argmax(type_prediction)]
            type_confidence = np.max(type_prediction)

            st.subheader("🔬 Brain Tumor Type Classification")
            st.write(f"**Tumor Type**: {tumor_type}")
            st.write(f"**Confidence**: {type_confidence:.2%}")
