import os
import json
from flask import Blueprint, jsonify, request, current_app
from werkzeug.utils import secure_filename

def create_blueprint(chatbot):
    bp = Blueprint('chatbot', __name__)
    
    allowed_extensions = {'txt', 'pdf', 'docx'}

    def allowed_file(filename):
        return '.' in filename and filename.rsplit('.', 1)[1].lower() in allowed_extensions

    @bp.route('/favicon.ico')
    def favicon():
        return send_from_directory(os.path.join(bp.root_path, 'static'),
                                   'favicon.ico', mimetype='image/vnd.microsoft.icon')

    @bp.route('/status', methods=['GET'])
    def status():
        return jsonify({'status': 'The chatbot is running'})

    @bp.route('/get_personas', methods=['GET'])
    def get_personas():
        personas = chatbot.get_all_personas()
        return jsonify([{
            'slug': p.get('slug') or p.get('id'),
            'display_name': p.get('display_name'),
            'emojicon': p.get('emojicon'),
            'prompt': p.get('prompt')
        } for p in personas])

    @bp.route('/set_persona', methods=['POST'])
    def set_persona():
        data = request.json
        slug = data.get('slug')
        if not slug:
            return jsonify({'error': 'No persona slug provided'}), 400
        if chatbot.set_persona(slug):
            current_persona = chatbot.get_current_persona()
            return jsonify({
                'message': f'Persona set to {current_persona.get("display_name")}',
                'slug': current_persona.get('slug') or current_persona.get('id'),
                'display_name': current_persona.get('display_name'),
                'emojicon': current_persona.get('emojicon')
            })
        return jsonify({'error': 'Persona not found'}), 404

    @bp.route('/get_current_persona', methods=['GET'])
    def get_current_persona():
        current_persona = chatbot.get_current_persona()
        if current_persona:
            return jsonify({
                'slug': current_persona.get('slug') or current_persona.get('id'),
                'display_name': current_persona.get('display_name'),
                'emojicon': current_persona.get('emojicon')
            })
        return jsonify({'error': 'No current persona set'}), 404

    @bp.route('/dashboard/personas/<slug>', methods=['PUT'])
    def update_persona(slug):
        data = request.json
        try:
            updated_persona = chatbot.update_persona(slug, data)
            return jsonify(updated_persona), 200
        except Exception as e:
            return jsonify({'error': str(e)}), 400

    @bp.route('/dashboard/personas/<slug>', methods=['DELETE'])
    def delete_persona(slug):
        try:
            chatbot.delete_persona(slug)
            return jsonify({'message': 'Persona deleted successfully'}), 200
        except Exception as e:
            return jsonify({'error': str(e)}), 400

    @bp.route('/dashboard/personas', methods=['POST'])
    def create_persona():
        data = request.json
        try:
            new_persona = chatbot.create_persona(data)
            return jsonify(new_persona), 201
        except Exception as e:
            return jsonify({'error': str(e)}), 400

    @bp.route('/upload_file', methods=['POST'])
    def upload_file():
        try:
            if 'file' not in request.files:
                return jsonify({'error': 'No file part'}), 400
            file = request.files['file']
            if file.filename == '':
                return jsonify({'error': 'No selected file'}), 400
            if file and allowed_file(file.filename):
                filename = secure_filename(file.filename)
                upload_folder = current_app.config['UPLOAD_FOLDER']
                if not os.path.exists(upload_folder):
                    os.makedirs(upload_folder)
                file_path = os.path.join(upload_folder, filename)
                file.save(file_path)
                return jsonify({'message': 'File successfully uploaded', 'filename': filename})
            else:
                return jsonify({'error': 'File type not allowed'}), 400
        except Exception as e:
            current_app.logger.error(f"Error in upload_file: {str(e)}")
            return jsonify({'error': str(e)}), 500

    @bp.route('/append_knowledge', methods=['POST'])
    def append_knowledge():
        try:
            data = request.json
            if not data or 'filename' not in data:
                return jsonify({'error': 'No filename provided'}), 400
            filename = data['filename']
            file_path = os.path.join(current_app.config['UPLOAD_FOLDER'], filename)
            if not os.path.exists(file_path):
                return jsonify({'error': 'File not found'}), 404
            
            result = chatbot.append_knowledge(file_path)
            return jsonify({'message': result}), 200
        except Exception as e:
            current_app.logger.error(f"Error in append_knowledge: {str(e)}")
            return jsonify({'error': str(e)}), 500

    @bp.route('/get_file_list', methods=['GET'])
    def get_file_list():
        try:
            upload_folder = current_app.config['UPLOAD_FOLDER']
            if not os.path.exists(upload_folder):
                return jsonify({'error': 'Upload folder does not exist'}), 404
            
            files = [f for f in os.listdir(upload_folder) if os.path.isfile(os.path.join(upload_folder, f)) and allowed_file(f)]
            return jsonify(files)
        except Exception as e:
            current_app.logger.error(f"Error in get_file_list: {str(e)}")
            return jsonify({'error': str(e)}), 500

    @bp.route('/delete_file', methods=['POST'])
    def delete_file():
        try:
            data = request.json
            if not data or 'filename' not in data:
                return jsonify({'error': 'No filename provided'}), 400
            filename = data['filename']
            file_path = os.path.join(current_app.config['UPLOAD_FOLDER'], filename)
            if not os.path.exists(file_path):
                return jsonify({'error': 'File not found'}), 404
            
            os.remove(file_path)
            return jsonify({'success': True, 'message': f'File {filename} deleted successfully'})
        except Exception as e:
            current_app.logger.error(f"Error in delete_file: {str(e)}")
            return jsonify({'error': str(e)}), 500

    @bp.route('/set_global_instructions', methods=['POST'])
    def set_global_instructions():
        try:
            data = request.json
            instructions = data.get('instructions', '')
            current_app.config['GLOBAL_INSTRUCTIONS'] = instructions
            return jsonify({'success': True, 'message': 'Global instructions saved successfully'})
        except Exception as e:
            current_app.logger.error(f"Error in set_global_instructions: {str(e)}")
            return jsonify({'success': False, 'error': str(e)}), 500

    @bp.route('/get_global_instructions', methods=['GET'])
    def get_global_instructions():
        try:
            instructions = current_app.config.get('GLOBAL_INSTRUCTIONS', '')
            return jsonify({'instructions': instructions})
        except Exception as e:
            current_app.logger.error(f"Error in get_global_instructions: {str(e)}")
            return jsonify({'error': str(e)}), 500

    return bp