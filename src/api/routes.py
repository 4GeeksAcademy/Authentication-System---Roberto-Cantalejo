"""
This module takes care of starting the API Server, Loading the DB and Adding the endpoints
"""
from flask import Flask, request, jsonify, url_for, Blueprint
from api.models import db, User
from api.utils import generate_sitemap, APIException
from flask_cors import CORS

api = Blueprint('api', __name__)

# Allow CORS requests to this API
CORS(api)


@api.route('/hello', methods=['POST', 'GET'])
def handle_hello():

    response_body = {
        "message": "Hello! I'm a message that came from the backend, check the network tab on the google inspector and you will see the GET request"
    }

    return jsonify(response_body), 200

@api.route('/register', methods=['POST'])
def register_user():
    data = request.get_json()
    if data is None:
        return jsonify({"message": "Email and password are required"}), 400
    new_user = User(
        email=data['email'],
        password=data['password'],
    )

    # Añade el usuario a la base de datos
    db.session.add(new_user)
    db.session.commit()

    return jsonify({"message": "User registered successfully"}), 200