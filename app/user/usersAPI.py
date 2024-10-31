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

@users_api.route(f'{API_VER_PATH_V1}/users', methods=['GET'])
@verify_token
@admin
def get_all_users():
    no_of_docs_each_page = request.args.get("mn", "")
    current_page_number =  request.args.get("pn", "")

    if no_of_docs_each_page and current_page_number:
        return make_response(dumps(userCollection.find({})
                                .skip(int(no_of_docs_each_page) * (int(current_page_number)-1))
                                .limit(int(no_of_docs_each_page))), 200)

    return make_response(dumps(userCollection.find({})))

@users_api.route(f'{API_VER_PATH_V1}/users/<id>', methods=['GET'])
@verify_token
def get_user(id):
    jwt_token = request.headers["x-access-token"]
    data = jwt.decode(jwt_token, SECRET_KEY, algorithms="HS256")

    user = userCollection.find_one({'_id': ObjectId(id)})

    if data["user"] == user["username"]: 
        return make_response(dumps(user), 200)
    
    return make_response(dumps({"Error": "Unauthorized"}), 401)

@users_api.route(f'{API_VER_PATH_V1}/logout', methods=['GET'])
@verify_token
def logout():
    jwt_token = request.headers["x-access-token"]

    blackListCollection.insert_one({"token": jwt_token})
    return make_response(jsonify({"Message": "logout Successful"}), 200)

@users_api.route(f'{API_VER_PATH_V1}/users/', methods=['POST'])
@verify_token
@admin
def create_new_user():
    data = request.json

    if data:
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

    if data: 
        user = userCollection.find_one({"username": data.get("username")})

        if not user:
            return make_response({"Error": "Non valid username"}, 401)
            
        if bcrypt.checkpw(bytes(data.get("password"), "UTF-8"), user["password"]):
            token = jwt.encode({
                "user": data.get("username"),
                "exp": datetime.now() + timedelta(minutes=30),
                "role": user["role"]
            }, SECRET_KEY, algorithm="HS256")

            return make_response(jsonify({"token": token}), 200)
            
    return make_response(dumps({"Error": "Username or Password incorrect, try again"}), 401)

@users_api.route(f'{API_VER_PATH_V1}/users/reserve/<id>', methods=['PUT'])
@verify_token
def reserve_book(id):
    if ObjectId.is_valid(id):
        query = { "_id": ObjectId(id) }
    else:
        query = { "_id": int(id) }

    jwt_token = request.headers["x-access-token"]

    if jwt_token:
        jwt_data = jwt.decode(jwt_token, SECRET_KEY, algorithms="HS256")
        book = bookCollection.find_one(query)

        filter = {"username": jwt_data["user"]}

        value = {"$push": {"books": book} }

        userCollection.update_one(filter, value)
        return make_response(dumps({"Reserved": book}), 201)
    
    return make_response({"Error": "Invalid request"}, 400)

@users_api.route(f'{API_VER_PATH_V1}/users/reserve/<id>', methods=['DELETE'])
@verify_token
def unreserve_book(id):
    jwt_token = request.headers["x-access-token"]
    user_id = jwt.decode(jwt_token, SECRET_KEY, algorithms="HS256")

    if ObjectId.is_valid(id):
        delete_query = {"$pull": { "books": {"_id": ObjectId(id)}}}
        deleted_obj = ObjectId(id)
    else:
        delete_query = {"$pull": { "books": {"_id": int(id)}}}
        deleted_obj = int(id)

    query = {"username": user_id["user"]}

    userCollection.update_one(query, delete_query)
    return make_response(dumps({"Unreserved": deleted_obj}), 200)
