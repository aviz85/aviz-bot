from openai import OpenAI
from dotenv import load_dotenv
import json, os

# Load environment variables from .env file if it exists
load_dotenv()

# Get the API key from the environment variable
OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')

if OPENAI_API_KEY is None:
    raise ValueError("OPENAI_API_KEY not found in environment variables.")

client = OpenAI(api_key=OPENAI_API_KEY)

class ChatBot:
    def __init__(self):

        self.conversation_history = []
                
    def get_chat_response(self, user_message, history):
        try:
            self.conversation_history = [{"role": msg["role"], "content": msg["content"]} for msg in history]
            self.conversation_history.append({"role": "user", "content": user_message})
            
            response = client.chat.completions.create(
                model="gpt-4o",
                messages=self.conversation_history,
                temperature=1,
                max_tokens=256,
                top_p=1,
                frequency_penalty=0,
                presence_penalty=0
            )

            # Access the response content correctly
            chat_response = response.choices[0].message.content.strip()
        
            # Add the assistant's response to the conversation history
            self.conversation_history.append({"role": "assistant", "content": chat_response})
        
            return chat_response
        except Exception as e:
            return str(e)
    
    def reset_chat_history(self):
        self.conversation_history = []

# Instantiate ChatBot
chatbot = ChatBot()
