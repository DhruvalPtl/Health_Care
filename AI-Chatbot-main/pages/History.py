import streamlit as st
from sidebar import authentication
from Authentication import Database , logout # Assuming this is your Firebase helper class
import json

st.set_page_config(page_title="History", page_icon="📜", layout="wide")
st.title("Chat & Symptom History")

api_key = "AIzaSyCJUg1gHTskBBY-v0oaYvvMyKUF5z2-lZ0"

# Sidebar options with download buttons
with st.sidebar:
    authentication()
    if "user_id" in st.session_state:
        st.markdown("---")
        # --- History Type Selection ---
        st.markdown("### History Options")
        history_option = st.radio("Choose History Type", ("Chat History", "Symptom History"))

# Ensure the user is logged in before showing history
if "user_id" not in st.session_state:
    st.error("Please log in to view your history.")
    st.stop()

# Initialize your database helper for the logged-in user
user_id = st.session_state["user_id"]
db = Database(user_id)

# Retrieve chat history (if any)
chat_history = db.chat_history1()  # Implement this method to return chat_history as a dict/object
symptom_history = db.symptom_history()  # Implement a similar method for symptom_history

st.header("History")
if history_option == "Chat History":
    if chat_history:
        st.header("Chat Sessions:")
        
        # If chat_history is a dict (as with push() entries using numeric keys)
        if isinstance(chat_history, dict):
            # Sort keys numerically if possible
            def key_sort(x):
                try:
                    return int(x)
                except ValueError:
                    return x

            sorted_keys = sorted(chat_history.keys(), key=key_sort)
            
            for key in sorted_keys:
                msg = chat_history[key]
                role = msg.get("role", "unknown")
                parts = msg.get("parts", [])
                # Join parts if there are multiple segments
                message_text = " ".join(parts)
                
                st.markdown(f"**{role.capitalize()}:** {message_text}")
                st.markdown("---")
        elif isinstance(chat_history, list):
            # Fallback if Firebase returns a list (unlikely with push keys)
            for msg in chat_history:
                role = msg.get("role", "unknown")
                parts = msg.get("parts", [])
                message_text = " ".join(parts)
                st.markdown(f"**{role.capitalize()}:** {message_text}")
                st.markdown("---")
        else:
            st.info("Chat history format not recognized.")
    else:
        st.info("No chat history found.")

elif history_option == "Symptom History":
    if symptom_history:
        st.header("Symptom Checker History")
        # symptom_history assumed to be a dict where each key is a push key with a dict value
        for key, entry in symptom_history.items():
            question = entry.get("Question", "No question provided")
            answer = entry.get("Answer", "No answer provided")
            st.markdown(f"**Record:** {key}")
            st.write(f"**Question:** {question}")
            st.write(f"**Answer:** {answer}")
            st.markdown("---")
    else:
        st.info("No symptom checker history found.")

# Optionally, you could add a button to download history as JSON
with st.sidebar:
    if st.button("Download Full History as JSON"):
        full_history = {"chat_history": chat_history, "symptom_history": symptom_history}
        st.download_button(
            label="Download JSON",
            data=json.dumps(full_history, indent=4),
            file_name="full_history.json",
            mime="application/json"
        )