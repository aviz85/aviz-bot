import json
import os
import sys
from openai import OpenAI
from dotenv import load_dotenv
import requests

# Add the bot directory to the system path
sys.path.append(os.path.dirname(__file__))

from scenario_builder import TreeBuilder, Node, StateMachine
from extractor import Extractor

# Load environment variables from .env file if it exists
load_dotenv()

# Get the API key from the environment variable
OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')
if OPENAI_API_KEY is None:
    raise ValueError("OPENAI_API_KEY not found in environment variables.")

client = OpenAI(api_key=OPENAI_API_KEY)

model_type = "openai"

extractor = Extractor(client)

class ChatBot:
    def __init__(self, tree_file=None):
        if tree_file is None:
            # Set the default path to the scenarios.json file within the current directory
            tree_file = os.path.join(os.path.dirname(__file__), 'scenarios.json')
            
        # Get the API key from the environment variable
        self.api_key = os.getenv('ANTHROPIC_API_KEY')
        
        if self.api_key is None:
            raise ValueError("ANTHROPIC_API_KEY not found in environment variables.")
  
                
        tree_builder = TreeBuilder(tree_file)
        self.state_machine = tree_builder.build_state_machine()  # State machine now contains the general system prompt

    def get_chat_response(self, user_message):
        current_node = self.state_machine.current_node
        
        current_node.chat_history.append({"role": "user", "content": user_message})

        # Pass only the current node's chat history to the extractor
        extracted_info = extractor.extract_info(
            user_message,
            "",
            current_node.required_info,
            current_node.chat_history  # Passing the current node's chat history
        )

        self.state_machine.global_data_store.update(extracted_info)
        
        # Transition to the next node before generating the next response
        self.state_machine.transition_to_next_node()
        
        # Update the current node after the transition
        current_node = self.state_machine.current_node
        
        # Include the general system prompt with the current node's system prompt
        combined_prompt = f"{self.state_machine.general_system_prompt} {current_node.system_prompt}"
        print(f'system: {combined_prompt}')
        
        try:
            # Add the user's message to the conversation history
            if model_type == "openai":
                # Using OpenAI
                response = client.chat.completions.create(
                    model="gpt-4o",
                    messages=[
                        {"role": "system", "content": combined_prompt},
                        *self.state_machine.global_chat_history()  # Using the entire chat history
                    ],
                    temperature=1,
                    max_tokens=256,
                    top_p=1,
                    frequency_penalty=0,
                    presence_penalty=0
                )
                chat_response = response.choices[0].message.content.strip()
            elif model_type == "anthropic":
                # Using Anthropic
                response = requests.post(
                    'https://api.anthropic.com/v1/messages',
                    headers={
                        'x-api-key': self.api_key,
                        'anthropic-version': '2023-06-01',
                        'content-type': 'application/json'
                    },
                    json={
                        "model": "claude-3-haiku-20240307",
                        "max_tokens": 256,
                        "system": combined_prompt,
                        "messages": self.state_machine.global_chat_history()
                    }
                )

                response_data = response.json()
                
                # Debugging: Print the entire response data
                if 'content' in response_data and len(response_data['content']) > 0:
                    chat_response = response_data['content'][0]['text'].strip()
                else:
                    chat_response = "No valid response received from the API."
                    print("Response Data:", json.dumps(response_data, indent=4))
            else:
                chat_response = "Invalid model_type specified."

            # Add the assistant's response to the conversation history
            current_node.chat_history.append({"role": "assistant", "content": chat_response})

            return chat_response
        except Exception as e:
            # Debugging: Print the exception
            print("Exception:", str(e))
            return str(e)

    def reset_chat_history(self):
        # Reset the chat history by rebuilding the state machine
        self.state_machine.clear_global_data_store()
        tree_builder = TreeBuilder(os.path.join(os.path.dirname(__file__), 'scenarios.json'))
        self.state_machine = tree_builder.build_state_machine()

# Additional method to get the entire chat history
def global_chat_history(self):
    history = []
    for node in self.nodes.values():  # Accessing self.nodes directly
        history.extend(node.chat_history)
    return history

# Adding the method to the StateMachine class
StateMachine.global_chat_history = global_chat_history
