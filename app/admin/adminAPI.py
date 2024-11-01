from flask import make_response, Blueprint
from pymongo import MongoClient
from bson.json_util import dumps
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

@admin_api.route(f'{API_VER_PATH_V1}/user-actions/login/fail', methods=['GET'])
@verify_token
@admin 
def get_failed_user_logins():    
    return make_response(dumps(activityCollection.find({"Status": "Failure"})), 200)

@admin_api.route(f'{API_VER_PATH_V1}/user-actions/user-deleted', methods=['GET'])
@verify_token
@admin 
def get_user_deleted():    
    return make_response(dumps(activityCollection.find({"Action": "User Deleted"})), 200)

@admin_api.route(f'{API_VER_PATH_V1}/user-actions/user-created', methods=['GET'])
@verify_token
@admin 
def get_user_created():    
    return make_response(dumps(activityCollection.find({"Action": "New User Created"})), 200)

@admin_api.route(f'{API_VER_PATH_V1}/user-actions/login/success', methods=['GET'])
@verify_token
@admin 
def get_successful_user_logins():    
    return make_response(dumps(activityCollection.find({"Status": "Successful"})), 200)

@admin_api.route(f'{API_VER_PATH_V1}/user-actions/reserved', methods=['GET'])
@verify_token
@admin 
def get_books_reserved_activity():    
    return make_response(dumps(activityCollection.find({"Action": "Book Reserved"})), 200)

@admin_api.route(f'{API_VER_PATH_V1}/user-actions/unreserved', methods=['GET'])
@verify_token
@admin 
def get_books_unreserved_activity():    
    return make_response(dumps(activityCollection.find({"Action": "Book Unreserved"})), 200)

@admin_api.route(f'{API_VER_PATH_V1}/user-actions/book-deleted', methods=['GET'])
@verify_token
@admin 
def get_book_deleted_activity():    
    return make_response(dumps(activityCollection.find({"Action": "Book Deleted"})), 200)

@admin_api.route(f'{API_VER_PATH_V1}/user-actions/book-updated', methods=['GET'])
@verify_token
@admin 
def get_book_updated_activity():    
    return make_response(dumps(activityCollection.find({"Action": "Book Updated"})), 200)

@admin_api.route(f'{API_VER_PATH_V1}/user-actions/book-created', methods=['GET'])
@verify_token
@admin 
def get_book_created_activity():    
    return make_response(dumps(activityCollection.find({"Action": "Book Created"})), 200)
