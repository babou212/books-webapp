from flask_cors import cross_origin
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
activityCollection = db.activityCollection

users_api = Blueprint("users_api", __name__)

@users_api.route(f'{API_VER_PATH_V1}/users', methods=['GET'])
@verify_token
@admin
def get_all_users():
    no_of_docs_each_page = request.args.get("ps", "")
    current_page_number =  request.args.get("pn", "")

    if no_of_docs_each_page and current_page_number:
        return make_response(dumps(userCollection.find({})
                                .skip(int(no_of_docs_each_page) * (int(current_page_number)-1))
                                .limit(int(no_of_docs_each_page))), 200)

    return make_response(dumps(userCollection.find({})))

@users_api.route(f'{API_VER_PATH_V1}/users/<id>', methods=['GET'])
@verify_token
def get_user_by_id(id):
    jwt_token = request.headers["x-access-token"]
    data = jwt.decode(jwt_token, SECRET_KEY, algorithms="HS256")

    user = userCollection.find_one({'_id': ObjectId(id)})

    if data["user"] == user["username"]: 
        return make_response(dumps(user), 200)
    
    return make_response(dumps({"Error": "Unauthorized"}), 401)

@users_api.route(f'{API_VER_PATH_V1}/user', methods=['GET'])
@verify_token
def get_user():
    jwt_token = request.headers["x-access-token"]
    data = jwt.decode(jwt_token, SECRET_KEY, algorithms="HS256")

    user = userCollection.find_one({"username": data["user"]})

    if data["user"]: 
        return make_response(dumps(user), 200)
    
    return make_response(dumps({"Error": "Unauthorized"}), 401)

@users_api.route(f'{API_VER_PATH_V1}/users/amount', methods=['GET'])
@verify_token
def get_amount_owed():
    jwt_token = request.headers["x-access-token"]
    data = jwt.decode(jwt_token, SECRET_KEY, algorithms="HS256")
    user = userCollection.find_one({"username": data["user"]})

    amount = user["amountOwed"]

    return make_response(jsonify(amount), 200)

@users_api.route(f'{API_VER_PATH_V1}/users/', methods=['POST'])
def create_new_user():
    data = request.json

    if data:
        user = userCollection.find_one({"username": data.get("username")})

        if user:
            return make_response(dumps({"Error": "Username already taken"}), 401)

        new_user = {
        "_id" : ObjectId(),
        "username" : data.get("username"),
        "password" : bytes(data.get("password"), encoding='utf8'),
        "role" : "user",
        "amountOwed": 0,
        "books" : []
        }

        new_user["password"] = bcrypt.hashpw(new_user["password"], bcrypt.gensalt())

        activity = {
            "Action": "New User Created",
            "user": new_user["username"],
            "id": new_user["_id"]
        }

        activityCollection.insert_one(activity)
        userCollection.insert_one(new_user)
        return make_response(dumps(userCollection.find_one({'_id': new_user["_id"]})), 201)
    
    return make_response(dumps({"Error": "JSON Object not provided"}), 400)

@users_api.route(f'{API_VER_PATH_V1}/users/<id>/', methods=['DELETE'])
@verify_token
@admin 
def delete_user(id):
    query = {"_id": ObjectId(id)}

    activity = {
            "Action": "User Deleted",
            "_id": ObjectId(id)
        }

    activityCollection.insert_one(activity)
    userCollection.delete_one(query)
    return make_response(dumps({"Deleted user": ObjectId(id)}), 200)

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

            activity = {
            "Action": "User Login",
            "user": data.get("username"),
            "Status": "Successful"
            }

            activityCollection.insert_one(activity)
            return make_response(jsonify(token), 200)
        
    activity = {
        "Action": "User Login",
        "user": data.get("username"),
        "Status": "Failure"
        }

    activityCollection.insert_one(activity)        
    return make_response(dumps({"Error": "Username or Password incorrect, try again"}), 401)

@users_api.route(f'{API_VER_PATH_V1}/logout', methods=['GET'])
@verify_token
def logout():
    jwt_token = request.headers["x-access-token"]

    blackListCollection.insert_one({"token": jwt_token})
    return make_response(jsonify({"Message": "logout Successful"}), 200)

@users_api.route(f'{API_VER_PATH_V1}/users/reserve/<id>', methods=['PUT'])
@verify_token
def reserve_book(id):
    jwt_token = request.headers["x-access-token"]

    if jwt_token:
        jwt_data = jwt.decode(jwt_token, SECRET_KEY, algorithms="HS256")
        query = {"_id": ObjectId(id)}
        book = bookCollection.find_one(query)

        if book["reserved"] == False:
            bookCollection.update_one(query, {"$set": {"reserved": True}})
            filter = {"username": jwt_data["user"]}
            
            user = userCollection.find_one(filter)

            amount_to_add = user["amountOwed"] + book["price"]

            book_value = {"$push": {"books": book}}
            cost_value = {"$set": {"amountOwed": amount_to_add}}

            activity = {
            "Action": "Book Reserved",
            "user": jwt_data["user"],
            "Book_id": book["_id"] 
            }

            activityCollection.insert_one(activity)
            userCollection.update_one(filter, book_value)
            userCollection.update_one(filter, cost_value)
            return make_response(dumps({"Reserved": book}), 201)
        
        return make_response(dumps({"Error": "Book has already been reserved"}), 400)
    
    return make_response({"Error": "Invalid request"}, 400)

@users_api.route(f'{API_VER_PATH_V1}/users/reserve/<id>', methods=['DELETE'])
@verify_token
def unreserve_book(id):
    jwt_token = request.headers["x-access-token"]
    user_id = jwt.decode(jwt_token, SECRET_KEY, algorithms="HS256")

    delete_query = {"$pull": {"books": {"_id": ObjectId(id)}}}
    deleted_obj = ObjectId(id)

    bookCollection.update_one({"_id": ObjectId(id)}, {"$set": {"reserved": False}})

    book = bookCollection.find_one({"_id": ObjectId(id)})
    user = userCollection.find_one({"username": user_id["user"]})

    amount_to_add = user["amountOwed"] - book["price"]

    cost_value = {"$set": {"amountOwed": amount_to_add}}

    query = {"username": user_id["user"]}

    activity = {
            "Action": "Book Unreserved",
            "user": user_id["user"],
            "Book_id": ObjectId(id)
            }

    activityCollection.insert_one(activity)
    userCollection.update_one(query, delete_query)
    userCollection.update_one(query, cost_value)
    return make_response(dumps({"Unreserved": deleted_obj}), 200)
