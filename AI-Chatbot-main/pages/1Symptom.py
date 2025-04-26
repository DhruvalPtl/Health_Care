# --- Polished Symptom Information Tool Code ---

import streamlit as st
import google.generativeai as genai
import datetime
# --- Import your custom modules ---
try:
    from Authentication import Database # Assuming this class exists
except ImportError:
    st.error("Authentication.py not found or Database class missing.")
    Database = None # Define as None if import fails
    db = None
    user_id = None

# --- Initialize Database and User ---
db = None
user_id = None
if "user_id" in st.session_state:
    user_id = st.session_state["user_id"]
    if Database: # Only try to instantiate if class was imported
        try:
            db = Database(user_id)
        except Exception as e:
            st.error(f"Failed to initialize database connection: {e}")
            db = None
    else:
        st.error("Database functionality is unavailable due to import error.")
else:
    st.info("ℹ️ Please log in to use this feature and save your interaction history.")


# --- Configure Gemini API ---
# --- CORRECTED SECTION: Using st.secrets ---
try:
    # Assumes .streamlit/secrets.toml has:
    # API_KEY = "YOUR_NEW_SECURE_GEMINI_API_KEY"
    # If your key is under a section like [GEMINI], use st.secrets["GEMINI"]["API_KEY"]
    api_key = st.secrets["API_KEY"]
    genai.configure(api_key=api_key)
    model = genai.GenerativeModel('gemini-2.5-flash-preview-04-17')
    st.sidebar.success("Gemini API Configured ✓") # Optional: Indicate success
except KeyError:
    st.error("❗️ Gemini API Key not found in Streamlit Secrets (secrets.toml). Please configure it.")
    st.stop()
except Exception as e:
    st.error(f"❗️ Error configuring Gemini API: {e}")
    st.stop()

with st.sidebar:
    st.markdown("---") # Separator after main sidebar content
    st.warning("**Reminder:** Educational tool only. Consult a doctor.") # Example: Disclaimer
    st.page_link("pages/4History.py", label="View Symptom History", icon="📜") # Example: Link
    if st.button("Reset Current Check", key="sidebar_reset"): # Example: Reset Button
         # Reset logic here...
         keys_to_clear = ["interaction_stage", "conversation_data", "ai_follow_up_question", "generated_summary", "db_save_error"]
         for key in keys_to_clear:
             if key in st.session_state: del st.session_state[key]
         st.rerun()

# --- Main Page Content ---
st.title("🧑‍⚕️ Symptom Information Assistant")
st.caption("An educational tool to provide general information based on symptoms.")

# --- CRITICAL DISCLAIMERS (Keep Prominent) ---
st.error(
    """
    **IMPORTANT:** This is **NOT** a diagnostic tool or a substitute for a doctor.
    It provides general information for educational purposes ONLY.
    **ALWAYS consult a qualified healthcare professional for medical advice.**
    """
)

# --- Initialize Session State (Cleaner Names) ---
if "interaction_stage" not in st.session_state:
    st.session_state.interaction_stage = "initial_input" # Stages: initial_input, awaiting_follow_up, generating_summary, display_summary
if "conversation_data" not in st.session_state:
    st.session_state.conversation_data = {"history": []} # Store conversation history
if "ai_follow_up_question" not in st.session_state:
    st.session_state.ai_follow_up_question = None
if "generated_summary" not in st.session_state:
    st.session_state.generated_summary = None
if "db_save_error" not in st.session_state:
     st.session_state.db_save_error = None


# --- Interaction Flow ---

# 1. Initial Input Stage
if st.session_state.interaction_stage == "initial_input":
    st.markdown("Tell me about the main symptoms, how long they've lasted, and any other details you think are relevant.")
    initial_description = st.text_area("Describe your symptoms here:", key="initial_desc_area", height=150, placeholder="e.g., I've had a dry cough and headache for 3 days...")

    if st.button("▶️ Submit Information", key="submit_initial") and initial_description:
        st.session_state.conversation_data["initial_input"] = initial_description
        st.session_state.conversation_data["history"].append({"role": "User", "text": initial_description})

        # --- AI Call 1: Decide if follow-up is needed ---
        with st.spinner("Analyzing..."):
            # (Keep the same prompt_for_question as in the previous polished example)
            prompt_for_question = f"""
            Analyze the user's description: "{initial_description}"
            Is ONE simple, open-ended, non-diagnostic follow-up question needed to get more context for a general educational summary later?
            Examples of good questions: "Are there any other symptoms?", "Can you describe the sensation?" this is only example you can ask out of this two.
            MUST be non-diagnostic.
            Respond ONLY with the question text, or the exact token `[NO_QUESTION_NEEDED]`.
            """
            try:
                response = model.generate_content(prompt_for_question)
                response_text = response.text.strip()

                if response_text == "[NO_QUESTION_NEEDED]" or not response_text or len(response_text) > 150: # Basic check for reasonable question length
                    st.session_state.ai_follow_up_question = None
                    st.session_state.interaction_stage = "generating_summary"
                else:
                    st.session_state.ai_follow_up_question = response_text.strip('"')
                    st.session_state.interaction_stage = "awaiting_follow_up"

                st.rerun()

            except Exception as e:
                st.error(f"❗️ Error during analysis: {e}")
                st.session_state.ai_follow_up_question = None
                st.session_state.interaction_stage = "generating_summary"
                st.button("🔄 Try Proceeding Anyway", on_click=lambda: st.session_state.update(interaction_stage="generating_summary"))


