from flask import request, make_response, jsonify
import jwt
from pymongo import MongoClient
from functools import wraps
import os

SECRET_KEY = os.getenv("SECRET_KEY") 

client = MongoClient()

db = client.books

blackListCollection = db.blackListCollection

def admin(func):
    @wraps(func)
    def admin_required_wrapper(*args, **kwargs):
        token = request.headers['x-access-token']
        data = jwt.decode(token, SECRET_KEY, algorithms="HS256")
        if data["role"] == "admin":
            return func(*args, **kwargs)
        else:
            return make_response(jsonify({"message": "Admin access required"}), 401)
    return admin_required_wrapper
