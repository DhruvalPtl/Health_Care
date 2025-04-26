# app.py
import streamlit as st
from PIL import Image # If using an icon

# --- Page Config (Set only once in the main script) ---
try:
    img = Image.open("icon/icon.png") # Adjust path if needed
    st.set_page_config(
        page_title="MediChat AI Suite",
        page_icon=img,
        layout="wide",
        initial_sidebar_state="expanded" # Keep sidebar open initially
    )
except FileNotFoundError:
     st.set_page_config(page_title="MediChat AI Suite", layout="wide")

st.title("Welcome to the MediChat AI Suite!")
st.markdown("""
Navigate through the different tools using the sidebar on the left.

*   **🧑‍⚕️ Symptom Info:** Get general educational information based on symptoms.
*   **🖼️ Image Analysis:** Analyze Chest X-rays or Brain Scans (Educational Demo).
*   **💬 Chatbot:** A general-purpose AI assistant.
*   **📜 History:** View your past interactions.

**Remember:** Tools providing health-related information are for educational purposes ONLY and are NOT a substitute for professional medical advice.
""")

# The rest of the page logic is handled by files in the pages/ directory
# You might add global setup here if needed later