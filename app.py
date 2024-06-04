from flask import Flask, request, jsonify, render_template
import importlib
import config

app = Flask(__name__)

# Dynamic Import
chatbot_module, chatbot_class_name = config.CHATBOT_IMPORT_PATH.rsplit(".", 1)
ChatBot = getattr(importlib.import_module(chatbot_module), chatbot_class_name)
chatbot = ChatBot() 

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/chat', methods=['POST'])
def chat():
    user_message = request.json.get('message')
    
    if not user_message:
        return jsonify({'error': 'No message provided'}), 400
    
    chat_response = chatbot.get_chat_response(user_message)
    
    if 'error' in chat_response:
        return jsonify({'error': chat_response}), 500
    
    return jsonify({'response': chat_response})

@app.route('/reset', methods=['POST'])
def reset():
    chatbot.reset_chat_history()
    return jsonify({'message': 'Chat history cleared'}), 200

if __name__ == '__main__':
    app.run(debug=True)
