import streamlit as st
from sidebar import authentication
from Authentication import Database , logout # Assuming this is your Firebase helper class
import json
import datetime

st.set_page_config(page_title="History", page_icon="📜", layout="wide")
st.title("📜 History")

api_key = st.secrets["API_KEY"]

# Sidebar options with download buttons
with st.sidebar:
    authentication()
    if "user_id" in st.session_state:
        with st.sidebar:
            st.markdown("---")
            st.markdown("### View History")
            # --- UPDATED RADIO BUTTON ---
            history_option = st.radio(
                "Choose History Type",
                ("Chat History", "Symptom Information", "Image Analysis"), # Added new option
                key="history_radio"
            )

# --- Main History Display Area ---

# Ensure the user is logged in before showing history
if "user_id" not in st.session_state:
    st.warning("ℹ️ Please log in to view your history.")
    st.stop()
elif not Database:
    st.error("Database connection module not available.")
    st.stop()

# Initialize your database helper for the logged-in user
user_id = st.session_state["user_id"]
db = Database(user_id)

st.header(f"Viewing: {history_option}")
if history_option == "Chat History":
    chat_history = db.get_chat_history() # Uses updated method name
    if chat_history:
        st.write("Your past chat conversations:")
        if isinstance(chat_history, list):
            for msg in reversed(chat_history): # Show newest first
                role = msg.get("role", "model")
                display_role = "assistant" if role == "model" else role
                parts = msg.get("parts", [])
                message_text = " ".join(parts)
                st.chat_message(display_role).write(message_text)
        else:
            st.warning("Chat history format not recognized (expected list).")
    else:
        st.info("No chat history found.")

elif history_option == "Symptom Information": # Updated label
    symptom_history = db.get_symptom_history() # Uses updated method name
    if symptom_history:
        st.write("Your past symptom information entries:")
        # Sort by push key (roughly chronological)
        for key in sorted(symptom_history.keys(), reverse=True): # Show newest first
            entry = symptom_history[key]
            initial_input_desc = entry.get("Question", "N/A")
            ai_summary = entry.get("Answer", "N/A")
            # You might want to add timestamp display here if you saved it
            st.markdown(f"**Entry ID:** `{key}`")
            st.markdown(f"**Your Input:** {initial_input_desc}")
            st.markdown(f"**AI Educational Summary:**")
            st.markdown(f"> {ai_summary.replace(chr(10), chr(10) + '> ')}") # Blockquote format for summary
            st.markdown("---")
    else:
        st.info("No symptom information history found.")

# --- NEW elif block for Image History ---
elif history_option == "Image Analysis":
    image_history = db.get_image_history() # Use new method
    if image_history:
        st.write("Your past image analysis results:")
        # Sort by push key (roughly chronological)
        for key in sorted(image_history.keys(), reverse=True): # Show newest first
            entry = image_history[key]
            # Extract data (handle potential missing keys)
            timestamp_str = entry.get("timestamp", "N/A")
            image_type = entry.get("image_type", "N/A")
            details = entry.get("diagnosis_details", {})
            ai_explanation = entry.get("ai_explanation", "N/A")

            # Format timestamp (optional)
            try:
                dt_object = datetime.datetime.fromisoformat(timestamp_str)
                display_time = dt_object.strftime("%Y-%m-%d %H:%M:%S")
            except:
                display_time = timestamp_str

            st.markdown(f"**Entry ID:** `{key}` ({display_time})")
            st.markdown(f"**Image Type:** {image_type}")

            # Display Diagnosis Details nicely
            st.markdown("**Model Findings:**")
            if isinstance(details, dict):
                for detail_key, detail_value in details.items():
                    st.markdown(f"- {detail_key.replace('_',' ')}: {detail_value}")
            else:
                 st.markdown(f"- {details}") # Fallback if not a dict

            st.markdown("**AI Educational Explanation:**")
            st.markdown(f"> {ai_explanation.replace(chr(10), chr(10) + '> ')}") # Blockquote format

            st.markdown("---") # Separator
    else:
        st.info("No image analysis history found.")

# Optionally, you could add a button to download history as JSON
with st.sidebar:
    st.markdown("---")
    st.markdown("### Download History")

    # Button to trigger data preparation
    if st.button("Prepare Full History Download"):
        if "user_id" in st.session_state and db:
            try:
                with st.spinner("Preparing download data..."):
                    # Fetch fresh data from the database
                    chat_data = db.get_chat_history()
                    symptom_data = db.get_symptom_history()
                    image_data = db.get_image_history()

                    full_history_data = {
                        "chat_history": chat_data,
                        "symptom_information_history": symptom_data,
                        "image_analysis_history": image_data
                    }
                    # Store prepared JSON in session state
                    st.session_state.download_data_json = json.dumps(full_history_data, indent=4)
                    st.session_state.show_download_button = True # Flag to show button
                    # --- No success message here, show implicitly by download button appearing ---

            except Exception as e:
                st.error(f"Error preparing download: {e}")
                # Ensure button flag is False on error
                if "show_download_button" in st.session_state:
                     del st.session_state.show_download_button
                if "download_data_json" in st.session_state:
                     del st.session_state.download_data_json
        else:
            st.warning("Please log in to prepare download.")
            # Ensure flags are False if not logged in
            if "show_download_button" in st.session_state:
                 del st.session_state.show_download_button
            if "download_data_json" in st.session_state:
                 del st.session_state.download_data_json

    # Conditionally display the download button
    if st.session_state.get("show_download_button", False) and "download_data_json" in st.session_state:
        st.download_button(
            label="⬇️ Download All History (JSON)",
            data=st.session_state.download_data_json,
            file_name=f"medichat_history_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}.json",
            mime="application/json",
            key="download_hist_btn" # Add a key
        )
        # --- KEY CHANGE: Clear the state *after* rendering the button ---
        # This ensures the button disappears on the next rerun unless "Prepare" is clicked again.
        del st.session_state.show_download_button
        if "download_data_json" in st.session_state: # Check just in case it failed to be created
             del st.session_state.download_data_json