# 2. Awaiting Follow-up Answer Stage
elif st.session_state.interaction_stage == "awaiting_follow_up":
    if st.session_state.ai_follow_up_question:
        st.info(f"🤖 **AI asks:** {st.session_state.ai_follow_up_question}")
        follow_up_answer = st.text_input("Your answer:", key="follow_up_answer_input", placeholder="Provide a brief answer...")

        if st.button("➡️ Submit Answer & Get Summary", key="submit_follow_up") and follow_up_answer:
            st.session_state.conversation_data["follow_up_question"] = st.session_state.ai_follow_up_question
            st.session_state.conversation_data["follow_up_answer"] = follow_up_answer
            st.session_state.conversation_data["history"].append({"role": "AI", "text": st.session_state.ai_follow_up_question})
            st.session_state.conversation_data["history"].append({"role": "User", "text": follow_up_answer})
            st.session_state.interaction_stage = "generating_summary"
            st.rerun()
    else:
        st.warning("Something went wrong. Resetting input.")
        st.session_state.interaction_stage = "initial_input"
        st.rerun()


# 3. Generating Summary Stage
elif st.session_state.interaction_stage == "generating_summary":
    st.info("⏳ Generating your educational summary...")
    with st.spinner("AI is working..."):
        # --- Prepare FINAL Safe Prompt ---
        # (Keep the same final_prompt as in the previous polished example)
        details = st.session_state.conversation_data
        context = f"User initial input: {details.get('initial_input', 'N/A')}"
        if 'follow_up_answer' in details:
            context += f"\nAI question: {details.get('follow_up_question', 'N/A')}\nUser answer: {details.get('follow_up_answer', 'N/A')}"

        final_prompt = f"""
        Role: AI educational assistant (NOT a doctor).
        User Context: {context}
        Task: Based ONLY on the user context, provide a brief, general educational summary.
        Instructions:
        1. Briefly acknowledge main symptoms/duration mentioned.
        2. Mention general info/advice TYPICALLY found on reputable health sites for these symptom TYPES (e.g., home care guidance, when to seek attention). Focus on systems or general processes. DO NOT list specific diseases/causes.
        3. Provide links to symptoms pages if available of NHS (https://www.nhs.uk/) and CDC (https://www.cdc.gov/) if not than provide main page link.
        4. STRONGLY emphasize this is NOT medical advice and to consult a healthcare professional.
        5. Be concise.
        Output ONLY the summary.
        """
        try:
            response = model.generate_content(final_prompt)
            st.session_state.generated_summary = response.text
            st.session_state.conversation_data["history"].append({"role": "AI", "text": f"Summary: {response.text}"})
            st.session_state.interaction_stage = "display_summary"

            # --- Save Interaction to Database ---
            if db and user_id:
             try:
                 timestamp = datetime.datetime.now().isoformat() # Keep timestamp for potential sorting later if needed
                 # Prepare data for the existing save method
                 # We'll save the initial input as 'symptoms' and summary as 'response'
                 # You could also format follow-up Q&A into the 'response' string if desired
                 initial_input_to_save = st.session_state.conversation_data.get('initial_input', 'N/A')
                 summary_to_save = st.session_state.generated_summary

                 # Use the method from Authentication.py
                 # Pass None for messages, pass key info to symptoms/response args
                 db.save_chat_to_database(
                     user_id=user_id,
                     messages=None, # Not saving general chat messages here
                     symptoms=f"Input: {initial_input_to_save}", # Or format better
                     response=summary_to_save
                 )
             except Exception as e:
                 st.session_state.db_save_error = f"Could not save interaction to history: {e}"

            st.rerun()

        except Exception as e:
            st.error(f"❗️ Failed to generate final summary: {e}")
            st.session_state.generated_summary = "Error: Could not generate summary."
            st.session_state.interaction_stage = "display_summary"
            st.rerun()


# 4. Display Summary Stage
elif st.session_state.interaction_stage == "display_summary":

    st.subheader("✅ Educational Information Summary")

    # Display DB save status (success or error)
    if st.session_state.db_save_error:
        st.warning(f"⚠️ {st.session_state.db_save_error}")
    elif db and user_id:
        st.success("💾 Interaction saved to your history.")

    with st.expander("Click to view the AI-generated summary", expanded=True):
        if st.session_state.generated_summary:
            st.markdown(st.session_state.generated_summary)
        else:
            st.error("Could not retrieve summary.")

        st.error(
            "**Reminder:** This AI-generated information is **NOT** medical advice. "
            "**Consult a healthcare professional.**"
        )

    if st.button("🔄 Start New Check", key="start_over"):
        keys_to_clear = ["interaction_stage", "conversation_data", "ai_follow_up_question", "generated_summary", "db_save_error"]
        for key in keys_to_clear:
            if key in st.session_state:
                del st.session_state[key]
        st.rerun()