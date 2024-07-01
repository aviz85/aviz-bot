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
        if username in users and check_password_hash(users.get(username), password):
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
    
    return render_template('dashboard/index.html', files=files, folders=folders, current_path=subpath)

@dashboard.route('/upload', methods=['POST'])
@login_required
def upload_file():
    if 'file' not in request.files:
        flash('לא נבחר קובץ')
        return redirect(request.referrer)
    file = request.files['file']
    if file.filename == '':
        flash('לא נבחר קובץ')
        return redirect(request.referrer)
    if file:
        filename = secure_filename(file.filename)
        subpath = request.form.get('subpath', '')
        upload_folder = os.path.join(current_app.config['UPLOAD_FOLDER'], subpath)
        os.makedirs(upload_folder, exist_ok=True)
        file.save(os.path.join(upload_folder, filename))
        flash('הקובץ הועלה בהצלחה')
    return redirect(request.referrer)

@dashboard.route('/delete/<path:filepath>', methods=['POST'])
@login_required
def delete_file(filepath):
    file_path = os.path.join(current_app.config['UPLOAD_FOLDER'], filepath)
    if os.path.exists(file_path):
        os.remove(file_path)
        flash('הקובץ נמחק בהצלחה')
    else:
        flash('הקובץ לא נמצא')
    return redirect(request.referrer)

@dashboard.route('/download/<path:filepath>')
@login_required
def download_file(filepath):
    return send_from_directory(current_app.config['UPLOAD_FOLDER'], filepath, as_attachment=True)