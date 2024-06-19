from flask import Blueprint, request, jsonify, current_app
from werkzeug.utils import secure_filename
import os

bp = Blueprint('chatbot', __name__)

@bp.route('/init', methods=['POST'])
def init():
    try:
        assistant = assistant_service.create_assistant()
        return jsonify({
            'name': assistant.name,
            'instructions': assistant.instructions,
            'tools': assistant.tools,
            'model': assistant.model,
        }), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500
