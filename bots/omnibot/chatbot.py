import os
import json
import logging
from dotenv import load_dotenv
from flask import current_app
from .tools.generate_image import generate_image
from .tools.rag import VectorDB
from .persona_manager import PersonaManager
from .api_client import AnthropicAPIClient
from .knowledge_manager import KnowledgeManager

load_dotenv()
logging.basicConfig(filename='app.log', level=logging.DEBUG, format='%(asctime)s %(levelname)s %(name)s %(message)s')

class ChatBot:
    def __init__(self, app, knowledge_files=None):
        self.app = app
        self.api_client = AnthropicAPIClient()
        self.persona_manager = PersonaManager(app)
        self.knowledge_manager = KnowledgeManager(app, knowledge_files)

    def get_chat_response(self, user_message, history):
        try:
            tools = [
                {
                    "name": "generate_image",
                    "description": "Generate an image based on a given prompt",
                    "input_schema": {
                        "type": "object",
                        "properties": {
                            "prompt": {"type": "string", "description": "The prompt for generating the image"}
                        },
                        "required": ["prompt"]
                    }
                },
                {
                    "name": "switch_persona",
                    "description": f"Switch to a different bot personality. Available personalities:\n{self.persona_manager.get_all_personas()}",
                    "input_schema": {
                        "type": "object",
                        "properties": {
                            "persona_index": {"type": "integer", "description": "The index of the prompt to switch to"}
                        },
                        "required": ["persona_index"]
                    }
                },
                {
                    "name": "get_knowledge",
                    "description": "Retrieve specific knowledge when the user ask something. Can ask up to 3 queries.",
                    "input_schema": {
                        "type": "object",
                        "properties": {
                            "queries": {
                                "type": "array",
                                "items": {"type": "string"},
                                "description": "An array of up to 3 queries to find answers in the knowledge base",
                                "maxItems": 1
                            }
                        },
                        "required": ["queries"]
                    }
                }
            ]
            messages = [{"role": msg["role"], "content": [{"type": "text", "text": msg["content"][0]["text"]}]} for msg in history]
            messages.append({"role": "user", "content": [{"type": "text", "text": user_message}]})
            data = {
                "model": "claude-3-5-sonnet-20240620",
                "max_tokens": 1024,
                "system": self.persona_manager.get_system_message(),
                "tools": tools,
                "messages": messages
            }
            if current_app.config.get("FORCE_RAG"):
                data["tool_choice"] = {"type": "tool", "name": "get_knowledge"}
            first_iteration = True
            while True:
                response_data = self.api_client.call_anthropic_api(data)
                if response_data.get('stop_reason') != 'tool_use':
                    break
                print(f"Debug: Tool use detected. Stop reason: {response_data.get('stop_reason')}")
                for content_block in response_data.get('content', []):
                    print(f"Debug: Processing content block: {content_block}")
                    if content_block.get('type') == 'tool_use':
                        tool_name = content_block.get('name')
                        tool_use_id = content_block.get('id')
                        tool_input = content_block.get('input')
                        print(f"Debug: Tool use details - Name: {tool_name}, ID: {tool_use_id}, Input: {tool_input}")
                        
                        tool_result = self.handle_tool_use(tool_name, tool_input, tool_use_id)
                        
                        data["messages"].extend([
                            {"role": "assistant", "content": [content_block]},
                            {"role": "user", "content": [{"type": "tool_result", "tool_use_id": tool_use_id, "content": tool_result}]}
                        ])
                if first_iteration:
                    # Remove tools and tool_choice after the first iteration
                    data.pop("tool_choice", None)
                    first_iteration = False
                print("Debug: Calling Anthropic API with updated data")
            print("Debug: Extracting final response")
            final_response = "".join(content_block.get('text', '') for content_block in response_data.get('content', []) if content_block.get('type') == 'text')
            print(f"Debug: Final response: {final_response}")
            return final_response
        except Exception as e:
            logging.error(f"Error in get_chat_response: {str(e)}")
            return str({"error": str(e)})

    def handle_tool_use(self, tool_name, tool_input, tool_use_id):
        if tool_name == "generate_image":
            print("Debug: Generating image")
            image_url = generate_image(tool_input.get("prompt"))
            print(f"Debug: Image generated. URL: {image_url}")
            return image_url
        elif tool_name == "switch_persona":
            print("Debug: Switching persona")
            switch_result = self.persona_manager.switch_persona(tool_input.get("persona_index"))
            print(f"Debug: Prompt switch result: {switch_result}")
            return switch_result
        elif tool_name == "get_knowledge":
            print("Debug: Getting knowledge")
            queries = tool_input.get("queries", [])
            knowledge_chunks = self.knowledge_manager.get_knowledge(queries)
            print(f"Debug: Knowledge chunks retrieved: {knowledge_chunks}")
            return json.dumps(knowledge_chunks)  # Return as JSON string
        else:
            return f"Unknown tool: {tool_name}"

    def append_knowledge(self, file_path):
        return self.knowledge_manager.append_knowledge(file_path)

# Usage
# app = Flask(__name__)
# chatbot = ChatBot(app, knowledge_files="path/to/your/knowledge_file.txt")