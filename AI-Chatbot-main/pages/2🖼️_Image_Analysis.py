import torch
import torch.nn as nn
import torchvision.transforms as transforms
import torchvision.models as models
from PIL import Image
import streamlit as st
import tensorflow as tf 
import numpy as np
import google.generativeai as genai # Import Gemini
import datetime # Import datetime
try:
    from Authentication import Database, Authentication, logout # Import necessary components
    from sidebar import authentication as sidebar_auth_ui # Import the UI function
except ImportError:
    st.error("Failed to import Authentication or Sidebar modules.")
    Database = None
    Authentication = None
    logout = None
    sidebar_auth_ui = None
# Inside image_diagnosis.py
import os

with st.sidebar:
    st.title("Options & Account") # Combined title
    if sidebar_auth_ui:
         # Directly call the function - it contains its own expanders
        sidebar_auth_ui()
    else:
         st.sidebar.warning("Authentication UI could not be loaded.")

# Check login status *after* potentially running the auth UI
IS_LOGGED_IN = "user_id" in st.session_state

# --- Initialize Database (Conditional) ---
db = None
if IS_LOGGED_IN and Database:
    user_id = st.session_state["user_id"]
    try:
        db = Database(user_id)
    except Exception as e:
        st.warning(f"Could not initialize database: {e}. History saving disabled.")
        db = None
    
# --- Configure Gemini API (using secrets) ---
# Ensure API key is configured, preferably once in the main app or sidebar
# For safety, re-configure here if this page runs independently
try:
    # Ensure secrets are loaded correctly based on your setup
    api_key = st.secrets["API_KEY"] # Or st.secrets["GEMINI"]["API_KEY"]
    genai.configure(api_key=api_key)
    gemini_model = genai.GenerativeModel('gemini-2.5-flash-preview-04-17') # Or your preferred model
except KeyError:
    st.error("❗️ Gemini API Key not found in Streamlit Secrets (secrets.toml). Explanation feature disabled.")
    gemini_model = None
except Exception as e:
    st.error(f"❗️ Error configuring Gemini API: {e}. Explanation feature disabled.")
    gemini_model = None

# --- Model Loading Functions (Use RELATIVE Paths!) ---
script_dir = os.path.dirname(os.path.abspath(__file__))

model_dir_path = os.path.abspath(os.path.join(script_dir, "..", "model"))

# --- Model Loading Functions (Using script-relative model_dir_path) ---
@st.cache_resource
def load_chest_xray_model():
    model_filename = "model.pth.tar"
    model_path = os.path.join(model_dir_path, model_filename) # Use calculated path
    if not os.path.exists(model_path):
         st.error(f"Chest X-ray Model file NOT FOUND at: {model_path}")
         return None
    try:
        state_dict = torch.load(model_path, map_location=torch.device('cpu'))
        # Recreate model structure (ensure models, nn are imported)
        model = models.densenet121(pretrained=False)
        num_ftrs = model.classifier.in_features
        model.classifier = nn.Linear(num_ftrs, 14)
        model.load_state_dict(state_dict, strict=False)
        model.eval()
        return model
    except Exception as e:
         st.error(f"Error loading Chest X-ray model: {e}")
         return None

@st.cache_resource
def load_brain_tumor_binary_model():
    model_filename = "brain_tumor_classifier_mobilenet.keras"
    model_path = os.path.join(model_dir_path, model_filename) # Use calculated path
    if not os.path.exists(model_path):
         st.error(f"Binary Tumor Model file NOT FOUND at: {model_path}")
         return None
    try:
        return tf.keras.models.load_model(model_path)
    except Exception as e:
         st.error(f"Error loading Binary Tumor model: {e}")
         return None

@st.cache_resource
def load_brain_tumor_type_model():
    model_filename = "Xception1_1,299,299,3.keras" # Filename with commas
    model_path = os.path.join(model_dir_path, model_filename) # Use calculated path
    if not os.path.exists(model_path):
         st.error(f"Type Tumor Model file NOT FOUND at: {model_path}")
         return None
    try:
        return tf.keras.models.load_model(model_path)
    except Exception as e:
         st.error(f"Error loading Type Tumor model: {e}")
         return None

# --- Image Transformations & Labels (Keep as is) ---
# ... (transform, chest_xray_labels, brain_tumor_labels, brain_tumor_types) ...
chest_xray_labels = [
    "Atelectasis", "Cardiomegaly", "Effusion", "Infiltration", "Mass", "Nodule",
    "Pneumonia", "Pneumothorax", "Consolidation", "Edema", "Emphysema", "Fibrosis",
    "Pleural Thickening", "Hernia"
]
brain_tumor_labels = ["No Tumor", "Tumor"]
brain_tumor_types = ['glioma', 'meningioma','notumor', 'pituitary']
transform = transforms.Compose([
    transforms.Resize((224, 224)),
    transforms.ToTensor(),
    transforms.Normalize([0.485, 0.456, 0.406], [0.229, 0.224, 0.225])
])


