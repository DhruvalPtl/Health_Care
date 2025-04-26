import streamlit as st
from PIL import Image
import google.generativeai as genai
from google.generativeai import protos  
try:
    from Authentication import Authentication, logout, Database
except ImportError: Authentication, logout, Database = None, None, None
try:
    from sidebar import render_sidebar # Import the updated function
except ImportError: render_sidebar = None
import os

script_dir = os.path.dirname(os.path.abspath(__file__))
icon_path = os.path.abspath(os.path.join(script_dir, "..", "icon", "icon.png"))
# --- Initialize Auth and DB ---
auth = Authentication() if Authentication else None
db = None # Initialize db to None
if Database and "user_id" in st.session_state:
    try:
        db = Database(st.session_state["user_id"]) # Assign db object if logged in
    except Exception as e:
        st.error(f"Chatbot: Failed to initialize database: {e}")
        
img = Image.open("icon/icon.png")
st.set_page_config(
    page_title="General Chatbot",
    page_icon=img,
    layout="wide",
)

auth = Authentication()
api_key = st.secrets["API_KEY"] 
# Initialize messages in session state

if "messages" not in st.session_state:
    st.session_state["messages"] = []

# Sidebar options with download buttons
if render_sidebar:
    try:
        # <<< Pass api_key and db object >>>
        model_name, max_length, stop_sequence = render_sidebar(api_key=api_key, db_connection=db)
    except Exception as e:
        st.sidebar.error(f"Error rendering sidebar: {e}")
else:
    st.sidebar.warning("Sidebar not available.")

# Set up generation configuration
generation_config = {
  "max_output_tokens": max_length,
  "stop_sequences": stop_sequence,
  "response_mime_type": "text/plain",
}

# Initialize chat in session state 
try:
    model = genai.GenerativeModel(model_name, generation_config=generation_config)
    st.session_state.chat = model.start_chat(history=st.session_state["messages"])
except Exception as e:
    st.error(f"Failed to initialize chat: {e}")

st.title("💬 General AI Chatbot")
st.caption("A Chatbot powered by Gemini")

st.chat_message("assistant").write("How can I help you?")

if "user_id" in st.session_state:
    user_id = st.session_state["user_id"]
    db = Database(user_id) 
    chat_history = db.get_chat_history()
    if chat_history:
            # Convert database entries to protos.Content structure
            st.session_state["messages"] = [
                protos.Content(
                    parts=[protos.Part(text=part) for part in msg["parts"]],
                    role=msg["role"]
                )
                for msg in chat_history
            ]
    else:
        st.session_state["messages"] = []

# Display chat messages
for msg in st.session_state.messages:
    # st.chat_message(msg["role"]).write(msg["parts"])
    role = "user" if msg.role == "user" else "assistant"
    st.chat_message(role).write("".join([part.text for part in msg.parts]))
    
if prompt := st.chat_input():
    # Append user input as a Content object with Part instance
    user_message = protos.Content(
        parts=[protos.Part(text=prompt)],
        role="user"
    )
    st.session_state["messages"].append(user_message)
    st.chat_message("user").write(prompt)
            
    if "chat" in st.session_state:
        try:
            # Send only the new user prompt to the chat object
            response = st.session_state.chat.send_message(prompt)

            # Append model response to session state for display
            model_message_proto = protos.Content(
                parts=[protos.Part(text=response.text)],
                role="model"
            )
            st.session_state["messages"].append(model_message_proto) # Append for immediate display
            st.chat_message("assistant").write(response.text) # Display immediately

            # --- Save updated history to DB (using overwrite method) ---
            if db and "user_id" in st.session_state:
                # Use chat object's history, which includes the latest turn
                saveable_history = [
                    {"role": msg.role, "parts": [part.text for part in msg.parts]}
                    for msg in st.session_state.chat.history # Get history directly from Gemini chat object
                ]
                # Call the save function (ensure db object is valid)
                db.save_chat_to_database(
                    user_id=st.session_state["user_id"],
                    messages=saveable_history, # Pass the full history list
                    symptoms=None,
                    response=None
                )
            elif "user_id" not in st.session_state:
                st.warning("Log in to save chat history.")
            # --- End Save ---

        except Exception as e:
            # Keep existing error handling (API key, quota, general)
            if "API_KEY_INVALID" in str(e):
                st.error("Invalid API key configured.")
            elif "429" in str(e):
                st.warning("Quota exceeded! Please wait or check API key usage.")
            else:
                st.error(f"An error occurred sending message: {e}")
    else:
        st.error("Chat session not initialized. Please refresh.")