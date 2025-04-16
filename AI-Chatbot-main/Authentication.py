import streamlit as st
import firebase_admin
from firebase_admin import credentials
import pyrebase

# Initialize Firebase app if not already initialized
if not firebase_admin._apps:
    try:
        firebase_config = dict(st.secrets["firebaseapp"])
        cred = credentials.Certificate(firebase_config)
        firebase_admin.initialize_app(cred)
    except Exception as e:
        st.error(f"Failed to initialize Firebase: {e}")

firebase = pyrebase.initialize_app(st.secrets["firebaseconfig"])
authentication = firebase.auth()

class Database:
    def __init__(self,user_id):
        self.db = firebase.database()
        self.user_id = user_id

    def chat_history(self):
        try:
            chat_history = self.db.child("users").child(self.user_id).child("chat_history").get().val()
                
            if chat_history is None:
                return []
            return chat_history
        
        except Exception as e:
            st.error(f"Error fetching chat history: {e}")
            return []  # Return an empty list on error

    def chat_history1(self):
        data = self.db.child("users").child(self.user_id).child("chat_history").get()
        return data.val()  # This returns a dict with push keys as keys

    
    def symptom_history(self):
        try:
            symptom_history = self.db.child("users").child(self.user_id).child("symptoms_history").get().val()
            if symptom_history is None:
                return []
            else:
                return symptom_history
        except Exception as e:
            st.error(f"Error fetching Symptom history: {e}")

    def save_chat_to_database(self,user_id, messages, symptoms, response):
        """Save chat history to Firebase Realtime Database."""
        try:
            if messages:
                chat_data = [
                    {
                        "role": msg.role,
                        "parts": [part.text for part in msg.parts]
                    }
                    for msg in messages
                ]
                # Write data to the user's chat history in Firebase
                self.db.child("users").child(user_id).child("chat_history").set(chat_data)
            elif symptoms and response:
                chat_data ={
                        "Question" : symptoms,
                        "Answer" : response 
                    }
                self.db.child("users").child(user_id).child("symptoms_history").push(chat_data)
        except Exception as e:
            st.error(f"Failed to save chat history: {e}")
    
    
class Authentication:
    def __init__(self):
        self.db = firebase.database()
        
    @staticmethod    
    def handle_auth_error(error_message):
        if "EMAIL_EXISTS" in error_message:
            return "This email is already registered. Please log in."
        elif "INVALID_EMAIL" in error_message:
            return "The email address is badly formatted. Please enter a valid email."
        elif "MISSING_EMAIL" in error_message:
            return "Email address is required. Please enter your email."
        elif "MISSING_PASSWORD" in error_message:
            return "Password is required. Please enter your password."
        elif "WEAK_PASSWORD" in error_message:
            return "The password is too weak. Please use at least 6 characters."
        elif "EMAIL_NOT_FOUND" in error_message or "USER_NOT_FOUND" in error_message:
            return "This email is not registered. Please sign up first."
        elif "INVALID_PASSWORD" in error_message:
            return "The password is incorrect. Please try again."
        elif "USER_DISABLED" in error_message:
            return "Your account has been disabled. Please contact support."
        elif "TOO_MANY_ATTEMPTS_TRY_LATER" in error_message:
            return "Too many unsuccessful attempts. Please try again later."
        elif "INVALID_API_KEY" in error_message or "API_KEY_EXPIRED" in error_message:
            return "Internal configuration error. Please contact support."
        elif "QUOTA_EXCEEDED" in error_message:
            return "Server is currently busy. Please try again later."
        elif "INVALID_LOGIN_CREDENTIALS" in error_message:
            return "Invalid email or password"
        else:
            return f"An error occurred: {error_message}"
            
    def sign_up(self,user_name,email,password):
        try:
            user = authentication.create_user_with_email_and_password(
                email=email, 
                password=password
            )
            user_id = user["localId"]
            
            user_data = {
                "user_name": user_name,
                "email": email,
            }
            self.db.child("users").child(user_id).set(user_data)
        except Exception as e:
            error_message = Authentication.handle_auth_error(str(e))
            st.error(error_message)    
                
    def login(self,email,password):
        try:
            user = authentication.sign_in_with_email_and_password(
                email=email,
                password=password
            )
            
            if user:
                st.success("Login successful!")
            
            user_id = user["localId"]

            user_data = self.db.child("users").child(user_id).get().val()
            
            if user_data:
                st.session_state["user_id"] = user_id
                st.session_state["user_name"] = user_data["user_name"]
                st.success(f"Welcome back, {user_data['user_name']}!")
            else:
                st.error("User data not found.")
                        
        except Exception as e:
            error_message = Authentication.handle_auth_error(str(e))
            st.error(error_message)
    
def logout():
    st.session_state.clear()
    st.success("Logged out successfully!")