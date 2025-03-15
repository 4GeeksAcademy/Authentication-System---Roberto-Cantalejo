"""
This module takes care of starting the API Server, Loading the DB and Adding the endpoints
"""
from flask import Flask, request, jsonify, url_for, Blueprint
from api.models import db, User
from api.utils import generate_sitemap, APIException
from flask_cors import CORS
import bcrypt
from flask_jwt_extended import create_access_token,jwt_required, get_jwt_identity

api = Blueprint('api', __name__)

# Allow CORS requests to this API
CORS(api)


@api.route('/hello', methods=['POST', 'GET'])
def handle_hello():

    response_body = {
        "message": "Hello! I'm a message that came from the backend, check the network tab on the google inspector and you will see the GET request"
    }

    return jsonify(response_body), 200

@api.route('/signup', methods=['POST'])
def register_user():
    data = request.get_json()
    if data is None:
        return jsonify({"message": "Email and password are required"}), 400
    email = data['email']
    password = data['password']
    bytes = password.encode('utf-8') # Convertimos la contraseña en un array de bytes.
    salt = bcrypt.gensalt() # Generamos la sal
    hashed_password = bcrypt.hashpw(bytes, salt) # Sacamos la contraseña ya hasheada.
    new_user = User( # Creamos al nuevo usuario con su email y la contraseña hasheada.
        email = email,
        password = hashed_password,
        is_active = True
    )
    db.session.add(new_user) # Se prepara para añadir el nuevo usuario a la base de datos.
    db.session.commit() # Se añade al usuario a la base de datos.

    return jsonify({"message": "User registered successfully"}), 201

@api.route('/login', methods=['POST'])
def login_user():
    data = request.get_json()
    if data is None:
        return jsonify({"message": "Email and password are required"}), 400
    email = data['email']
    password = data['password']
    user = User.query.filter_by(email=email).first() # Filtramos en la tabla "User" y hacemos una consulta filtrando por mail, entregando el primero que encuentre.
    if user is None:
        return jsonify({"message": "User not found"}), 404 # En caso de que no encuentre el usuario, regresa un mensaje indicáncolo.
    bytes_password = password.encode('utf-8')
    if bcrypt.checkpw(bytes_password, user.password): # Esto compara la contraseña en bytes con la contraseña hasheada almacenada mediante checkpw
        access_token = create_access_token(identity=user.id) # Otorgamos un token de acceso si es correcta la contraseña.
        return jsonify({
            "message": "Login successful",
            "access_token": access_token
        }), 200
    else:
        return jsonify({"message": "Invalid password"}), 401
    
@api.route('/private', methods=['GET'])
@jwt_required()  # Esto hace que solo si estás autenticado puedas entrar a la ruta "/private"
def privated_user():
    user_id = get_jwt_identity() #Obtiene la identidad de quien entra mediante el token
    user = User.query.get(user_id) # Buscamos al usuario en la base de datos mediante el id
    if user is None:
        return jsonify({"message": "User not found"}), 404 # Si no existe el usuario se devuelve un error
    return jsonify({
        "message": "Nothing is true. Everything is permitted.", # Y si existe, manda esto.
        "user_email": user.email,
        "user_id": user.id
    }), 200