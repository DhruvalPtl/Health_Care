import os
import streamlit as st
import google.generativeai as genai

# Initialize the Gemini API
api_key = st.secrets["API_KEY"]
genai.configure(api_key=api_key)

with st.sidebar.expander("Output Control Parameter"):
    temp = st.slider("🌡Temperature", 0.0, 2.0, 1.0, 0.05)
    top_p = st.slider("Top P", 0.0, 1.0, 0.95, 0.05)
    top_k = st.slider("Top K", 0, 100, 30)
    max_length = st.number_input("Max Output Length", 1, 8192, 4096)
    stop_sequence_input = st.text_input("Stop Sequence", placeholder="e.g., Thank you!")
    stop_sequence = stop_sequence_input.split(",") if stop_sequence_input else []

# Define the generation configuration
generation_config = {
    "temperature": temp,
    "top_p": top_p,
    "top_k": top_k,
    "max_output_tokens": max_length,
    "stop_sequences": stop_sequence,
    "response_mime_type": "text/plain",
}
st.write(generation_config)

# Create the model
model = genai.GenerativeModel(
    model_name="gemini-1.5-flash",
    generation_config=generation_config,
)

# Initialize chat session if not already initialized
if "chat_session" not in st.session_state:
    st.session_state["chat_session"] = model.start_chat(
        history=[]
    )

# Initialize messages if not already in session_state
if "messages" not in st.session_state:
    st.session_state["messages"] = [
        {"role": "assistant", "text": "Hello there! How can I help you today?\n"}
    ]

# Display the chat interface
st.title("IntelliGemini")
st.caption("A chatbot powered by Google Gemini")

st.write(st.session_state["chat_session"])

# Display previous chat messages
for msg in st.session_state["messages"]:
    role = "user" if msg["role"] == "user" else "assistant"
    st.chat_message(role).write(msg["text"])

# Handle new user input
if user_input := st.chat_input("Type your message here..."):
    # Append the user's message to the messages history
    user_message = {"role": "user", "text": user_input}
    st.session_state["messages"].append(user_message)
    st.chat_message("user").write(user_input)

    # Send the message to the Gemini model and get the response
    try:
        # Send the user message and get the assistant's response
        response = st.session_state["chat_session"].send_message(user_input)
        
        # Append the assistant's response to the messages history
        assistant_message = {"role": "assistant", "text": response.text}
        st.session_state["messages"].append(assistant_message)
        st.chat_message("assistant").write(response.text)

    except Exception as e:
        st.error(f"An error occurred: {e}")

