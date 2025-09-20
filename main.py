import os
import google.generativeai as genai
from dotenv import load_dotenv
from tools import search_flights, search_hotels, find_activities

# Load environment variables from the .env file
load_dotenv()

# Configure the Gemini API with your key
print("Configuring the Gemini API key...")
api_key = os.getenv("GEMINI_API_KEY")
if not api_key:
    raise ValueError("GEMINI_API_KEY not found. Please set it in your .env file.")
genai.configure(api_key=api_key)
print("Gemini API key configured successfully.")

# Initialize the Gemini model and tell it about the available tools
print("Initializing the Gemini model with tools...")
model = genai.GenerativeModel(
    model_name="gemini-1.5-flash",
    tools=[search_flights, search_hotels, find_activities])
print("Model initialized.")

# Start a chat session with automatic function calling enabled
print("Starting chat session...")
chat = model.start_chat(enable_automatic_function_calling=True)
print("Chat session started.")

# Define the user's detailed request
prompt = "I want to plan a 5-day trip to Goa from Mumbai for 2 adults in December. I am interested in beaches and local food."
# Send the user's request to the model
print(f"\nSending prompt: '{prompt}'")
print("-" * 30)
response = chat.send_message(prompt)

# Print the final, user-friendly response
print("-" * 30)
print("AGENT'S FINAL RESPONSE:")
print(response.text)