import streamlit as st

# Simulated database of users
USER_DB = {
    "123": "123",  # Username: Password
    "rbriggs": "securepass"
}

# Session state to track login status
if "logged_in" not in st.session_state:
    st.session_state["logged_in"] = False
if "current_user" not in st.session_state:
    st.session_state["current_user"] = None


def login(username, password):
    """Authenticate user against the simulated database."""
    if username in USER_DB and USER_DB[username] == password:
        st.session_state["logged_in"] = True
        st.session_state["current_user"] = username
        st.success(f"Welcome, {username}!")
    else:
        st.error("Invalid username or password. Please try again.")


def logout():
    """Log out the current user."""
    st.session_state["logged_in"] = False
    st.session_state["current_user"] = None
    st.info("You have been logged out.")


# Main application logic
with st.form("Login"):
    if not st.session_state["logged_in"]:
        # Login form
        st.header("Login")
        username = st.text_input("Username", key="login_username")
        password = st.text_input("Password", type="password", key="login_password")
        submitted = st.form_submit_button("Login")
        if submitted:
            login(username, password)
            st.switch_page("D:\Python\project-5\AI-Chatbot\pages\Temp2.py")
            # st.page_link("D:\Python\project-5\AI-Chatbot\pages\pages\demp1.py", label="Second")
    
    else:
        # Welcome screen after login
        st.title(f"Welcome, {st.session_state['current_user']}!")
        st.write("You are now logged in.")
        submitted = st.form_submit_button("Logout")
        if submitted:
            logout()
    