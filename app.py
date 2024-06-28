import os
import sys
import time
import sqlite3
from flask import Flask, request, jsonify, render_template, send_from_directory, g, redirect, url_for
from dotenv import load_dotenv
from jinja2 import TemplateNotFound, ChoiceLoader, FileSystemLoader
import importlib
import logging

# Load environment variables from the .env file
load_dotenv()

# Constants for rate limiting
RATE_LIMIT_WINDOW = int(os.getenv('RATE_LIMIT_WINDOW', 3600))  # 1 hour in seconds by default
RATE_LIMIT_REQUESTS = int(os.getenv('RATE_LIMIT_REQUESTS', 30))  # 30 requests per hour by default

# Initialize the Flask application
app = Flask(__name__)

# Set up the database connection
DATABASE = 'tokens.db'

def get_db():
    db = getattr(g, '_database', None)
    if db is None:
        db = g._database = sqlite3.connect(DATABASE)
    return db

@app.teardown_appcontext
def close_connection(exception):
    db = getattr(g, '_database', None)
    if db is not None:
        db.close()

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
app.config['bot_directory'] = bot_directory

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

# Add login route
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        token = request.form['token']
        db = get_db()
        cur = db.execute('SELECT * FROM tokens WHERE token = ?', (token,))
        user_token = cur.fetchone()
        if user_token:
            response = redirect(url_for('index'))
            response.set_cookie('token', token)
            return response
        else:
            return 'Invalid token', 401
    return render_template('login.html')

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
import inspect

@app.route('/chat', methods=['POST'])
def chat():
    global first_request_time, request_count
    token = request.cookies.get('token')
    if not token:
        return redirect(url_for('login'))

    db = get_db()
    cur = db.execute('SELECT * FROM tokens WHERE token = ?', (token,))
    user_token = cur.fetchone()
    if not user_token:
        return redirect(url_for('login'))

    token_id, token_str, credits, expiration_date = user_token
    if credits is not None and credits <= 0:
        return jsonify({'error': 'Token has no credits left'}), 403

    if expiration_date and time.time() > time.mktime(time.strptime(expiration_date, "%Y-%m-%d %H:%M:%S")):
        return jsonify({'error': 'Token has expired'}), 403

    payload = request.json
    user_message = payload.get('message')
    history = payload.get('history', [])
    
    if not user_message:
        return jsonify({'error': 'No message provided'}), 400

    # Check rate limit
    current_time = time.time()
    if first_request_time is None or current_time - first_request_time > RATE_LIMIT_WINDOW:
        first_request_time = current_time
        request_count = 0
    if request_count >= RATE_LIMIT_REQUESTS:
        return jsonify({'response': "וואו, אני עייף. בוא נדבר עוד שעה ככה... בסדר?"})
    request_count += 1

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

@app.route('/dashboard', methods=['GET', 'POST'])
def dashboard():
    if request.authorization and request.authorization.password == os.getenv('DASHBOARD_PASSWORD'):
        db = get_db()
        if request.method == 'POST':
            token = request.form['token']
            credits = request.form['credits']
            expiration_date = request.form['expiration_date']
            db.execute('INSERT INTO tokens (token, credits, expiration_date) VALUES (?, ?, ?)', (token, credits, expiration_date))
            db.commit()
        tokens = db.execute('SELECT * FROM tokens').fetchall()
        return render_template('dashboard.html', tokens=tokens)
    return 'Unauthorized', 401

@app.route('/get_current_personality', methods=['GET'])
def get_current_personality():
    try:
        current_personality = chatbot.initial_prompt_label
        return jsonify({'current_personality': current_personality})
    except AttributeError:
        app.logger.error("Chatbot object does not have initial_prompt_label attribute")
        return jsonify({'error': 'Unable to retrieve current personality'}), 500
          
try:
    routes_module = f"bots.{chatbot_name}.routes"
    bot_routes = importlib.import_module(routes_module)
    blueprint = bot_routes.create_blueprint(chatbot)
    app.register_blueprint(blueprint)
    app.logger.info(f"Custom routes for {chatbot_name} registered successfully.")
except ModuleNotFoundError:
    app.logger.warning(f"Routes module for {chatbot_name} not found. Continuing without additional routes.")
except AttributeError:
    app.logger.error(f"Routes module for {chatbot_name} does not have create_blueprint function.")
except Exception as e:
    app.logger.error(f"Error registering custom routes for {chatbot_name}: {str(e)}")

def init_db():
    with app.app_context():
        db = get_db()
        with app.open_resource('schema.sql', mode='r') as f:
            db.cursor().executescript(f.read())
        db.commit()

init_db()

# Main execution block to run the Flask app
if __name__ == '__main__':
    app.logger.info(f'Starting server for {chatbot_name}')
    if os.environ.get("WERKZEUG_RUN_MAIN") == "true":
        print(f' * Starting server for {chatbot_name}')
    app.run(debug=True, port=5001)