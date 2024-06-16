# https://github.com/aviz85/aviz-bot/

import os
import sys
from flask import Flask, request, jsonify, render_template, send_from_directory
from dotenv import load_dotenv
from jinja2 import TemplateNotFound, ChoiceLoader, FileSystemLoader
import importlib
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

sys.path.append(os.path.join(os.path.dirname(__file__), bot_directory))

# Determine the module paths for the chatbot and its routes
chatbot_module = f"bots.{chatbot_name}.chatbot"
routes_module = f"bots.{chatbot_name}.routes"

# Dynamically import the chatbot and its route configurations
ChatBot = getattr(importlib.import_module(chatbot_module), 'ChatBot')
chatbot = ChatBot()

# Make chatbot globally accessible
app.config['chatbot'] = chatbot

# Add the bot's template directory to the template loader search path
template_path = os.path.join(os.path.dirname(__file__), bot_directory, 'templates')
app.jinja_loader = ChoiceLoader([FileSystemLoader(template_path), app.jinja_loader])

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
        widget_template = 'widget.html'
        render_template(widget_template)
    except TemplateNotFound:
        widget_template = None
    return render_template('index.html', widget_template=widget_template, bot_name=chatbot_name)

# Handle chat messages via POST requests
import inspect

@app.route('/chat', methods=['POST'])
def chat():
    payload = request.json
    user_message = payload.get('message')
    if not user_message:
        return jsonify({'error': 'No message provided'}), 400

    additional_params = {key: value for key, value in payload.items() if key != 'message'}
    
    # Determine the number of parameters the function accepts
    params_count = len(inspect.signature(chatbot.get_chat_response).parameters)
    
    if params_count == 1:
        chat_response = chatbot.get_chat_response(user_message)
    elif params_count == 2:
        chat_response = chatbot.get_chat_response(user_message, additional_params)
    else:
        app.logger.error("chatbot.get_chat_response has an unexpected number of parameters")
        return jsonify({'error': 'Unexpected error occurred'}), 500
    
    if 'error' in chat_response:
        app.logger.error(f"Chat response error: {chat_response['error']}")
        return jsonify({'error': chat_response}), 500
    
    return jsonify({'response': chat_response})

# Reset the chat history
@app.route('/reset', methods=['POST'])
def reset():
    global chatbot
    del chatbot
    chatbot = ChatBot()
    return jsonify({'message': 'Chat history cleared and chatbot reset'}), 200

# Register the chatbot's custom routes after default routes
try:
    bot_routes = importlib.import_module(routes_module)
    app.register_blueprint(bot_routes.bp)
except ModuleNotFoundError:
    app.logger.warning(f"Routes module for {chatbot_name} not found. Continuing without additional routes.")

# Main execution block to run the Flask app
if __name__ == '__main__':
    app.logger.info(f'Starting server for {chatbot_name}')
    if os.environ.get("WERKZEUG_RUN_MAIN") == "true":
        print(f' * Starting server for {chatbot_name}')
    app.run(debug=True, port=5001)
