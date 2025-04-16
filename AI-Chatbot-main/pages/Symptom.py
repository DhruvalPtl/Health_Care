import streamlit as st
import google.generativeai as genai
from sidebar import render_sidebar
from Authentication import Database

if "user_id" in st.session_state:
    user_id = st.session_state["user_id"]
    db = Database(user_id)
# Replace with your Google Gemini API Key
api_key = "AIzaSyCJUg1gHTskBBY-v0oaYvvMyKUF5z2-lZ0"

# Configure Gemini API
genai.configure(api_key=api_key)

# Sidebar options with download buttons
model_name, max_length, stop_sequence = render_sidebar(api_key)

st.title("🩺 MediChat - Symptom Checker")
st.write("Enter your symptoms and get AI-based preliminary diagnoses.")

symptoms = st.text_area("Describe your symptoms (e.g., fever, cough, headache)")

if st.button("Check Symptoms"):
    if symptoms:
        model = genai.GenerativeModel("gemini-1.5-pro")
        prompt = f"""
        You are an AI medical assistant. A user is experiencing the following symptoms: {symptoms}.
       1️⃣ Provide **3-5 possible medical conditions** that could match these symptoms.
        2️⃣ Give a **short explanation** for each condition.
        3️⃣ If the symptoms seem severe, recommend seeking medical attention.
        4️⃣ Also provide advice on what to do.
        5️⃣ Format the response with bullet points.
        """
        response = model.generate_content(prompt)
        response = response.text

        if response:
            st.subheader("🩺 Possible Conditions:")
            st.markdown(response)
            if "user_id" in st.session_state:
                db.save_chat_to_database(st.session_state["user_id"],None,symptoms, response)
            else:
                st.warning("Log in to save chat history.")    
        else:
             st.error("No response from AI. Try again.")
    else:
        st.warning("⚠️ Please enter your symptoms.")
