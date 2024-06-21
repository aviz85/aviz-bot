import json
import os
import requests
from dotenv import load_dotenv

class ChatBot:
    def __init__(self, prompts_file=None):
        # Load environment variables from .env file if it exists
        load_dotenv()
        
        # Get the API key from the environment variable
        self.api_key = os.getenv('ANTHROPIC_API_KEY')
        
        if self.api_key is None:
            raise ValueError("ANTHROPIC_API_KEY not found in environment variables.")
        
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
            self.system_prompt = initial_prompt
        else:
            raise ValueError(f"Prompt with label '{self.initial_prompt_label}' not found in prompts.")

    def get_chat_response(self, user_message):
        try:
            # Add the user's message to the conversation history
            self.conversation_history.append({"role": "user", "content": user_message})
            
            response = requests.post(
                'https://api.anthropic.com/v1/messages',
                headers={
                    'x-api-key': self.api_key,
                    'anthropic-version': '2023-06-01',
                    'content-type': 'application/json'
                },
                json={
                    "model": "claude-3-5-sonnet-20240620",
                    "max_tokens": 256,
                    "system": self.system_prompt,
                    "messages": self.conversation_history
                }
            )

            response_data = response.json()
            
            # Debugging: Print the entire response data
            
            if 'content' in response_data and len(response_data['content']) > 0:
                chat_response = response_data['content'][0]['text'].strip()
            else:
                chat_response = "No valid response received from the API."
                print("Response Data:", json.dumps(response_data, indent=4))

            # Add the assistant's response to the conversation history
            self.conversation_history.append({"role": "assistant", "content": chat_response})
        
            return chat_response
        except Exception as e:
            # Debugging: Print the exception
            print("Exception:", str(e))
            return str(e)
    
    def reset_chat_history(self):
        self.conversation_history = []
        self.set_initial_prompt()

# Instantiate ChatBot
chatbot = ChatBot()
