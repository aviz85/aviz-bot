from flask import Blueprint, jsonify

bp = Blueprint('chatbot', __name__)

@bp.route('/status', methods=['GET'])
def status():
    return jsonify({'status': 'Claude is running'})
