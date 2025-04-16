# sign_up.py
import streamlit as st

def run():
    # Sign-up logic
    st.header("Sign Up")
    
    username = st.text_input("Create Username")
    password = st.text_input("Create Password", type="password")
    confirm_password = st.text_input("Confirm Password", type="password")
    
    if st.button("Sign Up"):
        if password == confirm_password:
            # Simulating a successful sign-up
            st.success("Account created successfully!")
        else:
            st.error("Passwords do not match. Please try again.")
