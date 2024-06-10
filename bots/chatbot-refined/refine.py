import os, json
import requests
from dotenv import load_dotenv

# Load environment variables from .env file if it exists
load_dotenv()

# Get the API key from the environment variable
ANTHROPIC_API_KEY = os.getenv('ANTHROPIC_API_KEY')

if ANTHROPIC_API_KEY is None:
    raise ValueError("ANTHROPIC_API_KEY not found in environment variables.")

class RefineText:

    def __init__(self):
        self.api_key = ANTHROPIC_API_KEY
        self.system_prompt = ("Please rephrase the Hebrew parts of the following text in proper Hebrew without losing the meaning. "
                              "If there's text in other languages, don't touch it. The output must be only the rewritten text itself "
                              "without any introduction or ending.")
    def refine_message(self, user_message):
        try:
            conversation_history = [
                {"role": "user", "content": user_message}
            ]

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
                    "system": self.system_prompt,
                    "messages": conversation_history
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
        
            return chat_response
        except Exception as e:
            # Debugging: Print the exception
            print("Exception:", str(e))
            return str(e)
