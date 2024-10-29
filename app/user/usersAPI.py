from flask import request, make_response, jsonify, Blueprint
from pymongo import MongoClient
from bson.json_util import dumps
from bson.objectid import ObjectId
import jwt
from datetime import datetime, timedelta
import os
import bcrypt
from decorators.admin import admin
from decorators.verify import verify_token

SECRET_KEY = os.getenv("SECRET_KEY") 
API_VER_PATH_V1 = "/api/v1/"

client = MongoClient()

db = client.books
bookCollection = db.booksCollection
userCollection = db.userCollection
blackListCollection = db.blackListCollection

users_api = Blueprint("users_api", __name__)

@users_api.route(f'{API_VER_PATH_V1}/users/', methods=['GET'])
@verify_token
@admin
def get_all_users():
    return make_response(dumps(userCollection.find({})), 200)

@users_api.route(f'{API_VER_PATH_V1}/users/<id>', methods=['GET'])
@verify_token
@admin
def get_user(id):
    return make_response(dumps(userCollection.find_one({'_id': ObjectId(id)})), 200)

@users_api.route(f'{API_VER_PATH_V1}/logout', methods=['GET'])
@verify_token
def logout():
    jwt_token = jwt.decode(request.headers["x-access-token"], SECRET_KEY, algorithms="HS256")
    blackListCollection.insert_one({"token": jwt_token})
    return make_response(jsonify({"Message": "logout Successful"}), 200)

@users_api.route(f'{API_VER_PATH_V1}/users/', methods=['POST'])
@verify_token
@admin
def create_new_user():

        data = request.json

        if not data:

            new_user = {
            "_id" : ObjectId(),
            "username" : data.get("username"),
            "password" : bytes(data.get("password"), encoding='utf8'),
            "role" : "user",
            "books" : [],
            }

            new_user["password"] = bcrypt.hashpw(new_user["password"], bcrypt.gensalt())

            userCollection.insert_one(new_user)
            return make_response(dumps(userCollection.find_one({'_id': new_user["_id"] })), 201)
        
        return make_response(dumps({"Error": "JSON Object not provided"}), 400)

@users_api.route(f'{API_VER_PATH_V1}/login/', methods=['POST'])
def user_login():
    data = request.json

    if not data: 

        user = userCollection.find_one({"username": data.get("username")})

        if not user:
            return make_response({"Error": "Non valid user"}, 401)
            
        if bcrypt.checkpw(bytes(data.get("password"), "UTF-8"), user["password"]):
            token = jwt.encode({
                "user": data.get("username"),
                "exp": datetime.now() + timedelta(minutes=30),
                "role": user["role"]
            }, SECRET_KEY, algorithm="HS256")

            return make_response(jsonify({"token": token}), 201)
        
        return make_response({}, 401)
    
    return make_response(dumps({"Error": "JSON Object not provided"}), 400)