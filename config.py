import os
from werkzeug.security import generate_password_hash

class Config:
    SECRET_KEY = os.getenv('SECRET_KEY', 'default_secret_key')
    USERS = {
        'admin': generate_password_hash(os.getenv('ADMIN_PASSWORD', 'default_password')),
        # Add more users here if needed
    }
    CHATBOT_NAME = os.getenv('CHATBOT_NAME', 'chatbot')
    FORCE_RAG = os.getenv('FORCE_RAG'), True
    

CHATBOT_IMPORT_PATH = "bots.chatbot.chatbot.ChatBot"
