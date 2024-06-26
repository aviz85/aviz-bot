import os
import json
from flask import Blueprint, jsonify, request, current_app

def create_blueprint(chatbot):
    bp = Blueprint('chatbot', __name__)

    @bp.route('/status', methods=['GET'])
    def status():
        return jsonify({'status': 'Claude is running'})

    @bp.route('/get_prompts', methods=['GET'])
    def get_prompts():
        bot_directory = current_app.config['bot_directory']
        prompts_file = os.path.join(bot_directory, 'prompts.json')
        
        if not os.path.exists(prompts_file):
            return jsonify({'error': 'prompts.json file not found'}), 404
        
        with open(prompts_file, 'r', encoding='utf-8') as f:
            prompts = json.load(f)
        
        return jsonify(prompts)

    @bp.route('/set_prompt', methods=['POST'])
    def set_prompt():
        data = request.json
        prompt_label = data.get('label')
        if not prompt_label:
            return jsonify({'error': 'No prompt label provided'}), 400
        
        chatbot.initial_prompt_label = prompt_label
        chatbot.system_message = chatbot.get_system_message()

        return jsonify({'message': f'Prompt {prompt_label} set successfully'})
    
    return bp
