from flask import Flask, request, jsonify, render_template, send_from_directory
import importlib
import os
from dotenv import load_dotenv
from jinja2 import TemplateNotFound
import logging

# Load environment variables from the .env file
load_dotenv()

# Initialize the Flask application
app = Flask(__name__)

# Configure logging
logging.basicConfig(filename='app.log', level=logging.DEBUG, format='%(asctime)s %(levelname)s %(name)s %(message)s')

# Fetch the chatbot's name from environment variables, with a fallback default
chatbot_name = os.getenv('CHATBOT_NAME', 'chatbot')

# Check if the specific chatbot's directory exists; fallback to default if it does not
bot_directory = f'bots/{chatbot_name}'
if not os.path.exists(bot_directory):
    app.logger.warning(f"Directory for {chatbot_name} not found, falling back to default chatbot directory.")
    chatbot_name = 'chatbot'  # Revert to the default chatbot
    bot_directory = 'bots/chatbot'  # Set the directory to the default chatbot's directory

# Determine the module paths for the chatbot and its routes
chatbot_module = f"bots.{chatbot_name}.chatbot"
routes_module = f"bots.{chatbot_name}.routes"

# Dynamically import the chatbot and its route configurations
ChatBot = getattr(importlib.import_module(chatbot_module), 'ChatBot')
chatbot = ChatBot()

try:
    bot_routes = importlib.import_module(routes_module)
    app.register_blueprint(bot_routes.bp)
except ModuleNotFoundError:
    app.logger.warning(f"Routes module for {chatbot_name} not found. Continuing without additional routes.")

# Serve static files from the chatbot's static directory
@app.route('/custom/static/<path:filename>')
def custom_static(filename):
    return send_from_directory(f'{bot_directory}/static', filename)

# Serve image files from the uploads directory
@app.route('/uploads/<path:filename>')
def uploads(filename):
    return send_from_directory(f'{bot_directory}/uploads', filename)

# Render the main page template
@app.route('/')
def index():
    widget_template = None
    try:
        widget_template = f'{chatbot_name}/widget.html'
        render_template(widget_template)
    except TemplateNotFound:
        widget_template = None
    return render_template('index.html', widget_template=widget_template, bot_name=chatbot_name)

# Handle chat messages via POST requests
@app.route('/chat', methods=['POST'])
def chat():
    user_message = request.json.get('message')
    if not user_message:
        return jsonify({'error': 'No message provided'}), 400
    chat_response = chatbot.get_chat_response(user_message)
    if 'error' in chat_response:
        app.logger.error(f"Chat response error: {chat_response['error']}")
        return jsonify({'error': chat_response}), 500
    return jsonify({'response': chat_response})

# Reset the chat history
@app.route('/reset', methods=['POST'])
def reset():
    chatbot.reset_chat_history()
    return jsonify({'message': 'Chat history cleared'}), 200

# Main execution block to run the Flask app
if __name__ == '__main__':
    app.logger.info(f'Starting server for {chatbot_name}')
    if os.environ.get("WERKZEUG_RUN_MAIN") == "true":
        print(f' * Starting server for {chatbot_name}')
    app.run(debug=True)
