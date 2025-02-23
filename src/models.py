from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import Integer, String, Boolean, ForeignKey, Table
from sqlalchemy.orm import relationship
from werkzeug.security import generate_password_hash

db = SQLAlchemy()

# USER MODEL

class User(db.Model):
    __tablename__ = 'users'
    id = db.Column(Integer, primary_key=True)
    email = db.Column(String(120), unique=True, nullable=False)
    password = db.Column(String(256), nullable=False)  # Mayor seguridad
    is_active = db.Column(Boolean, default=True)

    favorites = relationship('Favorite', back_populates='user', cascade="all, delete-orphan")

    def set_password(self, password):
        """Almacena la contraseña cifrada."""
        self.password = generate_password_hash(password)

    def serialize(self):
        return {
            "id": self.id,
            "email": self.email,
            "is_active": self.is_active,
            "favorites": [favorite.serialize() for favorite in self.favorites] if self.favorites else [],
        }

#  MANY-TO-MANY RELATIONSHIPS

# Relación muchos a muchos entre Characters y Episodes
character_episode = db.Table(
    'character_episode',
    db.Column('character_id', db.Integer, db.ForeignKey('characters.id'), primary_key=True),
    db.Column('episode_id', db.Integer, db.ForeignKey('episodes.id'), primary_key=True)
)

#  CHARACTER MODEL

class Character(db.Model):
    __tablename__ = 'characters'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(120), nullable=False)
    status = db.Column(db.String(50), nullable=False)
    species = db.Column(db.String(50), nullable=False)
    gender = db.Column(db.String(50), nullable=False)
    origin_id = db.Column(db.Integer, db.ForeignKey('locations.id'), nullable=True)
    location_id = db.Column(db.Integer, db.ForeignKey('locations.id'), nullable=True)
    image = db.Column(db.String(250), nullable=True)

    origin = relationship('Location', foreign_keys=[origin_id])
    location = relationship('Location', foreign_keys=[location_id])
    episodes = relationship('Episode', secondary=character_episode, back_populates='characters')

    def serialize(self):
        return {
            "id": self.id,
            "name": self.name,
            "status": self.status,
            "species": self.species,
            "gender": self.gender,
            "origin": self.origin.serialize() if self.origin else None,
            "location": self.location.serialize() if self.location else None,
            "image": self.image,
            "episodes": [episode.serialize() for episode in self.episodes] if self.episodes else [],
        }

# EPISODE MODEL

class Episode(db.Model):
    __tablename__ = 'episodes'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(120), nullable=False)
    air_date = db.Column(db.String(50), nullable=True)
    episode_code = db.Column(db.String(50), nullable=False)

    # Relación con Character (muchos a muchos)
    characters = db.relationship('Character', secondary=character_episode, back_populates='episodes')

    def serialize(self):
        return {
            "id": self.id,
            "name": self.name,
            "air_date": self.air_date,
            "episode_code": self.episode_code,
            "characters": [character.serialize() for character in self.characters] if self.characters else []
        }

# LOCATION MODEL

class Location(db.Model):
    __tablename__ = 'locations'
    id = db.Column(Integer, primary_key=True)
    name = db.Column(String(120), nullable=False)
    type = db.Column(String(50), nullable=True)
    dimension = db.Column(String(50), nullable=True)

    def serialize(self):
        return {
            "id": self.id,
            "name": self.name,
            "type": self.type,
            "dimension": self.dimension,
        }

# FAVORITE MODEL

class Favorite(db.Model):
    __tablename__ = 'favorites'
    id = db.Column(Integer, primary_key=True)
    user_id = db.Column(Integer, ForeignKey('users.id'), nullable=False)
    character_id = db.Column(Integer, ForeignKey('characters.id'), nullable=True)
    episode_id = db.Column(Integer, ForeignKey('episodes.id'), nullable=True)
    location_id = db.Column(Integer, ForeignKey('locations.id'), nullable=True)

    user = relationship('User', back_populates='favorites')
    character = relationship('Character')
    episode = relationship('Episode')
    location = relationship('Location')

    def serialize(self):
        return {
            "id": self.id,
            "user": self.user.email if self.user else None,  # Solo email por privacidad
            "character": self.character.serialize() if self.character else None,
            "episode": self.episode.serialize() if self.episode else None,
            "location": self.location.serialize() if self.location else None,
        }
