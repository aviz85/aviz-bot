from groq import Groq
from openai import OpenAI
from dotenv import load_dotenv
import json, os
import sys
import logging
from whatsapp_green_link import init_whatsapp_green_link

# Load environment variables from .env file if it exists
load_dotenv()

# Add the tools directory to the system path
sys.path.append(os.path.join(os.path.dirname(__file__), 'tools'))

# Allowed file types for transcription
ALLOWED_FILE_TYPES = ['flac', 'mp3', 'mp4', 'mpeg', 'mpga', 'm4a', 'ogg', 'opus', 'wav', 'webm']

# Try to import the generate_image function from tools/generate_image.py
try:
    from generate_image import generate_image
    logging.debug("generate_image function loaded successfully.")
except ImportError as e:
    logging.error(f"Error importing generate_image: {e}")
    sys.exit(1)


# Get the API key from the environment variable
GROQ_API_KEY = os.getenv('GROQ_API_KEY')

if GROQ_API_KEY is None:
    raise ValueError("GROQ_API_KEY not found in environment variables.")

g_client = Groq(api_key=GROQ_API_KEY)

# Get the API key from the environment variable
OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')

if OPENAI_API_KEY is None:
    raise ValueError("OPENAI_API_KEY not found in environment variables.")

client = OpenAI(api_key=OPENAI_API_KEY)

# Setup logging
logging.basicConfig(filename='app.log', level=logging.DEBUG, format='%(asctime)s %(levelname)s %(name)s %(message)s')

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

        init_whatsapp_green_link(self)

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
            
            # Define the tools to call
            tools = [
                {
                    "type": "function",
                    "function": {
                        "name": "generate_image",
                        "description": "Generate an image based on a given prompt",
                        "parameters": {
                            "type": "object",
                            "properties": {
                                "prompt": {
                                    "type": "string",
                                    "description": "The prompt for generating the image"
                                }
                            },
                            "required": ["prompt"]
                        }
                    }
                }
            ]

            response = client.chat.completions.create(
                model="gpt-4o",
                messages=self.conversation_history,
                tools=tools,
                tool_choice="auto",
                temperature=1,
                max_tokens=256,
                top_p=1,
                frequency_penalty=0,
                presence_penalty=0
            )

            # Check if the model wants to call a tool
            tool_calls = getattr(response.choices[0].message, "tool_calls", None)
            if tool_calls is not None:
                for tool_call in tool_calls:
                    tool_name = tool_call.function.name
                    arguments = tool_call.function.arguments
                    logging.debug(f"Tool name: {tool_name}")
                    logging.debug(f"Arguments: {arguments}")
                    
                    if tool_name == "generate_image":
                        prompt = json.loads(arguments).get("prompt")
                        logging.debug(f"Generating image with prompt: {prompt}")
                        
                        image_url = generate_image(prompt)
                        logging.debug(f"Image generated with absolute path: {image_url}")
                        
                        # Append function call result to conversation history
                        self.conversation_history.append({"role": "function", "name": "generate_image", "content": image_url})
                        
                        # Add the image URL to the conversation history
                        self.conversation_history.append({"role": "user", "content": f"Image generated at: {image_url}"})
                        
                        logging.debug(f"Updated conversation history: {self.conversation_history}")
                        
                        # Make a second call to get the final completion
                        final_response = client.chat.completions.create(
                            model="gpt-4o",
                            messages=self.conversation_history,
                            temperature=1,
                            max_tokens=256,
                            top_p=1,
                            frequency_penalty=0,
                            presence_penalty=0
                        )
                        
                        chat_response = final_response.choices[0].message.content.strip()
                        
                        # Append assistant's response to conversation history
                        self.conversation_history.append({"role": "assistant", "content": chat_response})
                        
                        logging.debug(f"Final conversation history: {self.conversation_history}")
                        
                        return chat_response

            # Access the response content correctly
            content = getattr(response.choices[0].message, "content", None)
            if content is not None:
                chat_response = content.strip()
            else:
                chat_response = "Sorry, I didn't get a response from the model."

            # Add the assistant's response to the conversation history
            self.conversation_history.append({"role": "assistant", "content": chat_response})
        
            return chat_response
        except Exception as e:
            logging.error(f"Error in get_chat_response: {str(e)}")
            return {"error": str(e)}

    def get_transcript(self, file_path):
        file_extension = file_path.split('.')[-1].lower()
        
        if file_extension not in ALLOWED_FILE_TYPES:
            raise ValueError(f"Invalid file type: {file_extension}. Allowed types are: {', '.join(ALLOWED_FILE_TYPES)}")
        
        with open(file_path, "rb") as file:
            transcription = g_client.audio.transcriptions.create(
                file=(file_path, file.read()),
                model="whisper-large-v3",
                response_format="json"
            )
            
            return transcription.text
    
    def reset_chat_history(self):
        self.conversation_history = []
        self.set_initial_prompt()

# Instantiate ChatBot
chatbot = ChatBot()
