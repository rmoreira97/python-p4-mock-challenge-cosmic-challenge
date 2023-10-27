#!/usr/bin/env python3

from models import db, Scientist, Mission, Planet
from flask_restful import Api, Resource
from flask_migrate import Migrate
from flask import Flask, make_response, jsonify, request
import os

BASE_DIR = os.path.abspath(os.path.dirname(__file__))
DATABASE = os.environ.get("DB_URI", f"sqlite:///{os.path.join(BASE_DIR, 'app.db')}")

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = DATABASE
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.json.compact = False

migrate = Migrate(app, db)
db.init_app(app)

@app.route('/scientists', methods=['GET'])
def get_scientists():
    scientists = Scientist.query.all()
    return jsonify([scientist.to_dict(only=('id', 'name', 'field_of_study')) for scientist in scientists])

@app.route('/scientists/<int:id>', methods=['GET'])
def get_scientist_by_id(id):
    scientist = db.session.get(Scientist, id)
    if not scientist:
        return jsonify({"error": "Scientist not found"}), 404
    data = scientist.to_dict()
    data['missions'] = [mission.to_dict() for mission in scientist.missions]
    return jsonify(data)

@app.route('/scientists', methods=['POST'])
def create_scientist():
    data = request.json
    name = data.get('name')
    field_of_study = data.get('field_of_study')

    if not name or not field_of_study:
        return jsonify({"errors": ["validation errors"]}), 400

    scientist = Scientist(name=name, field_of_study=field_of_study)
    db.session.add(scientist)
    db.session.commit()

    return jsonify(scientist.to_dict()), 201

@app.route('/scientists/<int:id>', methods=['PATCH'])
def update_scientist(id):
    scientist = db.session.get(Scientist, id)
    if not scientist:
        return jsonify({"error": "Scientist not found"}), 404

    data = request.json
    name = data.get('name')
    field_of_study = data.get('field_of_study')

    if not name or not field_of_study:
        return jsonify({"errors": ["validation errors"]}), 400

    scientist.name = name
    scientist.field_of_study = field_of_study

    db.session.commit()

    return jsonify(scientist.to_dict()), 202

@app.route('/scientists/<int:id>', methods=['DELETE'])
def delete_scientist(id):
    scientist = db.session.get(Scientist, id)
    if not scientist:
        return jsonify({"error": "Scientist not found"}), 404

    db.session.delete(scientist)
    db.session.commit()

    return jsonify({}), 204

@app.route('/planets', methods=['GET'])
def get_planets():
    planets = Planet.query.all()
    return jsonify([planet.to_dict(only=('id', 'name', 'distance_from_earth', 'nearest_star')) for planet in planets])

@app.route('/missions', methods=['POST'])
def create_mission():
    data = request.json
    name = data.get('name')
    scientist_id = data.get('scientist_id')
    planet_id = data.get('planet_id')

    if not name or not scientist_id or not planet_id:
        return jsonify({"errors": ["validation errors"]}), 400

    mission = Mission(name=name, scientist_id=scientist_id, planet_id=planet_id)
    db.session.add(mission)
    db.session.commit()

    response_data = mission.to_dict()
    response_data['scientist_id'] = mission.scientist_id
    response_data['planet_id'] = mission.planet_id

    return jsonify(response_data), 201

@app.route('/')
def home():
    return ''

if __name__ == '__main__':
    app.run(port=5555, debug=True)