import streamlit as st
from PIL import Image
import google.generativeai as genai
from google.generativeai import protos
from Authentication import Authentication, logout, Database
import json
import pandas as pd
import time
from sidebar import render_sidebar

img = Image.open("icon/icon.png")
st.set_page_config(
    page_title="Medichat AI",
    page_icon=img,
    layout="wide",
)

auth = Authentication()
api_key = st.secrets["API_KEY"] 
# Initialize messages in session state

if "messages" not in st.session_state:
    st.session_state["messages"] = []

# Sidebar options with download buttons
model_name, max_length, stop_sequence = render_sidebar(api_key)

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

st.title("Medichat AI")
st.caption("A Chatbot powered by Gemini")

st.chat_message("assistant").write("How can I help you?")

if "user_id" in st.session_state:
    user_id = st.session_state["user_id"]
    db = Database(user_id)
    chat_history = db.chat_history()
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
            # Concatenate messages into a single string
            full_prompt = "\n".join([
                "".join([part.text for part in msg.parts])
                for msg in st.session_state.messages
            ])
            full_prompt += "\n" + prompt
            
            # Send the user message and get a response
            try:
                response = st.session_state.chat.send_message(full_prompt)
            # Create the assistant's response as a Content object with Part instance
                model_message = protos.Content(
                    parts=[protos.Part(text=response.text)],
                    role="model"
                )
                st.session_state["messages"].append(model_message)
                st.chat_message("assistant").write(response.text)
            except Exception as e:
                if "API_KEY_INVALID" in str(e):
                    st.error("Invalid API key")
                    
            if "user_id" in st.session_state:
                db.save_chat_to_database(st.session_state["user_id"], st.session_state["messages"],None,None)
            else:
                st.warning("Log in to save chat history.")
                
        except Exception as e:
            if "429" in str(e):
                st.warning("Quota exceeded! Please wait a few minutes or enter your own API key in the sidebar.")
            else:
                st.error(f"An error occurred: {e}")
    else:
            st.error("Failed to start chat message")