# --- NEW Helper Function for Gemini Explanation ---
def get_gemini_image_explanation(prediction_details_text):
    """Generates a safe, educational explanation using Gemini."""
    if not gemini_model:
        return "AI explanation feature is currently unavailable."

    prompt = f"""
    Role: AI assistant explaining results from a medical image analysis model for educational purposes ONLY.
    Context: An AI model analyzed a medical image and produced the following findings:
    "{prediction_details_text}"

    Task: Provide a brief, simple, educational explanation of what these findings *generally* might suggest.
    Instructions:
    1.  **DO NOT DIAGNOSE.** Do not confirm any disease.
    2.  Keep the language simple and accessible.
    3.  Focus on general meaning (e.g., "findings suggestive of inflammation", "abnormal growth characteristics").
    4.  **Emphasize strongly** that this is AI output, NOT a real medical diagnosis, and the user MUST consult a qualified doctor/radiologist for interpretation and diagnosis.
    5.  Keep it concise (2-4 sentences).

    Example output (for 'Pneumonia: 85%'): "The AI analysis highlights findings that are often associated with inflammation in the lungs, like pneumonia. However, this is an automated result and not a diagnosis. It's essential to discuss these findings with a qualified healthcare professional for accurate interpretation."
    """
    try:
        response = gemini_model.generate_content(prompt)
        return response.text.strip()
    except Exception as e:
        return f"Could not generate AI explanation: {e}"

# --- Initialize Database (If user logged in) ---
db = None
if "user_id" in st.session_state:
    user_id = st.session_state["user_id"]
    try:
        # Ensure Database class is available
        from Authentication import Database
        db = Database(user_id)
    except ImportError:
        st.warning("Authentication module not found. History saving disabled.")
    except Exception as e:
        st.warning(f"Could not initialize database: {e}. History saving disabled.")

# --- Streamlit UI ---
st.subheader("🖼️ Medical Image Analysis")
st.markdown("""
    Upload Chest X-ray or Brain Scan images for analysis by AI models (DenseNet, MobileNet, Xception).
    *   Receive potential findings and confidence scores.
    *   Get a simplified AI-generated explanation of the results.
    *   **Reminder:** AI analysis can support understanding, but **final interpretation requires a medical professional.** Always discuss results with your doctor.
    """)
if IS_LOGGED_IN:
    diagnosis_type = st.selectbox("Select Analysis Type", ["Chest X-ray", "Brain Tumor"], key="diag_type_select") # Moved from sidebar
    uploaded_file = st.file_uploader(f"Upload a {diagnosis_type} Image", type=["png", "jpg", "jpeg"], key=f"uploader_{diagnosis_type}")
else:
    st.info("ℹ️ Please log in using the sidebar to upload an image and use the analysis tool.")
    uploaded_file = None # Ensure uploader is effectively disabled
    diagnosis_type = None
    
