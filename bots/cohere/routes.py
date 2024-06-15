from flask import Blueprint, request, jsonify, current_app
from werkzeug.utils import secure_filename
import os

bp = Blueprint('chatbot', __name__)

@bp.route('/upload-documents', methods=['POST'])
def upload_documents():
    files = request.files.getlist('documents')
    if not files:
        return jsonify({'error': 'No documents provided'}), 400

    document_paths = []
    for file in files:
        filename = secure_filename(file.filename)
        file_path = os.path.join('/tmp', filename)
        file.save(file_path)
        document_paths.append(file_path)

    chatbot = current_app.config['chatbot']
    session_id = chatbot.process_and_store_documents(document_paths)
    return jsonify({'message': 'Documents processed and stored successfully', 'session_id': session_id}), 200

@bp.route('/reset', methods=['POST'])
def reset():
    session_id = request.json.get('session_id')
    if not session_id:
        return jsonify({'error': 'No session ID provided'}), 400
    chatbot = current_app.config['chatbot']
    chatbot.reset_chat_history(session_id)
    return jsonify({'message': f'Chat history for session {session_id} cleared and chatbot reset'}), 200

@bp.route('/clear', methods=['POST'])
def clear():
    chatbot = current_app.config['chatbot']
    chatbot.clear_chat()
    return jsonify({'message': 'All chat histories and vector stores cleared'}), 200
