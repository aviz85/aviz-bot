from groq import Groq
from dotenv import load_dotenv
import json, os

# Load environment variables from .env file if it exists
load_dotenv()

# Get the API key from the environment variable
GROQ_API_KEY = os.getenv('GROQ_API_KEY')

if GROQ_API_KEY is None:
    raise ValueError("GROQ_API_KEY not found in environment variables.")

client = Groq(api_key=GROQ_API_KEY)

class ChatBot:
    def __init__(self, prompts_file=None):
        if prompts_file is None:
            # Set the default path to the prompts.json file within the current directory
            prompts_file = os.path.join(os.path.dirname(__file__), 'prompts.json')
        
        with open(prompts_file, 'r') as f:
            prompts_data = json.load(f)
        self.prompts = prompts_data["prompts"]
        self.conversation_history = []
        
        # Set the initial prompt label
        self.initial_prompt_label = "sarcastic_friend"  # Specify the label of the chosen prompt
        
        # Initialize conversation history with the initial system prompt
        self.set_initial_prompt()

    def set_initial_prompt(self):
        initial_prompt = next((prompt["prompt"] for prompt in self.prompts if prompt["label"] == self.initial_prompt_label), None)
        if initial_prompt:
            self.conversation_history.append({"role": "system", "content": initial_prompt})
        else:
            raise ValueError(f"Prompt with label '{self.initial_prompt_label}' not found in prompts.")

    def get_chat_response(self, user_message):
        try:
            # Add the user's message to the conversation history
            self.conversation_history.append({"role": "user", "content": user_message})
            
            response = client.chat.completions.create(
                messages=self.conversation_history,
                model="llama3-70b-8192",
                temperature=1,
                max_tokens=1024,
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
        self.set_initial_prompt()

# Instantiate ChatBot
chatbot = ChatBot()
