from openai import OpenAI
from dotenv import load_dotenv
from flask import Flask, jsonify, request
import os

class AssistantService:
    def __init__(self):
        load_dotenv()
        self.api_key = os.getenv('OPENAI_API_KEY')
        if self.api_key is None:
            raise ValueError("OPENAI_API_KEY not found in environment variables.")
        self.client = OpenAI(api_key=self.api_key)
        self.assistant = None

    def create_assistant(self):
        if self.assistant is None:
            self.assistant = self.client.beta.assistants.create(
                name="Math Tutor",
                instructions="You are a personal math tutor. Write and run code to answer math questions.",
                tools=[{"type": "code_interpreter"}],
                model="gpt-4o",
            )
        return self.assistant

# Create the Flask app
app = Flask(__name__)
assistant_service = AssistantService()

thread = client.beta.threads.create()

message = client.beta.threads.messages.create(
  thread_id=thread.id,
  role="user",
  content="I need to solve the equation `3x + 11 = 14`. Can you help me?"
)