import os
from flask import Flask, request, jsonify
from flask_migrate import Migrate
from flask_cors import CORS
from werkzeug.security import generate_password_hash, check_password_hash
from utils import APIException, generate_sitemap
from admin import setup_admin
from models import db, User, Character, Episode, Location, Favorite
from flask_jwt_extended import create_access_token, get_jwt_identity, jwt_required, JWTManager

app = Flask(__name__)
app.url_map.strict_slashes = False

# Configuración de la base de datos
db_url = os.getenv("DATABASE_URL")
if db_url:
    app.config['SQLALCHEMY_DATABASE_URI'] = db_url.replace("postgres://", "postgresql://")
else:
    app.config['SQLALCHEMY_DATABASE_URI'] = "sqlite:///tmp/test.db"
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

MIGRATE = Migrate(app, db)
db.init_app(app)
CORS(app)
setup_admin(app)

# Configuración de JWT
app.config["JWT_SECRET_KEY"] = os.getenv("JWT_SECRET_KEY", "lynda2025")
jwt = JWTManager(app)

# Manejo de errores
@app.errorhandler(APIException)
def handle_invalid_usage(error):
    return jsonify(error.to_dict()), error.status_code

# Generación de sitemap
@app.route('/')
def sitemap():
    return generate_sitemap(app)

# Users

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
    if not data or not data.get("email") or not data.get("password"):
        return jsonify({"msg": "Email and password are required"}), 400

    hashed_password = generate_password_hash(data["password"])

    new_user = User(email=data["email"], password=hashed_password)
    db.session.add(new_user)
    db.session.commit()
    return jsonify(new_user.serialize()), 201

# Auth

@app.route("/login", methods=["POST"])
def login():
    email = request.json.get("email")
    password = request.json.get("password")

    if not email or not password:
        return jsonify({"msg": "Email and password are required"}), 400

    user = User.query.filter_by(email=email).first()
    if not user or not check_password_hash(user.password, password):
        return jsonify({"msg": "Invalid credentials"}), 401

    access_token = create_access_token(identity=email)
    return jsonify(access_token=access_token), 200

@app.route("/infoperfil", methods=["GET"])
@jwt_required()
def get_infoperfil():
    current_user = get_jwt_identity()
    return jsonify(logged_in_as=current_user), 200

# Characters

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
@jwt_required()
def create_character():
    data = request.json
    if not data:
        return jsonify({"msg": "No input data provided"}), 400

    new_character = Character(
        name=data.get("name"),
        status=data.get("status"),
        species=data.get("species"),
        gender=data.get("gender"),
        origin_id=data.get("origin_id"),
        location_id=data.get("location_id"),
        image=data.get("image")
    )
    db.session.add(new_character)
    db.session.commit()
    return jsonify(new_character.serialize()), 201

# Episodes

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
@jwt_required()
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

# Locations

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
@jwt_required()
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

# Favorites
@app.route('/users/<int:user_id>/favorites', methods=['POST'])
@jwt_required()
def add_favorite_to_user(user_id):
    user = User.query.get(user_id)
    if not user:
        return jsonify({"msg": "User not found"}), 404

    data = request.json
    if not data or not any([data.get("character_id"), data.get("episode_id"), data.get("location_id")]):
        return jsonify({"msg": "Invalid input"}), 400  # Verifica que al menos un ID esté presente

    existing_favorite = Favorite.query.filter_by(
        user_id=user_id, 
        character_id=data.get("character_id"),
        episode_id=data.get("episode_id"),
        location_id=data.get("location_id")
    ).first()
    
    if existing_favorite:
        return jsonify({"msg": "Favorite already added"}), 409

    new_favorite = Favorite(
        user_id=user_id,
        character_id=data.get("character_id"),
        episode_id=data.get("episode_id"),
        location_id=data.get("location_id")
    )
    db.session.add(new_favorite)
    db.session.commit()
    return jsonify(new_favorite.serialize()), 201

# Runer server

if __name__ == '__main__':
    PORT = int(os.environ.get('PORT', 3000))
    app.run(host='0.0.0.0', port=PORT, debug=False)
