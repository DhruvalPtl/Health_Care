# app.py (Your main application script)

import streamlit as st
from PIL import Image
import os
import google.generativeai as genai # For initial configuration

# --- Page Configuration ---
# Calculate icon path relative to this script
APP_DIR = os.path.dirname(os.path.abspath(__file__))
ICON_PATH = os.path.join(APP_DIR, "icon", "icon.png") # Assumes icon folder is at the root

try:
    page_icon = Image.open(ICON_PATH)
except FileNotFoundError:
    st.warning(f"Icon not found at {ICON_PATH}, using default.")
    page_icon = "🩺" # Default emoji icon
except Exception as e:
    st.warning(f"Error loading icon: {e}")
    page_icon = "🩺"

st.set_page_config(
    page_title="MediChat AI Suite",
    page_icon=page_icon, # Use loaded image or default emoji
    layout="wide",
    initial_sidebar_state="expanded", # Keep sidebar open initially
    menu_items={ # Optional: Customize menu
        'Get Help': None, # Can link to documentation or remove
        'Report a bug': None,
        'About': "# MediChat AI Suite\nAn educational AI assistant demo."
    }
)

# --- Initial API Configuration (Do this once here) ---
try:
    # Load API key securely from secrets
    api_key = st.secrets["API_KEY"] # Ensure this matches your secrets.toml key name
    genai.configure(api_key=api_key)
    # Optionally add a small indicator in sidebar if config succeeds,
    # but avoid cluttering. Other pages can handle specific model init errors.
    # st.sidebar.caption("API Configured")
except KeyError:
    st.error("🔴 **Error:** Gemini API Key not found in Streamlit Secrets (`secrets.toml`). AI features requiring the key will fail.")
    st.stop() # Stop execution if key is essential and missing
except Exception as e:
    st.error(f"🔴 **Error configuring Gemini API:** {e}")
    st.stop() # Stop execution on configuration error


# --- Welcome / Landing Page Content ---

st.title("MediChat AI: Your AI Health Information Assistant")
st.subheader("Your AI-Powered Healthcare Tool Hub")

# st.markdown("---")

st.info(
    """
    **Important Note:** This application provides AI-powered tools for educational and informational purposes.
    The insights generated are based on algorithms and data, and **should not replace the judgment of a qualified healthcare professional.**
    For any health concerns or medical decisions, please **always consult with your doctor or another qualified healthcare provider.**
    """
)

st.markdown("---")

st.header("Available Tools:")
st.markdown("Use the sidebar navigation on the left to access the different features:")

col1, col2 = st.columns(2)

with col1:
    st.subheader("🧑‍⚕️ Symptom Information")
    st.markdown("""
    Describe your symptoms and duration to receive **general educational information**.
    *   The AI may ask a clarifying question.
    *   Provides links to reputable health resources (NHS, CDC).
    *   **Does NOT provide diagnoses or medical advice.**
    """)
    try: st.page_link("pages/1🧑‍⚕️_Symptom_Info.py", label="Go to Symptom Info", icon="🧑‍⚕️")
    except: pass

    st.subheader("💬 General Chatbot")
    st.markdown("""
    Engage in a general conversation with the Gemini AI model.
    *   Ask questions on various topics.
    *   Experiment with the AI's text generation capabilities.
    *   **Note:** Avoid asking for medical diagnoses here; use the dedicated tools.
    """)
    # Optional: Add a direct link button if desired (st.page_link needs file path)
    try: st.page_link("pages/3💬_Chatbot.py", label="Go to Chatbot", icon="💬")
    except: pass # Handle error if page doesn't exist


with col2:
    st.subheader("🖼️ Medical Image Analysis")
    st.markdown("""
    Upload Chest X-ray or Brain Scan images for analysis by AI models (DenseNet, MobileNet, Xception).
    *   Receive potential findings and confidence scores.
    *   Get a simplified AI-generated explanation of the results.
    *   **Educational Use Only:** Results are illustrative and not a real diagnosis.
    """)
    try: st.page_link("pages/2🖼️_Image_Analysis.py", label="Go to Image Analysis", icon="🖼️")
    except: pass
    
    st.subheader("📜 History")
    st.markdown("""
    Review your past interactions with the different tools (requires login).
    *   View Chatbot conversations.
    *   See previous Symptom Information entries.
    *   Check past Image Analysis results.
    *   Download your history data.
    """)
    try: st.page_link("pages/4📜_History.py", label="Go to History", icon="📜")
    except: pass


st.markdown("---")
st.caption("Navigate using the sidebar. Ensure you are logged in to save history.")

# No need to call render_sidebar() here - the individual pages will handle it.