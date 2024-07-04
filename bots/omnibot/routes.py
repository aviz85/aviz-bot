import os
import json
from flask import Blueprint, jsonify, request, send_from_directory
from werkzeug.utils import secure_filename
from .models import Persona  # Ensure this import path is correct

def create_blueprint(app, chatbot):
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
        try:
            personas = chatbot.persona_manager.get_all_personas()
            personas_dicts = [p.to_dict() if isinstance(p, Persona) else p for p in personas]
            return jsonify(personas_dicts)
        except Exception as e:
            app.logger.error(f"Error in get_personas: {str(e)}")
            return jsonify({'error': str(e)}), 500

    @bp.route('/get_current_persona', methods=['GET'])
    def get_current_persona():
        try:
            current_persona = chatbot.persona_manager.get_current_persona()
            if current_persona:
                return jsonify(current_persona.to_dict() if isinstance(current_persona, Persona) else current_persona)
            return jsonify({'error': 'No current persona set'}), 404
        except Exception as e:
            app.logger.error(f"Error in get_current_persona: {str(e)}")
            return jsonify({'error': str(e)}), 500

    @bp.route('/set_persona', methods=['POST'])
    def set_persona():
        data = request.json
        slug = data.get('slug')
        if not slug:
            return jsonify({'error': 'No persona slug provided'}), 400
        if chatbot.persona_manager.set_persona(slug):
            current_persona = chatbot.persona_manager.get_current_persona()
            return jsonify({
                'message': f'Persona set to {current_persona.display_name}',
                'slug': current_persona.slug,
                'display_name': current_persona.display_name,
                'emojicon': current_persona.emojicon
            })
        return jsonify({'error': 'Persona not found'}), 404

    @bp.route('/dashboard/personas/<slug>', methods=['PUT'])
    def update_persona(slug):
        data = request.json
        try:
            success = chatbot.persona_manager.update_persona(
                slug, 
                display_name=data.get('display_name'),
                prompt=data.get('prompt'),
                emojicon=data.get('emojicon')
            )
            if success:
                updated_persona = chatbot.persona_manager.get_by_slug(slug)
                return jsonify(updated_persona.to_dict()), 200
            else:
                return jsonify({'error': 'Persona not found'}), 404
        except Exception as e:
            app.logger.error(f"Error in update_persona: {str(e)}")
            return jsonify({'error': str(e)}), 400

    @bp.route('/dashboard/personas/<slug>', methods=['DELETE'])
    def delete_persona(slug):
        try:
            chatbot.persona_manager.delete_persona(slug)
            return jsonify({'message': 'Persona deleted successfully'}), 200
        except Exception as e:
            app.logger.error(f"Error in delete_persona: {str(e)}")
            return jsonify({'error': str(e)}), 400

    @bp.route('/dashboard/personas', methods=['POST'])
    def create_persona():
        data = request.json
        try:
            new_persona = chatbot.persona_manager.create_persona(
                slug=data.get('slug'),
                display_name=data.get('display_name'),
                prompt=data.get('prompt'),
                emojicon=data.get('emojicon')
            )
            return jsonify(new_persona.to_dict()), 201
        except Exception as e:
            app.logger.error(f"Error in create_persona: {str(e)}")
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
                upload_folder = app.config['UPLOAD_FOLDER']
                if not os.path.exists(upload_folder):
                    os.makedirs(upload_folder)
                file_path = os.path.join(upload_folder, filename)
                file.save(file_path)
                return jsonify({'message': 'File successfully uploaded', 'filename': filename})
            else:
                return jsonify({'error': 'File type not allowed'}), 400
        except Exception as e:
            app.logger.error(f"Error in upload_file: {str(e)}")
            return jsonify({'error': str(e)}), 500

    @bp.route('/append_knowledge', methods=['POST'])
    def append_knowledge():
        try:
            data = request.json
            if not data or 'filename' not in data:
                return jsonify({'error': 'No filename provided'}), 400
            filename = data['filename']
            file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            if not os.path.exists(file_path):
                return jsonify({'error': 'File not found'}), 404
            
            result = chatbot.append_knowledge(file_path)
            return jsonify({'message': result}), 200
        except Exception as e:
            app.logger.error(f"Error in append_knowledge: {str(e)}")
            return jsonify({'error': str(e)}), 500

    @bp.route('/get_file_list', methods=['GET'])
    def get_file_list():
        try:
            upload_folder = app.config['UPLOAD_FOLDER']
            if not os.path.exists(upload_folder):
                return jsonify({'error': 'Upload folder does not exist'}), 404
            
            files = [f for f in os.listdir(upload_folder) if os.path.isfile(os.path.join(upload_folder, f)) and allowed_file(f)]
            return jsonify(files)
        except Exception as e:
            app.logger.error(f"Error in get_file_list: {str(e)}")
            return jsonify({'error': str(e)}), 500

    @bp.route('/delete_file', methods=['POST'])
    def delete_file():
        try:
            data = request.json
            if not data or 'filename' not in data:
                return jsonify({'error': 'No filename provided'}), 400
        
            filename = data['filename']
            file_base_name = os.path.splitext(filename)[0]
            upload_folder = app.config['UPLOAD_FOLDER']
        
            # Delete the main file and associated files
            for file in os.listdir(upload_folder):
                if file.startswith(file_base_name):
                    file_path = os.path.join(upload_folder, file)
                    os.remove(file_path)
                    app.logger.info(f"Deleted file: {file}")
        
            # Update manifest.json
            manifest_path = os.path.join(upload_folder, 'file_manifest.json')
            if os.path.exists(manifest_path):
                with open(manifest_path, 'r+') as f:
                    manifest = json.load(f)
                    if file_base_name in manifest:
                        del manifest[file_base_name]
                        f.seek(0)
                        json.dump(manifest, f, indent=2)
                        f.truncate()
                        app.logger.info(f"Updated manifest.json, removed entry for {file_base_name}")
        
            return jsonify({'success': True, 'message': f'File {filename} and associated files deleted successfully'})
 
        except Exception as e:
            app.logger.error(f"Error in delete_file: {str(e)}")
            return jsonify({'error': str(e)}), 500

    @bp.route('/set_global_instructions', methods=['POST'])
    def set_global_instructions():
        try:
            data = request.json
            instructions = data.get('instructions', '')
            app.config['GLOBAL_INSTRUCTIONS'] = instructions
            return jsonify({'success': True, 'message': 'Global instructions saved successfully'})
        except Exception as e:
            app.logger.error(f"Error in set_global_instructions: {str(e)}")
            return jsonify({'success': False, 'error': str(e)}), 500

    @bp.route('/get_global_instructions', methods=['GET'])
    def get_global_instructions():
        try:
            instructions = app.config.get('GLOBAL_INSTRUCTIONS', '')
            return jsonify({'instructions': instructions})
        except Exception as e:
            app.logger.error(f"Error in get_global_instructions: {str(e)}")
            return jsonify({'error': str(e)}), 500

    return bp