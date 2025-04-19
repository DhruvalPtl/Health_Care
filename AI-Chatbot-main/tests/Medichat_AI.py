import streamlit as st
from PIL import Image
import google.generativeai as genai
from google.generativeai import protos
# from Authentication import Authentication, logout, Database
import json
import pandas as pd
import time

img = Image.open("icon/icon.png")
st.set_page_config(
    page_title="Medichat AI",
    page_icon=img,
    layout="wide",
)

# auth = Authentication()
# api_key = st.secrets["API_KEY"]
api_key = "AIzaSyCJUg1gHTskBBY-v0oaYvvMyKUF5z2-lZ0" 
# Initialize messages in session state

if "messages" not in st.session_state:
    st.session_state["messages"] = []

# Sidebar options with download buttons
with st.sidebar:
    
    # if "user_id" not in st.session_state:
    #     with st.expander("Sign Up"):  
    #         username = st.text_input("Username",value="",placeholder="yourname")
    #         email = st.text_input("Email Address",placeholder="abc@example.com",value="")
    #         password = st.text_input("Password", type="password",placeholder="Must 6 Character long",value="")
    #         confirm_password = st.text_input("Confirm Password", type="password",placeholder="Must 6 Character long",value="")
    #         if st.button("Sign up"):
    #             # Process form data
    #             if not username:
    #                 st.error("Please enter a username")
    #             elif not email or "@" not in email or ".com" not in email:
    #                 st.error("Enter email with valid format")
    #             elif not password or len(password) < 6:
    #                 st.error("Enter 6 or more character password")
    #             elif password == confirm_password:
    #                 auth.sign_up(username,email,confirm_password)
    #                 st.success("Sign Up successfully! Login to continue")
    #             else:
    #                 st.error("Password do not match")
                
    #     with st.expander("Login"):
    #         email = st.text_input("Your Email")
    #         password = st.text_input("Your Password", type="password")
    #         if st.button("Login"):
    #             # Process form data
    #             if not email or  ("@" and ".com" not in email) :
    #                 st.error("Enter email with valid format")
    #             elif not password or len(password) < 6:
    #                 st.error("Enter 6 or more character password")
    #             elif password:
    #                 auth.login(email,password)
    #                 time.sleep(2)
    #                 st.rerun()
    #             else:
    #                 st.error("Enter Email and Password")
    # else:
    #     st.subheader(st.session_state["user_name"])
    #     if st.button("Logout"):
    #         logout()
    #         for key in list(st.session_state.keys()):
    #             del st.session_state[key]
    #         st.rerun()
        
    
    st.markdown("## Medichat AI")
    st.markdown("""
                
    **Welcome to IntelliGemini!**

    Explore Gemini language models, adjust settings, and manage chat history.  
    *Happy chatting!*
    """)

    user_api_key = st.text_input("Enter your Gemini API key",type="password")
    if user_api_key:
            genai.configure(api_key=user_api_key)
    elif api_key:
            genai.configure(api_key=api_key)
            st.warning(
                "✅ The API key has been provided by the developer.\n\n"
                "🔒Note: Chat functionality is currently limited.\n\n"
                "You can get your Gemini API Key [here](https://aistudio.google.com/app/apikey)"
            )
   
    tool = st.toggle("Code Execution Tool",False)
    if tool:
        st.write("Code Execution Tool is now active. it enables the model to generate and run Python code")
        tools = "code_execution"
    else:
        tools = None
        
    model_name = st.selectbox("Choose a gemini Model",("gemini-1.5-flash","gemini-1.5-flash-8b","gemini-1.5-pro"))
    with st.expander("Output Control Parameter"):
        temp = st.slider("🌡Temperature",0.0,2.0,1.0,0.05)
        top_p = st.slider("Top P",0.0,1.0,.95,.05)
        top_k = st.slider("Top K",0,100,30)
        max_length = st.number_input("Max Output Length",1,8192,4096)
        stop_sequence_input = st.text_input("Stop Sequence", placeholder="e.g., Thank you!")
        stop_sequence = stop_sequence_input.split(",") if stop_sequence_input else []

    # Download Chat
    with st.expander("Download Chat"):
        if st.session_state["messages"]:
            
            def content_to_dict(content_obj):
                if isinstance(content_obj, dict):
                    return content_obj  
                return {
                    "role": content_obj.role,
                    "parts": [part.text for part in content_obj.parts],
                }

            download_message = [content_to_dict(msg) for msg in st.session_state["messages"]]
            
            json_data = json.dumps(download_message, indent=4)

            # json_data = json.dumps(st.session_state["messages"], indent=4)
            st.download_button("As JSON Format", json_data, file_name="chat_history.json", mime="application/json")
                
            # CSV download button
            df = pd.DataFrame(download_message)
            csv_data = df.to_csv(index=False)
            st.download_button("As CSV Format", csv_data, file_name="chat_history.csv", mime="text/csv")

    if st.button("Clear Chat"):
        st.session_state["messages"] = []
        st.rerun() 
        
# Set up generation configuration
generation_config = {
  "temperature": temp,
  "top_p": top_p,
  "top_k": top_k,
  "max_output_tokens": max_length,
  "stop_sequences": stop_sequence,
  "response_mime_type": "text/plain",
}

# Initialize chat in session state 
try:
    model = genai.GenerativeModel(model_name, generation_config=generation_config, tools=tools)
    st.session_state.chat = model.start_chat(history=st.session_state["messages"])
except Exception as e:
    st.error(f"Failed to initialize chat: {e}")

st.title("IntelliGemini")
st.caption("A Chatbot powered by Gemini")

st.chat_message("assistant").write("How can I help you?")

if "user_id" in st.session_state:
    user_id = st.session_state["user_id"]
    # db = Database(user_id)
    # chat_history = db.chat_history()
    # if chat_history:
    #         # Convert database entries to protos.Content structure
    #         st.session_state["messages"] = [
    #             protos.Content(
    #                 parts=[protos.Part(text=part) for part in msg["parts"]],
    #                 role=msg["role"]
    #             )
    #             for msg in chat_history
    #         ]
    # else:
    #     st.session_state["messages"] = []

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
                    
            # if "user_id" in st.session_state:
            #     db.save_chat_to_database(st.session_state["user_id"], st.session_state["messages"])
            # else:
            #     st.warning("Log in to save chat history.")
                
        except Exception as e:
            if "429" in str(e):
                st.warning("Quota exceeded! Please wait a few minutes or enter your own API key in the sidebar.")
            else:
                st.error(f"An error occurred: {e}")
    else:
            st.error("Failed to start chat message")