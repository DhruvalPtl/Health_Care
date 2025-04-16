import streamlit as st
import firebase_admin
from firebase_admin import credentials, auth, firestore
import bcrypt


st.title("User Authentication")

# # Firebase Admin SDK Initialization
# cred = credentials.Certificate("D:\Python\project-5\AI-Chatbot\intelligemini.json")
# firebase_admin.initialize_app(cred)
# db = firestore.client()

# # Hash password using bcrypt
# def hash_password(password):
#     return bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())

# # Verify hashed password
# def verify_password(password, hashed):
#     return bcrypt.checkpw(password.encode('utf-8'), hashed)

# # Store user details in Firestore
# def store_user(email, password_hash):
#     users_ref = db.collection("users")
#     users_ref.document(email).set({
#         "email": email,
#         "password": password_hash.decode('utf-8')  # Decode to store as a string
#     })

# # Authenticate user
# def authenticate_user(email, password):
#     users_ref = db.collection("users")
#     user_doc = users_ref.document(email).get()
#     if user_doc.exists:
#         user_data = user_doc.to_dict()
#         if verify_password(password, user_data["password"].encode('utf-8')):
#             return True
#     return False

# # Streamlit UI
# st.title("User Authentication")

# menu = st.sidebar.selectbox("Menu", ["Signup", "Login"])

# if menu == "Signup":
#     st.subheader("Signup")
#     email = st.text_input("Email")
#     password = st.text_input("Password", type="password")
#     if st.button("Sign Up"):
#         if email and password:
#             password_hash = hash_password(password)
#             try:
#                 store_user(email, password_hash)
#                 st.success("User registered successfully!")
#             except Exception as e:
#                 st.error(f"Error: {e}")
#         else:
#             st.error("Please provide both email and password.")

# elif menu == "Login":
#     st.subheader("Login")
#     email = st.text_input("Email")
#     password = st.text_input("Password", type="password")
#     if st.button("Log In"):
#         if email and password:
#             if authenticate_user(email, password):
#                 st.success("Login successful!")
#             else:
#                 st.error("Invalid email or password.")
#         else:
#             st.error("Please provide both email and password.")
