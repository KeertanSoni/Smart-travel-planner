import streamlit as st
import os
import google.generativeai as genai
from dotenv import load_dotenv
from tools import search_flights, search_hotels, find_activities

# --- Agent Configuration ---
# Load environment variables from the .env file
load_dotenv()

# Configure the Gemini API with your key
api_key = os.getenv("GEMINI_API_KEY")
if not api_key:
    # In a deployed Streamlit app, you might use st.secrets instead
    st.error("GEMINI_API_KEY not found. Please set it in your .env file.")
else:
    genai.configure(api_key=api_key)

# Initialize the Gemini model and tell it about the available tools
model = genai.GenerativeModel(
    model_name="gemini-1.5-flash",
    tools=[search_flights, search_hotels, find_activities]
)

# --- Main App Logic ---

# Set up the Streamlit page title and a header
st.set_page_config(page_title="AI Travel Agent", page_icon="✈️")
st.title("🤖 Your Personal AI Travel Agent")
st.markdown("I can help you plan your next trip! Just tell me where you want to go.")

# Get the user's travel request from a text input box
prompt = st.text_input(
    "Enter your travel plans...",
    placeholder="e.g., A 5-day trip to Goa from Mumbai for 2 adults in December"
)

# If the user clicks the 'Plan My Trip' button
if st.button("Plan My Trip"):
    if prompt:
        # Show a loading spinner while the agent is working
        with st.spinner("🌍 Calling the travel APIs and building your itinerary... This may take a moment."):
            try:
                # Start a chat session with the model
                chat = model.start_chat(enable_automatic_function_calling=True)
                
                # Send the user's prompt to the model
                response = chat.send_message(prompt)
                
                # Display the agent's final response
                st.markdown(response.text)

            except Exception as e:
                # Show an error message if something goes wrong
                st.error(f"An error occurred: {e}")
    else:
        # Show a warning if the user didn't enter a prompt
        st.warning("Please enter your travel plans first.")