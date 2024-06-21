import os
import json
from pathlib import Path
# import logging
# from openai import client  # Make sure to install the openai package

class BaseChatBot:
    def __init__(self, prompts_file=None):
        if prompts_file is None:
            chatbot_name = os.getenv('CHATBOT_NAME', 'chatbot')            
            prompts_file = (Path(__file__).parent / '../' / f"{chatbot_name}/prompts.json").resolve()
            
        with open(prompts_file, 'r') as f:
            prompts_data = json.load(f)
        self.prompts = prompts_data["prompts"]
        self.conversation_history = []
        
        # Set the initial prompt label
        self.initial_prompt_label = "sarcastic_friend"  # Specify the label of the chosen prompt
        
        # Define the constant for the uploads folder
        self.upload_folder = (Path(__file__).parent / '../' / f"{chatbot_name}/uploads").resolve()
        
        # Initialize conversation history with the initial system prompt
        self.set_initial_prompt()

    def set_initial_prompt(self):
        initial_prompt = next((prompt["prompt"] for prompt in self.prompts if prompt["label"] == self.initial_prompt_label), None)
        if initial_prompt:
            self.conversation_history.append({"role": "system", "content": initial_prompt})
        else:
            raise ValueError(f"Prompt with label '{self.initial_prompt_label}' not found in prompts.")

    def get_chat_response(self, user_message):        
        print(user_message)
        # Additional initialization if needed
    
    def reset_chat_history(self):
        self.conversation_history = []
        self.set_initial_prompt()
