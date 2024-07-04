class Persona:
    def __init__(self, slug, display_name, prompt, emojicon):
        self.slug = slug
        self.display_name = display_name
        self.prompt = prompt
        self.emojicon = emojicon

    @classmethod
    def get_all(cls, personas):
        return [cls.from_dict(p) if isinstance(p, dict) else p for p in personas]

    @classmethod
    def get_by_slug(cls, personas, slug):
        for p in personas:
            if isinstance(p, dict) and p['slug'] == slug:
                return cls.from_dict(p)
            elif isinstance(p, cls) and p.slug == slug:
                return p
        return None

    @classmethod
    def create(cls, personas, slug, display_name, prompt, emojicon):
        new_persona = cls(slug, display_name, prompt, emojicon)
        personas.append(new_persona)
        return new_persona
    
    def update(self, display_name=None, prompt=None, emojicon=None):
        if display_name is not None:
            self.display_name = display_name
        if prompt is not None:
            self.prompt = prompt
        if emojicon is not None:
            self.emojicon = emojicon

    @classmethod
    def delete(cls, personas, slug):
        persona_to_delete = cls.get_by_slug(personas, slug)
        if persona_to_delete:
            personas.remove(persona_to_delete)

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