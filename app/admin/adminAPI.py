from flask import request, make_response, Blueprint
from pymongo import MongoClient
from bson.json_util import dumps
from bson.objectid import ObjectId
import os
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

admin_api = Blueprint("admin_api", __name__)

@admin_api.route(f'{API_VER_PATH_V1}/user-actions', methods=['GET'])
@verify_token
@admin 
def get_all_user_actions():    
    return make_response(dumps(activityCollection.find({})), 200)

@admin_api.route(f'{API_VER_PATH_V1}/user-actions/login', methods=['GET'])
@verify_token
@admin 
def get_user_logins():    
    return make_response(dumps(activityCollection.find({"Action": "User Login"})), 200)

