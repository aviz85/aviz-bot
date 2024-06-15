import json
import cohere
from .retriever import RetrieverWithRerank
import os
from dotenv import load_dotenv
from uuid import uuid4
from datetime import datetime, timedelta

# Load environment variables from the .env file
load_dotenv()

class ChatBot:
    def __init__(self, api_key=None, prompts_file=None):
        self.api_key = api_key or os.getenv('COHERE_API_KEY')
        self.client = cohere.Client(api_key=self.api_key)
        
        if prompts_file is None:
            prompts_file = os.path.join(os.path.dirname(__file__), 'prompts.json')
        
        with open(prompts_file, 'r') as f:
            prompts_data = json.load(f)
        self.prompts = prompts_data["prompts"]
        self.conversation_history = {}
        self.retrievers = {}
        self.session_expiry = {}

        self.initial_prompt_label = "sarcastic_friend"

    def set_initial_prompt(self, session_id):
        initial_prompt = next((prompt["prompt"] for prompt in self.prompts if prompt["label"] == self.initial_prompt_label), None)
        if initial_prompt:
            self.conversation_history[session_id] = [{"role": "CHATBOT", "text": initial_prompt}]
        else:
            raise ValueError(f"Prompt with label '{self.initial_prompt_label}' not found in prompts.")

    def process_and_store_documents(self, document_paths):
        self.cleanup_expired_sessions()
        session_id = str(uuid4())
        retriever = RetrieverWithRerank(api_key=self.api_key)
        retriever.build_index(document_paths)
        self.retrievers[session_id] = retriever
        self.set_initial_prompt(session_id)
        self.session_expiry[session_id] = datetime.now() + timedelta(hours=24)
        return session_id

    def cleanup_expired_sessions(self):
        current_time = datetime.now()
        expired_sessions = [sid for sid, expiry in self.session_expiry.items() if expiry < current_time]
        for sid in expired_sessions:
            del self.conversation_history[sid]
            del self.retrievers[sid]
            del self.session_expiry[sid]

    def get_chat_response(self, user_message, params):
        print("Starting get_chat_response")
        print("self:", self)
        print("self.conversation_history:", self.conversation_history)

        try:
            if 'session_id' not in params:
                print("Error: session_id is missing in params")
                return {"error": "session_id is missing in params"}
            
            session_id = params['session_id']
            print("session_id:", session_id)
            
            if session_id not in self.conversation_history:
                print("Error: session_id not found in conversation_history")
                return {"error": "session_id not found in conversation_history"}
            
            if session_id not in self.retrievers:
                print("Error: session_id not found in retrievers")
                return {"error": "session_id not found in retrievers"}

            print("Appending user message to conversation history")
            self.conversation_history[session_id].append({"role": "USER", "text": user_message})
            print("Updated conversation history:", self.conversation_history[session_id])
            
            print("Retrieving documents")
            retrieved_docs = self.retrievers[session_id].retrieve(user_message)
            print("retrieved_docs:", retrieved_docs)
            
            print("Sending chat request to client")
            response = self.client.chat(
                message=user_message,
                chat_history=self.conversation_history[session_id],
                model="command-r-plus",
                temperature=0.0,
                documents=[{"text": doc['text']} for doc in retrieved_docs]
            )
            print("response:", response)

            chat_response = response.text.strip()
            print("chat_response:", chat_response)

            print("Appending assistant response to conversation history")
            self.conversation_history[session_id].append({"role": "CHATBOT", "text": chat_response})
            print("Updated conversation history:", self.conversation_history[session_id])

            return chat_response
        except Exception as e:
            print("Exception occurred:", str(e))
            return {"error": str(e)}
            
    def reset_chat_history(self, session_id):
        if session_id in self.conversation_history:
            del self.conversation_history[session_id]
        if session_id in self.retrievers:
            del self.retrievers[session_id]
        if session_id in self.session_expiry:
            del self.session_expiry[session_id]

    def clear_chat(self):
        self.conversation_history.clear()
        self.retrievers.clear()
        self.session_expiry.clear()