if IS_LOGGED_IN and uploaded_file is not None and diagnosis_type is not None:
    image = Image.open(uploaded_file).convert("RGB")
    st.image(image, caption="Uploaded Image", use_container_width=True)

    # --- Initialize variables for saving ---
    results_to_save = {}
    raw_prediction_text = "No prediction generated."
    ai_explanation_text = "No explanation generated."

    # --- Process Image ---
    try: # Wrap processing in try block
        if diagnosis_type == "Chest X-ray":
            with st.spinner("Analyzing Chest X-ray..."):
                model = load_chest_xray_model()
                img_tensor = transform(image).unsqueeze(0)
                with torch.no_grad():
                    output = model(img_tensor)
                probabilities = torch.sigmoid(output[0])
                results = {disease: prob.item() for disease, prob in zip(chest_xray_labels, probabilities)}
                sorted_results = sorted(results.items(), key=lambda x: x[1], reverse=True)

            st.subheader("🩻 Chest X-ray Analysis Results")
            prediction_lines = []
            for disease, confidence in sorted_results:
                line = f"**{disease}**: {confidence:.2%}"
                st.write(line)
                if confidence > 0.50: # Or some threshold to decide what to explain
                     prediction_lines.append(line.replace("**","")) # Collect significant findings for explanation

            # Generate Text for Explanation & Saving
            raw_prediction_text = "\n".join(prediction_lines) if prediction_lines else "No significant findings above threshold."
            if gemini_model:
                 ai_explanation_text = get_gemini_image_explanation(f"Chest X-ray findings:\n{raw_prediction_text}")
                 st.info(f"**AI Explanation (Educational):** {ai_explanation_text}")

            # Prepare data for saving
            results_to_save = {
                "timestamp": datetime.datetime.now().isoformat(),
                "image_type": "Chest X-ray",
                "diagnosis_details": {disease: f"{conf:.2%}" for disease, conf in sorted_results[:5]}, # Save top 5 raw scores
                "ai_explanation": ai_explanation_text
            }

        elif diagnosis_type == "Brain Tumor":
            with st.spinner("Analyzing Brain Scan..."):
                binary_model = load_brain_tumor_binary_model()
                type_model = load_brain_tumor_type_model()

                # Preprocessing (Keep as is)
                img_array_binary = tf.keras.preprocessing.image.img_to_array(image)
                img_array_binary = tf.image.resize(img_array_binary, (224, 224)) / 255.0
                img_array_binary = np.expand_dims(img_array_binary, axis=0)

                # Binary Classification (Keep as is)
                tumor_prediction = binary_model.predict(img_array_binary)
                diagnosis_confidence_raw = tumor_prediction[0][0]
                is_tumor = diagnosis_confidence_raw > 0.5
                tumor_class = "Tumor" if is_tumor else "No Tumor"
                display_diagnosis_confidence = diagnosis_confidence_raw if is_tumor else 1 - diagnosis_confidence_raw

            st.subheader("🧠 Brain Tumor Diagnosis")
            binary_result_text = f"**Diagnosis**: {tumor_class} (Confidence: {display_diagnosis_confidence:.2%})"
            st.write(binary_result_text)
            raw_prediction_text = binary_result_text.replace("**","") # Start prediction text

            # Conditional Type Classification (Keep as is)
            diagnosis_confidence_threshold = 0.50
            type_result_text = ""
            tumor_type_detail = "N/A"

            if is_tumor and display_diagnosis_confidence >= diagnosis_confidence_threshold:
                st.subheader("🔬 Brain Tumor Type Classification")
                with st.spinner("Classifying tumor type..."):
                    # Preprocessing for Type Model (Keep as is)
                    img_array_type = tf.keras.preprocessing.image.img_to_array(image)
                    img_array_type = tf.image.resize(img_array_type, (299, 299)) / 255.0
                    img_array_type = np.expand_dims(img_array_type, axis=0)
                    # Predict type (Keep as is)
                    type_prediction = type_model.predict(img_array_type)
                    prediction_index = np.argmax(type_prediction[0])
                    tumor_type = brain_tumor_types[prediction_index]
                    type_confidence = type_prediction[0][prediction_index]

                tumor_type_detail = f"{tumor_type} (Confidence: {type_confidence:.2%})" # For saving

                # Handle 'notumor' conflict (Keep as is)
                if tumor_type.lower() == 'notumor':
                    warning_text = f"Initial diagnosis suggested 'Tumor' (Confidence: {display_diagnosis_confidence:.2%}), but detailed classification suggests 'No Tumor' (Confidence: {type_confidence:.2%}). This can occur in borderline cases."
                    st.warning(warning_text)
                    type_result_text = warning_text # Use warning as part of summary
                else:
                    type_result_text = f"**Tumor Type**: {tumor_type} (Confidence: {type_confidence:.2%})"
                    st.write(type_result_text)
                    raw_prediction_text += f"\n{type_result_text.replace('**','')}" # Add type result to summary

            elif is_tumor and display_diagnosis_confidence < diagnosis_confidence_threshold:
                low_conf_text = f"Initial diagnosis suggested 'Tumor', but with low confidence ({display_diagnosis_confidence:.2%}). Detailed classification not performed."
                st.warning(low_conf_text)
                type_result_text = low_conf_text # Use warning as part of summary
                raw_prediction_text += f"\n{low_conf_text}" # Add warning to summary

            # Generate Explanation for Brain Tumor
            if gemini_model:
                ai_explanation_text = get_gemini_image_explanation(f"Brain Scan Analysis:\n{raw_prediction_text}")
                st.info(f"**AI Explanation (Educational):** {ai_explanation_text}")

            # Prepare data for saving
            results_to_save = {
                "timestamp": datetime.datetime.now().isoformat(),
                "image_type": "Brain Tumor",
                "diagnosis_details": {
                    "Binary_Diagnosis": f"{tumor_class} ({display_diagnosis_confidence:.2%})",
                    "Type_Classification": tumor_type_detail # Captures type or N/A or conflict info
                 },
                "ai_explanation": ai_explanation_text
            }

        # --- Attempt to Save History (Common to both types) ---
        if db and user_id and results_to_save: # Check if db initialized and user logged in and results exist
             with st.spinner("Saving results to history..."):
                 save_success = db.save_image_diagnosis_result(results_to_save)
                 # Optionally provide feedback, though it might be below the fold
                 if save_success:
                     st.success("Results saved to history.")
                 else:
                     st.error("Failed to save results to history.")

    except Exception as e:
        st.error(f"An error occurred during image processing or analysis: {e}")
        # Optionally clear results_to_save here if you don't want partial saves on error
        results_to_save = {}