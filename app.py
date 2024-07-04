import os
import sys
import time
import traceback
import json
import importlib
import logging
from flask import Flask, request, jsonify, render_template, send_from_directory, url_for
from flask_login import LoginManager, login_required, logout_user
from werkzeug.utils import secure_filename
from werkzeug.security import generate_password_hash, check_password_hash
from dotenv import load_dotenv
from jinja2 import TemplateNotFound, ChoiceLoader, FileSystemLoader
from models import User
from config import Config

# Load environment variables from the .env file
load_dotenv()

def create_app():
    app = Flask(__name__)
    app.secret_key = os.getenv('SECRET_KEY', 'your_secret_key')  # Make sure to set this in your .env file
    app.config.from_object(Config)

    # Fetch the chatbot's name from environment variables, with a fallback default
    chatbot_name = os.getenv('CHATBOT_NAME', 'default_chatbot')
    app.config['CHATBOT_NAME'] = chatbot_name

    # Set up bot directory
    bot_directory = f'bots/{chatbot_name}'
    if not os.path.exists(bot_directory):
        app.logger.warning(f"Directory for {chatbot_name} not found, falling back to default chatbot directory.")
        chatbot_name = 'chatbot'  # Revert to the default chatbot
        bot_directory = 'bots/chatbot'  # Set the directory to the default chatbot's directory
    
    app.config['RATE_LIMIT_REQUESTS'] = int(os.getenv('RATE_LIMIT_REQUESTS', 30))
    app.config['HISTORY_LIMIT'] = int(os.getenv('HISTORY_LIMIT', 20))
    app.config['BOT_DIRECTORY'] = bot_directory
    app.config['UPLOAD_FOLDER'] = os.path.join(bot_directory, 'uploads')

    # Try to import custom Persona model, fall back to default if not found
    try:
        custom_models = importlib.import_module(f"bots.{chatbot_name}.models")
        Persona = custom_models.Persona
        app.logger.info(f"Custom Persona model loaded for {chatbot_name}")
    except ImportError:
        from models import Persona  # Fall back to default Persona model
        app.logger.warning(f"Custom Persona model not found for {chatbot_name}, using default")


    # Ensure the upload folder exists
    os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

    # Add the bot's directory to sys.path
    sys.path.append(os.path.join(os.path.dirname(__file__), bot_directory))

    # Determine the module paths for the chatbot and its routes
    chatbot_module = f"bots.{chatbot_name}.chatbot"
    routes_module = f"bots.{chatbot_name}.routes"

    # Load personas from JSON file
    with open(os.path.join(bot_directory, 'personas.json'), 'r') as f:
        personas_data = json.load(f)

    # Create Persona objects and store in app.config
    app.config['PERSONAS'] = [
        Persona(p['id'], p['display_name'], p['prompt'], p['emojicon'])
        for p in personas_data['prompts']
    ]

    # Set default current persona
    app.config['CURRENT_PERSONA'] = app.config['PERSONAS'][0] if app.config['PERSONAS'] else None

    # Set default global instructions
    app.config['GLOBAL_INSTRUCTIONS'] = ""

    # Dynamically import the chatbot and its route configurations
    ChatBot = getattr(importlib.import_module(chatbot_module), 'ChatBot')
    chatbot = ChatBot(app)

    # Make chatbot globally accessible
    app.config['CHATBOT'] = chatbot

    # Add the bot's template directory to the template loader search path
    template_path = os.path.join(os.path.dirname(__file__), bot_directory, 'templates')
    app.jinja_loader = ChoiceLoader([FileSystemLoader(template_path), app.jinja_loader])

    # Initialize Flask-Login
    login_manager = LoginManager()
    login_manager.init_app(app)
    login_manager.login_view = 'dashboard.login'

    # Configure logging
    logging.basicConfig(filename='app.log', level=logging.DEBUG, format='%(asctime)s %(levelname)s %(name)s %(message)s')

    # User loader for Flask-Login
    @login_manager.user_loader
    def load_user(user_id):
        return User(user_id)

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

    # In-memory store for rate limiting
    first_request_time = None
    request_count = 0

    # Handle chat messages via POST requests
    @app.route('/chat', methods=['POST'])
    def chat():
        nonlocal first_request_time, request_count
        payload = request.json
        user_message = payload.get('message')
        history = payload.get('history', [])
        
        if not user_message:
            return jsonify({'error': 'No message provided'}), 400

        # Check rate limit
        current_time = time.time()
        if first_request_time is None or current_time - first_request_time > int(os.getenv('RATE_LIMIT_WINDOW', 3600)):
            first_request_time = current_time
            request_count = 0
        if request_count >= app.config['RATE_LIMIT_REQUESTS']:
            return jsonify({'response': "וואו, אני עייף. בוא נדבר עוד שעה ככה... בסדר?"})
        request_count += 1

        # Limit history
        history_limit = app.config['HISTORY_LIMIT']
        if history_limit % 2 != 0:
            history_limit -= 1
        if history:
            if history[-1]['role'] == 'assistant':
                history = history[-history_limit:]
            else:
                history = history[-(history_limit-1):]
                if history and history[0]['role'] != 'user':
                    history = history[1:]  # Ensure the first message is from the user

        try:
            # Call get_chat_response with both user_message and history
            chat_response = chatbot.get_chat_response(user_message, history)
        except Exception as e:
            app.logger.error(f"Error in chatbot.get_chat_response: {str(e)}")
            return jsonify({'error': 'An error occurred while processing your request'}), 500

        if isinstance(chat_response, dict) and 'error' in chat_response:
            app.logger.error(f"Chat response error: {chat_response['error']}")
            return jsonify({'error': chat_response['error']}), 500

        return jsonify({'response': chat_response})

    @app.route('/get_current_personality', methods=['GET'])
    def get_current_personality():
        try:
            current_persona = app.config['CURRENT_PERSONA']
            return jsonify({
                'slug': current_persona.slug,
                'display_name': current_persona.display_name,
                'emojicon': current_persona.emojicon
            })
        except Exception as e:
            app.logger.error(f"Error retrieving current personality: {str(e)}")
            return jsonify({'error': 'Unable to retrieve current personality'}), 500

    @app.errorhandler(Exception)
    def handle_exception(e):
        # Log the error
        app.logger.error(f"Unhandled exception: {str(e)}")
        app.logger.error(traceback.format_exc())
        # Return JSON instead of HTML for HTTP errors
        return jsonify(error=str(e)), 500

    # Register blueprints
    from dashboard.routes import dashboard as dashboard_blueprint
    app.register_blueprint(dashboard_blueprint, url_prefix='/dashboard')

    try:
        bot_routes = importlib.import_module(routes_module)
        blueprint = bot_routes.create_blueprint(app, chatbot)
        app.register_blueprint(blueprint)
        app.logger.info(f"Custom routes for {chatbot_name} registered successfully.")
    except ModuleNotFoundError:
        app.logger.warning(f"Routes module for {chatbot_name} not found. Continuing without additional routes.")
    except AttributeError:
        app.logger.error(f"Routes module for {chatbot_name} does not have create_blueprint function.")
    except Exception as e:
        app.logger.error(f"Error registering custom routes for {chatbot_name}: {str(e)}")

    return app

if __name__ == '__main__':
    app = create_app()
    app.run(debug=True)