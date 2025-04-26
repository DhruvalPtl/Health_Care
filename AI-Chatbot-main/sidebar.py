import streamlit as st
import time
import json
import pandas as pd
import google.generativeai as genai
from Authentication import Authentication, logout, Database
import datetime

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
            st.subheader(f'Welcome {st.session_state["user_name"].capitalize()}')
            if st.button("Logout"):
                logout()
                # Clear all session state data
                for key in list(st.session_state.keys()):
                    del st.session_state[key]
                st.rerun()
                
def render_sidebar(api_key,db_connection):
    """
    Renders the sidebar for Medichat AI.
    Returns:
        model_name (str): Selected Gemini model.
        max_length (int): Maximum output length.
        stop_sequence (list): List of stop sequence tokens.
    """
    db = None
    if Database and "user_id" in st.session_state:
        try:
            db = Database(st.session_state["user_id"])
        except Exception as e:
            st.sidebar.warning(f"DB connection error for actions: {e}")

    with st.sidebar:
        
        authentication()
        # --- API Key & Model Selection ---
        user_api_key = st.text_input("Enter your Gemini API key", type="password")
        if user_api_key:
            genai.configure(api_key=user_api_key)
        elif api_key:
            genai.configure(api_key=api_key)
            st.warning("You can get your Gemini API Key [here](https://aistudio.google.com/app/apikey)")
            
        st.markdown("AI Model Settings")
        
        # --- Output Control ---
        with st.expander("Output Control Parameter"):
            model_name = st.selectbox("Choose a gemini Model", (
                "gemini-2.5-flash-preview-04-17",
                "gemini-2.5-pro-preview-03-25",
                "gemini-2.0-flash",
                "gemini-2.0-flash-thinking-exp-01-21"
            ))
            
            max_length = st.number_input("Max Output Length", 1, 8192, 4096)
            stop_sequence_input = st.text_input("Stop Sequence", placeholder="e.g., Thank you!")
            stop_sequence = stop_sequence_input.split(",") if stop_sequence_input else []
        
        if "user_id" in st.session_state:    
            st.warning("Deleting history is permanent.")
            if st.button("🗑️ Delete Chat History from DB", key="delete_chat_prep_sidebar"):
                st.session_state.confirm_delete_sidebar = True # Use unique key

            # Confirmation step for delete
            if st.session_state.get("confirm_delete_sidebar", False):
                st.error("Permanently delete chat history?")
                col1, col2 = st.columns(2)
                with col1:
                    if st.button("YES, DELETE DB", type="primary", key="delete_chat_confirm_sidebar"):
                        if db_connection: # Check if db object was passed and valid
                            delete_success = db_connection.delete_chat_history()
                            if delete_success:
                                # Clear session state too
                                if "messages" in st.session_state: st.session_state["messages"] = []
                                if "chat" in st.session_state: del st.session_state["chat"]
                                st.success("Chat history deleted from database.")
                            # Error message is shown inside delete_chat_history if it fails
                        else:
                            st.error("Database connection not available or not logged in.")
                        # Always clear flag and rerun after action attempt
                        del st.session_state.confirm_delete_sidebar
                        st.rerun()
                with col2:
                    if st.button("Cancel Delete", key="delete_chat_cancel_sidebar"):
                        del st.session_state.confirm_delete_sidebar # Clear flag
                        st.rerun() # Rerun to hide confirmation
        else:
        # --- Clear Current Session Button (Only when not logged in) ---
            if st.button("✨ Clear Current Session", key="clear_chat_session_btn"):
                if "messages" in st.session_state: st.session_state["messages"] = []
                if "chat" in st.session_state: del st.session_state["chat"]
                st.success("Chat session cleared.")
                st.rerun()
                                
        # --- Download Chat ---
        if st.button("Prepare Chat History Download", key="prepare_chat_dl_btn"):
                    # Proceed with preparation
            with st.spinner("Preparing chat data..."):
                # --- Get definitive history from the chat object ---
                current_chat_history_obj = st.session_state.chat.history

                # --- Convert to list[dict] ---
                # Define helper function locally or ensure it's available
                def content_to_dict(content_obj):
                        if isinstance(content_obj, dict): return content_obj
                        if hasattr(content_obj, 'role') and hasattr(content_obj, 'parts'):
                            return {"role": content_obj.role, "parts": [part.text for part in content_obj.parts]}
                        return {"role": "unknown", "parts": [str(content_obj)]}
                dict_list_history = [content_to_dict(msg) for msg in current_chat_history_obj]

                if dict_list_history:
                        # Store prepared JSON in session state
                        st.session_state.download_chat_data_json = json.dumps(dict_list_history, indent=4)
                        st.session_state.show_chat_download_button = True # Flag to show button
                        st.caption("Data prepared. Download button below.") # Feedback
                else:
                        st.info("Chat history is currently empty.")
                        if "show_chat_download_button" in st.session_state: del st.session_state.show_chat_download_button

        # Conditionally display the actual download button
            if st.session_state.get("show_chat_download_button", False) and "download_chat_data_json" in st.session_state:
                st.download_button(
                    label="⬇️ Download Prepared Chat (JSON)",
                    data=st.session_state.download_chat_data_json, # Use prepared data
                    # Add timestamp to filename
                    file_name=f"chatbot_history_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}.json",
                    mime="application/json",
                    key="dl_chat_btn"
                )
                # Clear the flag/data immediately after rendering the button
                # This forces the user to click "Prepare" again for the next download
                del st.session_state.show_chat_download_button
                if "download_chat_data_json" in st.session_state:
                    del st.session_state.download_chat_data_json
        
    # Return values that might be needed in the main app
    return model_name, max_length, stop_sequence
