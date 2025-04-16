import streamlit as st
import google.generativeai as genai
from google.generativeai import protos
import firebase_admin
from firebase_admin import credentials
import pyrebase
import json

# Firebase Initialization
if not firebase_admin._apps:
    try:
        cred = credentials.Certificate("D:\Python\project-5\AI-Chatbot\intelligemini.json")
        firebase_admin.initialize_app(cred)
    except Exception as e:
        st.error(f"Failed to initialize Firebase: {e}")
with open("D:\Python\project-5\AI-Chatbot\Firebaseconfig.json") as config:
    firebaseConfig = json.loads(config)

firebase = pyrebase.initialize_app(firebaseConfig)
authentication = firebase.auth()
db = firebase.database()

# API Key for IntelliGemini
api_key = st.secrets["API_KEY"]

# Initialize chat session state
if "messages" not in st.session_state:
    initial_message = protos.Content(
        parts=[protos.Part(text="How can I help you?")], role="model"
    )
    st.session_state["messages"] = [initial_message]

# User Authentication Functions
def sign_up(user_name, email, password):
    try:
        user = authentication.create_user_with_email_and_password(email, password)
        user_id = user["localId"]
        user_data = {"user_name": user_name, "email": email}
        db.child("users").child(user_id).set(user_data)
        st.success("Sign Up successful!")
    except Exception as e:
        st.error(f"An error occurred during sign-up: {e}")

def login(email, password):
    try:
        user = authentication.sign_in_with_email_and_password(email, password)
        user_id = user["localId"]
        user_data = db.child("users").child(user_id).get().val()
        if user_data:
            st.session_state["user_id"] = user_id
            st.session_state["user_name"] = user_data["user_name"]
            st.success(f"Welcome back, {user_data['user_name']}!")
        else:
            st.error("User data not found.")
    except Exception as e:
        st.error("Invalid login credentials. Please check your email or password.")

def logout():
    st.session_state.clear()
    st.success("Logged out successfully!")

# Sidebar for Authentication and IntelliGemini Settings
with st.sidebar:
    st.markdown("## IntelliGemini")
    st.markdown("**Welcome to IntelliGemini!** Explore and manage your chat experience.")
    
    if "user_id" not in st.session_state:
        st.subheader("Sign Up")
        sign_up_name = st.text_input("Full Name")
        sign_up_email = st.text_input("Email Address")
        sign_up_password = st.text_input("Password", type="password")
        if st.button("Sign Up"):
            sign_up(sign_up_name, sign_up_email, sign_up_password)

        st.subheader("Login")
        login_email = st.text_input("Login Email Address", key="login_email")
        login_password = st.text_input("Login Password", type="password", key="login_password")
        if st.button("Login"):
            login(login_email, login_password)
    else:
        st.success(f"Logged in as {st.session_state['user_name']}")
        if st.button("Logout"):
            logout()

    # Gemini API Key Configuration
    user_api_key = st.text_input("Enter your Gemini API key", type="password")
    if user_api_key:
        genai.configure(api_key=user_api_key)
    elif api_key:
        genai.configure(api_key=api_key)
        st.info("✅ API key is provided by the developer")
    else:
        st.error("Please enter your API key.")

    # Chat Settings
    model_name = st.selectbox("Choose a Gemini Model", ["gemini-1.5-flash", "gemini-1.5-flash-8b", "gemini-1.5-pro"])
    temp = st.slider("🌡 Temperature", 0.0, 2.0, 1.0, 0.05)
    max_length = st.number_input("Max Output Length", 1, 8192, 4096)

# Main IntelliGemini Chat Interface
st.title("IntelliGemini")
st.caption("A Chatbot powered by Gemini and Firebase")

if "user_id" in st.session_state:
    # Load previous chat history for the user
    chat_history = db.child("users").child(st.session_state["user_id"]).child("chat_history").get().val()
    if chat_history:
        st.session_state["messages"] = [protos.Content(**msg) for msg in chat_history]

    # Display chat messages
    for msg in st.session_state["messages"]:
        role = "user" if msg.role == "user" else "assistant"
        st.chat_message(role).write("".join(part.text for part in msg.parts))

    # User input and chatbot response
    if prompt := st.chat_input():
        user_message = protos.Content(parts=[protos.Part(text=prompt)], role="user")
        st.session_state["messages"].append(user_message)
        st.chat_message("user").write(prompt)

        try:
            model = genai.GenerativeModel(model_name)
            chat = model.start_chat(history=st.session_state["messages"])
            response = chat.send_message(prompt)
            model_message = protos.Content(parts=[protos.Part(text=response.text)], role="model")
            st.session_state["messages"].append(model_message)
            st.chat_message("assistant").write(response.text)
        except Exception as e:
            st.error(f"Error generating response: {e}")

        # Save chat history to Firebase
        db.child("users").child(st.session_state["user_id"]).child("chat_history").set(
            [msg.to_dict() for msg in st.session_state["messages"]]
        )
else:
    st.warning("Please log in to start chatting.")
