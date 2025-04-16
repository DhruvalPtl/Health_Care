import streamlit as st 
from Authentication import login

with st.sidebar.popover("Open popover",use_container_width=False):
    with st.form("Sign_up"):
        # Create form elements
        st.header("Login")
        email = st.text_input("Email Address")
        password = st.text_input("Password", type="password")
        submit_button = st.form_submit_button("Sign up")
        if submit_button:
            # Process form data
            if password:
                login(email,password)
            else:
                st.error("Password do not match")