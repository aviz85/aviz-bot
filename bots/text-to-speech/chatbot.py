# Created by sagi bar on 10/6/2024
# the reference: https://platform.openai.com/docs/guides/text-to-speech

from openai import OpenAI
from dotenv import load_dotenv
import json, os
import uuid

from flask import request
from pathlib import Path
from deep_translator import GoogleTranslator

# Load environment variables from .env file if it exists
load_dotenv()

# Get the API key from the environment variable
OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')

if OPENAI_API_KEY is None:
    raise ValueError("OPENAI_API_KEY not found in environment variables.")

client = OpenAI(api_key=OPENAI_API_KEY)

class ChatBot:
    # Define the constant for the uploads folder
    UPLOAD_FOLDER = Path(__file__).parent / "uploads"

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
            print(user_message)

            # check language
            is_hebrew_message = self.is_hebrew(user_message)

            if is_hebrew_message:
                print("Hebrew")
                # Translate hebrew to english
                user_message = self.translate_text(user_message, "en")                
            else:
                print("Not Hebrew")
                
            print(user_message)

             # Add the user's message to the conversation history
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
            
            if is_hebrew_message: 
                # Translate the response to hebrew
                chat_response = self.translate_text(chat_response, "iw") #the answer in hebrew
                print(chat_response)

            # get the url for voice message
            voice_response = self.get_voice_url(chat_response)            
        
            # Add the assistant's response to the conversation history
            self.conversation_history.append({"role": "assistant", "content": chat_response})
        
            return voice_response
        except Exception as e:
            return str(e)
    
    def reset_chat_history(self):
        self.conversation_history = []
        self.set_initial_prompt()
    
    def is_hebrew(self, prompt: str) -> bool:
        for char in prompt:
            if '\u0590' <= char <= '\u05FF':
                return True
        return False
    
    def translate_text(self, text: str, target_language: str):        
        try:
            # Translate the text using deep-translator
            translated = GoogleTranslator(source='auto', target=target_language).translate(text)
            return translated
        except Exception as e:
            return f"Error occurred during translation: {e}"

    def get_file_url(self, prompt=None):
        print(f'Enter get_voice_url')

        # Generate a unique filename
        unique_filename = f"{uuid.uuid4()}.mp3"            
        # base_dir = Path(__file__).parent / "uploads"
        speech_file_path = self.UPLOAD_FOLDER / unique_filename
        # speech_file_path = Path(__file__).parent / "uploads" / "speech.mp3"

        # Ensure the directory exists
        speech_file_path.parent.mkdir(parents=True, exist_ok=True)

        response = client.audio.speech.create(
        model="tts-1",
        voice="onyx",
        input= prompt
        )

        response.stream_to_file(speech_file_path)
        voice_url = f"/uploads/{os.path.basename( speech_file_path.as_uri())}"

        # voice_url = speech_file_path.as_uri()
        full_url = request.host_url.rstrip('/') + voice_url
        print(full_url)
        return full_url

# Instantiate ChatBot
chatbot = ChatBot()
