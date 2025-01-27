"""
This module takes care of starting the API Server, Loading the DB and Adding the endpoints
"""
import os
from flask import Flask, request, jsonify, url_for
from flask_migrate import Migrate
from flask_swagger import swagger
from flask_cors import CORS
from utils import APIException, generate_sitemap
from admin import setup_admin
from models import db, User, Character, Episode, Location, Favorite  # Importar modelos


app = Flask(__name__)
app.url_map.strict_slashes = False

# Config base de datos
db_url = os.getenv("DATABASE_URL")
if db_url is not None:
    app.config['SQLALCHEMY_DATABASE_URI'] = db_url.replace("postgres://", "postgresql://")
else:
    app.config['SQLALCHEMY_DATABASE_URI'] = "sqlite:////tmp/test.db"
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

MIGRATE = Migrate(app, db)
db.init_app(app)
CORS(app)
setup_admin(app)

# Handle/serialize errors like a JSON object
@app.errorhandler(APIException)
def handle_invalid_usage(error):
    return jsonify(error.to_dict()), error.status_code

# generate sitemap with all your endpoints
@app.route('/')
def sitemap():
    return generate_sitemap(app)

# Endpoints para User
@app.route('/users', methods=['GET'])
def get_users():
    users = User.query.all()
    return jsonify([user.serialize() for user in users]), 200

@app.route('/users/<int:id>', methods=['GET'])
def get_user(id):
    user = User.query.get(id)
    if not user:
        return jsonify({"msg": "User not found"}), 404
    return jsonify(user.serialize()), 200

@app.route('/users', methods=['POST'])
def create_user():
    data = request.json
    if not data:
        return jsonify({"msg": "No input data provided"}), 400

    new_user = User(
        username=data.get("username"),
        email=data.get("email"),
        password=data.get("password")  # "si es real se ecrp"
    )
    db.session.add(new_user)
    db.session.commit()
    return jsonify(new_user.serialize()), 201

@app.route('/users/<int:id>', methods=['PUT'])
def update_user(id):
    user = User.query.get(id)
    if not user:
        return jsonify({"msg": "User not found"}), 404

    data = request.json
    user.username = data.get("username", user.username)
    user.email = data.get("email", user.email)
    user.password = data.get("password", user.password)  # # "si es real se ecrp"

    db.session.commit()
    return jsonify(user.serialize()), 200

@app.route('/users/<int:id>', methods=['DELETE'])
def delete_user(id):
    user = User.query.get(id)
    if not user:
        return jsonify({"msg": "User not found"}), 404

    db.session.delete(user)
    db.session.commit()
    return jsonify({"msg": f"User with ID {id} deleted"}), 200

# Endpoints para manejar favoritos de un usuario
@app.route('/users/<int:user_id>/favorites', methods=['GET'])
def get_user_favorites(user_id):
    user = User.query.get(user_id)
    if not user:
        return jsonify({"msg": "User not found"}), 404

    return jsonify([favorite.serialize() for favorite in user.favorites]), 200

@app.route('/users/<int:user_id>/favorites', methods=['POST'])
def add_favorite_to_user(user_id):
    user = User.query.get(user_id)
    if not user:
        return jsonify({"msg": "User not found"}), 404

    data = request.json
    if not data:
        return jsonify({"msg": "No input data provided"}), 400

    new_favorite = Favorite(
        user_id=user_id,
        character_id=data.get("character_id"),
        episode_id=data.get("episode_id"),
        location_id=data.get("location_id")
    )
    db.session.add(new_favorite)
    db.session.commit()
    return jsonify(new_favorite.serialize()), 201

@app.route('/users/<int:user_id>/favorites/<int:favorite_id>', methods=['DELETE'])
def remove_favorite_from_user(user_id, favorite_id):
    user = User.query.get(user_id)
    if not user:
        return jsonify({"msg": "User not found"}), 404

    favorite = Favorite.query.get(favorite_id)
    if not favorite or favorite.user_id != user_id:
        return jsonify({"msg": "Favorite not found or not associated with this user"}), 404

    db.session.delete(favorite)
    db.session.commit()
    return jsonify({"msg": f"Favorite {favorite_id} removed from User {user_id}"}), 200

# Characters Endpoints
@app.route('/characters', methods=['GET'])
def get_characters():
    characters = Character.query.all()
    return jsonify([character.serialize() for character in characters]), 200

@app.route('/characters/<int:id>', methods=['GET'])
def get_character(id):
    character = Character.query.get(id)
    if not character:
        return jsonify({"msg": "Character not found"}), 404
    return jsonify(character.serialize()), 200

@app.route('/characters', methods=['POST'])
def create_character():
    data = request.json
    if not data:
        return jsonify({"msg": "No input data provided"}), 400

    new_character = Character(
        name=data.get("name"),
        status=data.get("status"),
        species=data.get("species"),
        gender=data.get("gender"),
        origin=data.get("origin"),
        location=data.get("location"),
        image=data.get("image")
    )
    db.session.add(new_character)
    db.session.commit()
    return jsonify(new_character.serialize()), 201

