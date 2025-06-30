import os
from flask import Flask, jsonify, request
from flask_migrate import Migrate
from flask_cors import CORS
from utils import APIException, generate_sitemap
from admin import setup_admin
from models import db, User, Character, Planet, Favorite

app = Flask(__name__)
app.url_map.strict_slashes = False

app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv(
    'DATABASE_URL', 'sqlite:///database.db')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db.init_app(app)
MIGRATE = Migrate(app, db)
CORS(app)
setup_admin(app)


@app.errorhandler(APIException)
def handle_invalid_usage(error):
    return jsonify(error.to_dict()), error.status_code


@app.route('/')
def sitemap():
    return generate_sitemap(app)


@app.route('/people', methods=['GET'])
def get_people():
    characters = Character.query.all()
    results = [char.serialize() for char in characters]
    return jsonify(results), 200


@app.route('/people/<int:people_id>', methods=['GET'])
def get_person(people_id):
    char = Character.query.get(people_id)
    if char is None:
        return jsonify({"error": "Character not found"}), 404
    return jsonify(char.serialize()), 200


@app.route('/planets', methods=['GET'])
def get_planets():
    planets = Planet.query.all()
    results = [planet.serialize() for planet in planets]
    return jsonify(results), 200


@app.route('/planets/<int:planet_id>', methods=['GET'])
def get_planet(planet_id):
    planet = Planet.query.get(planet_id)
    if planet is None:
        return jsonify({"error": "Planet not found"}), 404
    return jsonify(planet.serialize()), 200


@app.route('/users', methods=['GET'])
def get_users():
    users = User.query.all()
    results = [user.serialize() for user in users]
    return jsonify(results), 200


@app.route('/users/favorites', methods=['GET'])
def get_user_favorites():
    user = User.query.get(1)
    if user is None:
        return jsonify({"error": "User not found"}), 404
    favorites = Favorite.query.filter_by(user_id=user.id).all()
    results = [fav.serialize() for fav in favorites]
    return jsonify(results), 200


@app.route('/favorite/planet/<int:planet_id>', methods=['POST'])
def add_favorite_planet(planet_id):
    user = User.query.get(1)
    if user is None:
        return jsonify({"error": "User not found"}), 404
    planet = Planet.query.get(planet_id)
    if planet is None:
        return jsonify({"error": "Planet not found"}), 404
    existing_fav = Favorite.query.filter_by(user_id=user.id, planet_id=planet.id).first()
    if existing_fav:
        return jsonify({"message": "Favorite already exists"}), 400
    favorite = Favorite(user_id=user.id, planet_id=planet.id)
    db.session.add(favorite)
    db.session.commit()
    return jsonify(favorite.serialize()), 201


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=int(os.getenv('PORT', 3000)), debug=True)