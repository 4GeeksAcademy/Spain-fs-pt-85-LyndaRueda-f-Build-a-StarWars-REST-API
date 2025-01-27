from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import mapped_column
from sqlalchemy import Integer, String, Boolean


db = SQLAlchemy()

# Tabla intermedia para la relación muchos a muchos entre Users y Favorites
user_favorite = db.Table(
    'user_favorite',
    db.Column('user_id', db.Integer, db.ForeignKey('users.id'), primary_key=True),
    db.Column('favorite_id', db.Integer, db.ForeignKey('favorites.id'), primary_key=True)
)

# Modelo User
class User(db.Model):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String(120), nullable=False)

    # Relación muchos a muchos con la tabla intermedia
    favorites = db.relationship('Favorite', secondary=user_favorite, backref='users')

    def serialize(self):
        return {
            "id": self.id,
            "username": self.username,
            "email": self.email,
            "favorites": [favorite.serialize() for favorite in self.favorites],
        }

# Relación muchos a muchos Characters y Episodes
character_episode = db.Table(
    'character_episode',
    db.Column('character_id', db.Integer, db.ForeignKey('characters.id'), primary_key=True),
    db.Column('episode_id', db.Integer, db.ForeignKey('episodes.id'), primary_key=True)
)

# Modelo Character
class Character(db.Model):
    __tablename__ = 'characters'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(120), nullable=False)
    status = db.Column(db.String(50), nullable=False)
    species = db.Column(db.String(50), nullable=False)
    gender = db.Column(db.String(50), nullable=False)
    origin = db.Column(db.String(120), nullable=True)
    location = db.Column(db.String(120), nullable=True)
    image = db.Column(db.String(250), nullable=True)

    episodes = db.relationship('Episode', secondary=character_episode, backref='characters')

    def serialize(self):
        return {
            "id": self.id,
            "name": self.name,
            "status": self.status,
            "species": self.species,
            "gender": self.gender,
            "origin": self.origin,
            "location": self.location,
            "image": self.image,
            "episodes": [episode.serialize() for episode in self.episodes],
        }

# Modelo Episode
class Episode(db.Model):
    __tablename__ = 'episodes'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(120), nullable=False)
    air_date = db.Column(db.String(50), nullable=True)
    episode_code = db.Column(db.String(50), nullable=False)

    def serialize(self):
        return {
            "id": self.id,
            "name": self.name,
            "air_date": self.air_date,
            "episode_code": self.episode_code,
        }

# Modelo Location
class Location(db.Model):
    __tablename__ = 'locations'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(120), nullable=False)
    type = db.Column(db.String(50), nullable=True)
    dimension = db.Column(db.String(50), nullable=True)

    def serialize(self):
        return {
            "id": self.id,
            "name": self.name,
            "type": self.type,
            "dimension": self.dimension,
        }

# Modelo Favorite
class Favorite(db.Model):
    __tablename__ = 'favorites'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    character_id = db.Column(db.Integer, db.ForeignKey('characters.id'), nullable=True)
    episode_id = db.Column(db.Integer, db.ForeignKey('episodes.id'), nullable=True)
    location_id = db.Column(db.Integer, db.ForeignKey('locations.id'), nullable=True)

    user = db.relationship('User', back_populates='favorites')
    character = db.relationship('Character')
    episode = db.relationship('Episode')
    location = db.relationship('Location')

    def serialize(self):
        return {
            "id": self.id,
            "user_id": self.user_id,
            "character": self.character.serialize() if self.character else None,
            "episode": self.episode.serialize() if self.episode else None,
            "location": self.location.serialize() if self.location else None,
        }
