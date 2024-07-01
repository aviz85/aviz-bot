import os
from flask import Blueprint, render_template, request, redirect, url_for, flash, send_from_directory, current_app
from flask_login import login_required, login_user, logout_user
from werkzeug.utils import secure_filename
from werkzeug.security import generate_password_hash, check_password_hash
from models import User

dashboard = Blueprint('dashboard', __name__, 
                      template_folder='templates',
                      static_folder='static',
                      static_url_path='/dashboard/static')

# This should be replaced with a proper user database
users = {
    "admin": generate_password_hash("password")
}

@dashboard.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        if username == os.getenv('ADMIN_USERNAME') and check_password_hash(generate_password_hash(os.getenv('ADMIN_PASSWORD')), password):
            user = User(username)
            login_user(user)
            return redirect(url_for('dashboard.index'))
        else:
            flash('שם משתמש או סיסמה לא נכונים')
    return render_template('dashboard/login.html')
    
@dashboard.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('dashboard.login'))
    
@dashboard.route('/')
@dashboard.route('/<path:subpath>')
@login_required
def index(subpath=''):
    bot_name = current_app.config['CHATBOT_NAME']
    widget_template_path = 'dashboard/widget.html'  # Relative path from the template folder

    uploads_dir = os.path.join(current_app.config['UPLOAD_FOLDER'], subpath)
    
    if not os.path.exists(uploads_dir):
        flash('התיקייה לא קיימת')
        return redirect(url_for('dashboard.index'))
    
    files = []
    folders = []
    for item in os.listdir(uploads_dir):
        item_path = os.path.join(uploads_dir, item)
        if os.path.isfile(item_path):
            files.append(item)
        elif os.path.isdir(item_path):
            folders.append(item)
    
    return render_template('dashboard/index.html', files=files, folders=folders, current_path=subpath, bot_name=bot_name, widget_template=widget_template_path)