# Created by sagi bar on 20/6/2024
import os
from pathlib import Path
import uuid

from deep_translator import GoogleTranslator
from flask import request
from bots.tools.BaseChatBot import BaseChatBot
from openai import OpenAI

class ChatBot(BaseChatBot):
    def __init__(self, prompts_file=None):
        print("__init__")
        super().__init__(prompts_file)
        # Additional initialization if needed   
        if os.getenv("OPENAI_API_KEY") is None or os.getenv("OPENAI_API_KEY") == "":
            raise ValueError("OPENAI_API_KEY is not set")    
        
        OPENAI_API_KEY = os.getenv('OPENAI_API_KEY') 
        if OPENAI_API_KEY is None:
            raise ValueError("OPENAI_API_KEY not found in environment variables.")
        
        self.llm_object = OpenAI(api_key=OPENAI_API_KEY)

    def get_chat_response(self, user_message, history):
        super().get_chat_response(user_message)
        print("get_chat_response")
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

            # Initialize conversation history from history parameter
            self.conversation_history = [{"role": msg["role"], "content": msg["content"]} for msg in history]
            self.conversation_history.append({"role": "user", "content": user_message})
            
            response = self.llm_object.chat.completions.create(
                model="gpt-4o",
                messages=self.conversation_history,
                temperature=0.5,
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
            voice_response = self.get_file_url(chat_response)            
        
            # Add the assistant's response to the conversation history
            self.conversation_history.append({"role": "assistant", "content": chat_response})
        
            return voice_response
        except Exception as e:
            return str(e)
        
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
        print(f'Enter get_file_url')
       
        # Generate a unique filename
        speech_file_name = f"{uuid.uuid4()}.mp3"
        speech_file_path = Path(self.upload_folder) / speech_file_name        
        
        # Ensure the directory exists
        speech_file_path.parent.mkdir(parents=True, exist_ok=True)

        response = self.llm_object.audio.speech.create(
        model="tts-1",
        voice="onyx",
        input= prompt
        )

        response.stream_to_file(speech_file_path)
        # voice_url = f"/bots/text-to-speech/uploads/{speech_file_name}"
        voice_url = f"/uploads/{os.path.basename( speech_file_path.as_uri())}"
        
        full_url = request.host_url.rstrip('/') + voice_url
        print(full_url)
        return full_url

# Instantiate ChatBot
chatbot = ChatBot()
