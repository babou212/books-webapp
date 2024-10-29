from flask import request, make_response, jsonify
import jwt
from pymongo import MongoClient
from functools import wraps
import os

SECRET_KEY = os.getenv("SECRET_KEY") 

client = MongoClient()

db = client.books

blackListCollection = db.blackListCollection

def verify_token(func):
    @wraps(func)
    def jwt_wrapper(*args, **kwargs):
        jwt_token = None
        if "x-access-token" in request.headers:
            jwt_token = request.headers["x-access-token"]
        if not jwt_token:
            return make_response(jsonify({"Error": "Missing token"}), 401)
        try:
            data = jwt.decode(jwt_token, SECRET_KEY, algorithms="HS256")
        except: 
            return make_response(jsonify({"Error": "Token is invalid"}), 401)
        black_list_token = blackListCollection.find_one({"token": jwt_token})
        if black_list_token is not None:
            return make_response(jsonify({"Message": "Token has been invalidated"}), 401)
        return func(*args, **kwargs)
    return jwt_wrapper
