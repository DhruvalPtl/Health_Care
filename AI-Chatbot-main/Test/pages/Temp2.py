import streamlit as st
import streamlit_authenticator as stauth

# Step 1: Define users and credentials (hashed passwords)
credentials = {
    "usernames": {
        "jsmith": {
            "name": "John Smith",
            "email": "abc",
            "password": "1234"  # Hash the password
        },
        "rbriggs": {
            "name": "Rebecca Briggs",
            "email": "rbriggs@gmail.com",
            "password":  "123" # Hash the password
        }
    }
}

# Step 2: Initialize authenticator
authenticator = stauth.Authenticate(
    credentials=credentials,
    cookie_name="auth",  # Name of the cookie for authentication
    cookie_expiry_days=30  # Expiry for the authentication cookie
)

# Step 3: Login widget
st.title("Login Page")
authentication_status= authenticator.login("main")

# Step 4: Handle authentication status
if authentication_status:
    authenticator.logout("main")  # Show logout button
    st.write(f"Welcome *Dhruval*!")
    st.title("You are logged in!")
elif authentication_status is False:
    st.error("Username/password is incorrect")
elif authentication_status is None:
    st.warning("Please enter your username and password")