@app.route('/characters/<int:id>', methods=['PUT'])
def update_character(id):
    character = Character.query.get(id)
    if not character:
        return jsonify({"msg": "Character not found"}), 404

    data = request.json
    character.name = data.get("name", character.name)
    character.status = data.get("status", character.status)
    character.species = data.get("species", character.species)
    character.gender = data.get("gender", character.gender)
    character.origin = data.get("origin", character.origin)
    character.location = data.get("location", character.location)
    character.image = data.get("image", character.image)

    db.session.commit()
    return jsonify(character.serialize()), 200

@app.route('/characters/<int:id>', methods=['DELETE'])
def delete_character(id):
    character = Character.query.get(id)
    if not character:
        return jsonify({"msg": "Character not found"}), 404

    db.session.delete(character)
    db.session.commit()
    return jsonify({"msg": f"Character with ID {id} deleted"}), 200

# Episodes Endpoints
@app.route('/episodes', methods=['GET'])
def get_episodes():
    episodes = Episode.query.all()
    return jsonify([episode.serialize() for episode in episodes]), 200

@app.route('/episodes/<int:id>', methods=['GET'])
def get_episode(id):
    episode = Episode.query.get(id)
    if not episode:
        return jsonify({"msg": "Episode not found"}), 404
    return jsonify(episode.serialize()), 200

@app.route('/episodes', methods=['POST'])
def create_episode():
    data = request.json
    if not data:
        return jsonify({"msg": "No input data provided"}), 400

    new_episode = Episode(
        name=data.get("name"),
        air_date=data.get("air_date"),
        episode_code=data.get("episode_code")
    )
    db.session.add(new_episode)
    db.session.commit()
    return jsonify(new_episode.serialize()), 201

@app.route('/episodes/<int:id>', methods=['PUT'])
def update_episode(id):
    episode = Episode.query.get(id)
    if not episode:
        return jsonify({"msg": "Episode not found"}), 404

    data = request.json
    episode.name = data.get("name", episode.name)
    episode.air_date = data.get("air_date", episode.air_date)
    episode.episode_code = data.get("episode_code", episode.episode_code)

    db.session.commit()
    return jsonify(episode.serialize()), 200

@app.route('/episodes/<int:id>', methods=['DELETE'])
def delete_episode(id):
    episode = Episode.query.get(id)
    if not episode:
        return jsonify({"msg": "Episode not found"}), 404

    db.session.delete(episode)
    db.session.commit()
    return jsonify({"msg": f"Episode with ID {id} deleted"}), 200

# Locations Endpoints
@app.route('/locations', methods=['GET'])
def get_locations():
    locations = Location.query.all()
    return jsonify([location.serialize() for location in locations]), 200

@app.route('/locations/<int:id>', methods=['GET'])
def get_location(id):
    location = Location.query.get(id)
    if not location:
        return jsonify({"msg": "Location not found"}), 404
    return jsonify(location.serialize()), 200

@app.route('/locations', methods=['POST'])
def create_location():
    data = request.json
    if not data:
        return jsonify({"msg": "No input data provided"}), 400

    new_location = Location(
        name=data.get("name"),
        type=data.get("type"),
        dimension=data.get("dimension")
    )
    db.session.add(new_location)
    db.session.commit()
    return jsonify(new_location.serialize()), 201

@app.route('/locations/<int:id>', methods=['PUT'])
def update_location(id):
    location = Location.query.get(id)
    if not location:
        return jsonify({"msg": "Location not found"}), 404

    data = request.json
    location.name = data.get("name", location.name)
    location.type = data.get("type", location.type)
    location.dimension = data.get("dimension", location.dimension)

    db.session.commit()
    return jsonify(location.serialize()), 200

@app.route('/locations/<int:id>', methods=['DELETE'])
def delete_location(id):
    location = Location.query.get(id)
    if not location:
        return jsonify({"msg": "Location not found"}), 404

    db.session.delete(location)
    db.session.commit()
    return jsonify({"msg": f"Location with ID {id} deleted"}), 200

# Favorites Endpoints
@app.route('/favorites', methods=['GET'])
def get_favorites():
    favorites = Favorite.query.all()
    return jsonify([favorite.serialize() for favorite in favorites]), 200

@app.route('/favorites', methods=['POST'])
def create_favorite():
    data = request.json
    new_favorite = Favorite(
        user_id=data.get("user_id"),
        character_id=data.get("character_id"),
        episode_id=data.get("episode_id"),
        location_id=data.get("location_id")
    )
    db.session.add(new_favorite)
    db.session.commit()
    return jsonify(new_favorite.serialize()), 201

@app.route('/favorites/<int:id>', methods=['DELETE'])
def delete_favorite(id):
    favorite = Favorite.query.get(id)
    if not favorite:
        return jsonify({"msg": "Favorite not found"}), 404

    db.session.delete(favorite)
    db.session.commit()
    return jsonify({"msg": f"Favorite with ID {id} deleted"}), 200

# Corre app
if __name__ == '__main__':
    PORT = int(os.environ.get('PORT', 3000))
    app.run(host='0.0.0.0', port=PORT, debug=False)
