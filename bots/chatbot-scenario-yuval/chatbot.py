import json
import os
import sys
from openai import OpenAI
from dotenv import load_dotenv

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
extractor = Extractor(client)

class ChatBot:
    def __init__(self, tree_file=None):
        if tree_file is None:
            # Set the default path to the scenarios.json file within the current directory
            tree_file = os.path.join(os.path.dirname(__file__), 'scenarios.json')
                
        tree_builder = TreeBuilder(tree_file)
        self.state_machine = tree_builder.build_state_machine()  # State machine now contains the general system prompt

    def get_chat_response(self, user_message):
        current_node = self.state_machine.current_node
        # Include the general system prompt with the current node's system prompt
        combined_prompt = f"{self.state_machine.general_system_prompt} {current_node.system_prompt}"

        current_node.chat_history.append({"role": "user", "content": user_message})
        print(f'system: {combined_prompt}')
        
        # Generate a response from the AI model using the combined prompt
        response = client.chat.completions.create(
            model="gpt-4o",
            messages=[
                {"role": "system", "content": combined_prompt},
                *current_node.chat_history
            ],
            temperature=1,
            max_tokens=256,
            top_p=1,
            frequency_penalty=0,
            presence_penalty=0
        )

        chat_response = response.choices[0].message.content.strip()
        current_node.chat_history.append({"role": "assistant", "content": chat_response})

        # Pass the whole chat history to the extractor
        extracted_info = extractor.extract_info(
            user_message,
            chat_response,
            current_node.required_info,
            current_node.chat_history  # Passing the full chat history
        )

        self.state_machine.global_data_store.update(extracted_info)
        self.state_machine.transition_to_next_node()

        return chat_response

    def reset_chat_history(self):
        # Reset the chat history by rebuilding the state machine
        self.state_machine.clear_global_data_store()
        self.state_machine = self.build_state_machine()