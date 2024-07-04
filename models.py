# models.py

from flask_login import UserMixin
from flask import current_app

class User(UserMixin):
    def __init__(self, id):
        self.id = id

