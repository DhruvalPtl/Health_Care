import streamlit as st
import time
import json
import pandas as pd
import google.generativeai as genai
from Authentication import Authentication, logout

auth = Authentication()

def authentication():
    # --- Authentication ---
        if "user_id" not in st.session_state:
            with st.expander("Sign Up"):
                username = st.text_input("Username", value="", placeholder="yourname")
                email = st.text_input("Email Address", placeholder="abc@example.com", value="")
                password = st.text_input("Password", type="password", placeholder="Must be 6+ characters", value="")
                confirm_password = st.text_input("Confirm Password", type="password", placeholder="Must be 6+ characters", value="")
                if st.button("Sign up"):
                    if not username:
                        st.error("Please enter a username")
                    elif not email or "@" not in email or ".com" not in email:
                        st.error("Enter email with valid format")
                    elif not password or len(password) < 6:
                        st.error("Enter 6 or more character password")
                    elif password == confirm_password:
                        auth.sign_up(username, email, confirm_password)
                        st.success("Sign Up successfully! Login to continue")
                    else:
                        st.error("Password do not match")
                        
            with st.expander("Login"):
                email_login = st.text_input("Your Email")
                password_login = st.text_input("Your Password", type="password")
                if st.button("Login"):
                    if not email_login or "@" not in email_login or ".com" not in email_login:
                        st.error("Enter email with valid format")
                    elif not password_login or len(password_login) < 6:
                        st.error("Enter 6 or more character password")
                    elif password_login:
                        auth.login(email_login, password_login)
                        time.sleep(2)
                        st.rerun()
                    else:
                        st.error("Enter Email and Password")
        else:
            st.subheader(f"Welcome {st.session_state["user_name"].capitalize()}")
            if st.button("Logout"):
                logout()
                # Clear all session state data
                for key in list(st.session_state.keys()):
                    del st.session_state[key]
                st.rerun()
def render_sidebar(api_key):
    """
    Renders the sidebar for Medichat AI.
    Returns:
        model_name (str): Selected Gemini model.
        max_length (int): Maximum output length.
        stop_sequence (list): List of stop sequence tokens.
    """
    with st.sidebar:
        
        authentication()
        # --- Welcome Message ---
        st.markdown("## Medichat AI")
        st.markdown("""
        ##  Welcome to MediChat AI!  
        
        Your **AI-powered medical assistant** is here to help!  
        
        -  Get **symptom-based diagnoses**  
        -  Analyze **medical images** (X-ray, MRI)  
        -  Explore **Gemini AI models**  
        -  Manage & download **chat history**  
        
         *Start your conversation and let AI assist you!*  
        """)
        
        # --- API Key & Model Selection ---
        user_api_key = st.text_input("Enter your Gemini API key", type="password")
        if user_api_key:
            genai.configure(api_key=user_api_key)
        elif api_key:
            genai.configure(api_key=api_key)
            st.warning("You can get your Gemini API Key [here](https://aistudio.google.com/app/apikey)")
            
        model_name = st.selectbox("Choose a gemini Model", (
            "gemini-2.0-flash",
            "gemini-2.0-flash-thinking-exp-01-21",
            "gemini-2.0-flash-lite"
        ))
        
        # --- Output Control ---
        with st.expander("Output Control Parameter"):
            max_length = st.number_input("Max Output Length", 1, 8192, 4096)
            stop_sequence_input = st.text_input("Stop Sequence", placeholder="e.g., Thank you!")
            stop_sequence = stop_sequence_input.split(",") if stop_sequence_input else []
        
        # --- Download Chat ---
        with st.expander("Download Chat"):
            if st.session_state.get("messages"):
                def content_to_dict(content_obj):
                    if isinstance(content_obj, dict):
                        return content_obj  
                    return {
                        "role": content_obj.role,
                        "parts": [part.text for part in content_obj.parts],
                    }
                download_message = [content_to_dict(msg) for msg in st.session_state["messages"]]
                json_data = json.dumps(download_message, indent=4)
                st.download_button("As JSON Format", json_data, file_name="chat_history.json", mime="application/json")
                
                df = pd.DataFrame(download_message)
                csv_data = df.to_csv(index=False)
                st.download_button("As CSV Format", csv_data, file_name="chat_history.csv", mime="text/csv")
        
        # --- Clear Chat ---
        if st.button("Clear Chat"):
            st.session_state["messages"] = []
            st.rerun()
    
    # Return values that might be needed in the main app
    return model_name, max_length, stop_sequence
