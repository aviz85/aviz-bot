import os
import json
from flask import Blueprint, jsonify, request, current_app
from werkzeug.utils import secure_filename

def create_blueprint(chatbot):
    bp = Blueprint('chatbot', __name__)

    # Set the upload folder path for knowledge-related files
    upload_folder = os.path.join(current_app.config['bot_directory'], 'uploads', 'knowledge')
    allowed_extensions = {'txt', 'json', 'docx', 'pdf', 'rtf', 'csv', 'html'}  # You can extend this list as needed

    def allowed_file(filename):
        return '.' in filename and filename.rsplit('.', 1)[1].lower() in allowed_extensions

    # Ensure the directory exists
    if not os.path.exists(upload_folder):
        os.makedirs(upload_folder)

    @bp.route('/status', methods=['GET'])
    def status():
        return jsonify({'status': 'The chatbot is running'})

    @bp.route('/get_prompts', methods=['GET'])
    def get_prompts():
        prompts_file = os.path.join(current_app.config['bot_directory'], 'prompts.json')
        
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
    
    @bp.route('/upload_knowledge', methods=['POST'])
    def upload_file():
        # Check if the post request has the file part
        if 'file' not in request.files:
            return jsonify({'error': 'No file part in the request'}), 400
        file = request.files['file']
        if file.filename == '':
            return jsonify({'error': 'No file selected'}), 400
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            file_path = os.path.join(upload_folder, filename)
            file.save(file_path)
            return jsonify({'message': f'File uploaded successfully to {file_path}'})
        return jsonify({'error': 'Invalid file type'}), 400
               
    @bp.route('/append_knowledge', methods=['POST'])
    def append_knowledge():
        file_path = request.json.get('file_path')
        if not file_path:
            return jsonify({'error': 'No file path provided'}), 400
        
        if not os.path.exists(file_path):
            return jsonify({'error': 'File not found'}), 404
        
        result = chatbot.append_knowledge(file_path)
        return jsonify({'message': result})
    
    return bp