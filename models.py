# models.py

from flask_login import UserMixin
from flask import current_app

class User(UserMixin):
    def __init__(self, id):
        self.id = id

class Persona:
    def __init__(self, slug, display_name, prompt, emojicon):
        self.slug = slug
        self.display_name = display_name
        self.prompt = prompt
        self.emojicon = emojicon

    @classmethod
    def get_all(cls):
        return current_app.config.get('PERSONAS', [])

    @classmethod
    def get_by_slug(cls, slug):
        return next((p for p in cls.get_all() if p.slug == slug), None)

    @classmethod
    def create(cls, slug, display_name, prompt, emojicon):
        new_persona = cls(slug, display_name, prompt, emojicon)
        personas = cls.get_all()
        personas.append(new_persona)
        current_app.config['PERSONAS'] = personas
        return new_persona

    def update(self, display_name=None, prompt=None, emojicon=None):
        if display_name is not None:
            self.display_name = display_name
        if prompt is not None:
            self.prompt = prompt
        if emojicon is not None:
            self.emojicon = emojicon

    @classmethod
    def delete(cls, slug):
        personas = cls.get_all()
        personas = [p for p in personas if p.slug != slug]
        current_app.config['PERSONAS'] = personas

    def to_dict(self):
        return {
            'slug': self.slug,
            'display_name': self.display_name,
            'prompt': self.prompt,
            'emojicon': self.emojicon
        }

    @classmethod
    def from_dict(cls, data):
        return cls(
            slug=data['slug'],
            display_name=data['display_name'],
            prompt=data['prompt'],
            emojicon=data['emojicon']
        )