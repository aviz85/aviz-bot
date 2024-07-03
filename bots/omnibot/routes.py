# routes.py
import os
import traceback
import json
from flask import Blueprint, jsonify, request, current_app, send_from_directory
from werkzeug.utils import secure_filename

def create_blueprint(chatbot):
    bp = Blueprint('chatbot', __name__)
    
    allowed_extensions = {'txt', 'pdf', 'docx'}

    def allowed_file(filename):
        return '.' in filename and filename.rsplit('.', 1)[1].lower() in allowed_extensions

    @bp.route('/status', methods=['GET'])
    def status():
        return jsonify({'status': 'The chatbot is running'})

    @bp.route('/get_prompts', methods=['GET'])
    def get_prompts():
        prompts_file = os.path.join(current_app.config['BOT_DIRECTORY'], 'prompts.json')
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

    @bp.route('/upload_file', methods=['POST'])
    def upload_file():
        try:
            if 'file' not in request.files:
                return jsonify({'error': 'No file part'}), 400
            file = request.files['file']
            if file.filename == '':
                return jsonify({'error': 'No selected file'}), 400
            if file:
                filename = secure_filename(file.filename)
                upload_folder = current_app.config['UPLOAD_FOLDER']
                if not os.path.exists(upload_folder):
                    os.makedirs(upload_folder)
                file_path = os.path.join(upload_folder, filename)
                file.save(file_path)
                return jsonify({'message': 'File successfully uploaded', 'filename': filename})
        except Exception as e:
            current_app.logger.error(f"Error in upload_file: {str(e)}")
            return jsonify({'error': str(e), 'traceback': traceback.format_exc()}), 500
    
    @bp.route('/append_knowledge', methods=['POST'])
    def append_knowledge():
        try:
            data = request.json
            current_app.logger.info(f"Received data: {data}")
            
            if not data or 'filename' not in data:
                return jsonify({'error': 'No filename provided'}), 400
            upload_folder = current_app.config['UPLOAD_FOLDER']
            file_path = os.path.join(upload_folder, data['filename'])
            current_app.logger.info(f"Attempting to append knowledge from file: {file_path}")
            
            if not os.path.exists(file_path):
                current_app.logger.error(f"File not found: {file_path}")
                return jsonify({'error': 'File not found'}), 404
            
            # Call the chatbot's append_knowledge method
            print(file_path)
            result = current_app.config['chatbot'].append_knowledge(file_path)
            current_app.logger.info(f"Knowledge appended successfully: {result}")
            return jsonify({'message': result}), 200
        except Exception as e:
            current_app.logger.error(f"Error in append_knowledge route: {str(e)}")
            return jsonify({'error': str(e), 'traceback': traceback.format_exc()}), 500
            
    
    @bp.route('/get_file_list', methods=['GET'])
    def get_file_list():
        try:
            upload_folder = current_app.config['UPLOAD_FOLDER']
            current_app.logger.info(f"Checking for files in: {upload_folder}")
            
            if not os.path.exists(upload_folder):
                current_app.logger.warning(f"Upload folder does not exist: {upload_folder}")
                return jsonify({'error': 'Upload folder does not exist'}), 404
            
            all_files = os.listdir(upload_folder)
            current_app.logger.info(f"All files in directory: {all_files}")
            
            files = [f for f in all_files if f.endswith(('.txt', '.docx', '.pdf'))]
            current_app.logger.info(f"Filtered files: {files}")
            
            return jsonify(files)
        except Exception as e:
             current_app.logger.error(f"Error in get_file_list: {str(e)}")
             return jsonify({'error': str(e)}), 500
    
    @bp.route('/delete_file', methods=['POST'])
    def delete_file():
        try:
            filename = request.json.get('filename')
            if not filename:
                return jsonify({'error': 'No filename provided'}), 400
            
            file_path = os.path.join(current_app.config['UPLOAD_FOLDER'], filename)
            if not os.path.exists(file_path):
                return jsonify({'error': 'File not found'}), 404
            
            os.remove(file_path)
            
            # Delete any additional files with the same name prefix
            base_name = os.path.splitext(filename)[0]
            for f in os.listdir(current_app.config['UPLOAD_FOLDER']):
                if f.startswith(base_name) and f != filename:
                    os.remove(os.path.join(current_app.config['UPLOAD_FOLDER'], f))
            
            return jsonify({'success': True, 'message': f'File {filename} deleted successfully'})
        except Exception as e:
            current_app.logger.error(f"Error in delete_file: {str(e)}")
            return jsonify({'error': str(e)}), 500

    @bp.route('/set_additional_instructions', methods=['POST'])
    def set_additional_instructions():
        try:
            data = request.json
            instructions = data.get('instructions', '')
            current_app.config['ADDITIONAL_INSTRUCTIONS'] = instructions
            return jsonify({'success': True, 'message': 'Additional instructions saved successfully'})
        except Exception as e:
            current_app.logger.error(f"Error in set_additional_instructions: {str(e)}")
            return jsonify({'success': False, 'error': str(e)}), 500

    @bp.route('/get_additional_instructions', methods=['GET'])
    def get_additional_instructions():
        try:
            instructions = current_app.config.get('ADDITIONAL_INSTRUCTIONS', '')
            return jsonify({'instructions': instructions})
        except Exception as e:
            current_app.logger.error(f"Error in get_additional_instructions: {str(e)}")
            return jsonify({'error': str(e)}), 500
        
    return bp