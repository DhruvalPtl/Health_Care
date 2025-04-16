import streamlit as st 
from Authentication import sign_up

with st.form("Sign_up"):
    # Create form elements
    st.header("Sign up")
    username = st.text_input("Username")
    email = st.text_input("Email Address")
    password = st.text_input("Password", type="password")
    confirm_password = st.text_input("Confirm Password", type="password")
    submit_button = st.form_submit_button("Sign up")
    if submit_button:
        # Process form data
        if password == confirm_password:
            sign_up(username,email,confirm_password)
        else:
            st.error("Password do not match")