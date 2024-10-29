from flask import request, make_response, Blueprint
from pymongo import MongoClient
from bson.json_util import dumps
from bson.objectid import ObjectId
import jwt
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

books_api = Blueprint("books_api", __name__)

@books_api.route(f'{API_VER_PATH_V1}/books/', methods=['GET'])
def get_all_books():
    return make_response(dumps(bookCollection.find({})), 200)

@books_api.route(f'{API_VER_PATH_V1}/books/<id>/', methods=['GET'])
def get_book_by_id(id):
    if ObjectId.is_valid(id):
        book = bookCollection.find_one({'_id': ObjectId(id) })
        if book:
            return make_response(dumps(book), 200)
        else:
            return make_response(dumps({"Error": "Book not found"}), 404)

    book = bookCollection.find_one({'_id': int(id)})
    if book:
        return make_response(dumps(book), 200)
    else:
        return make_response(dumps({"Error": "Book not found"}), 404)
   
@books_api.route(f'{API_VER_PATH_V1}/books/results/', methods=['GET'])
def get_book_by_text_search():
    query = request.args.get("query", "")

    if query:
        return make_response(dumps(bookCollection.find({ "$text": { "$search": query } })), 200)
    
    return make_response(dumps({"Error": "Search Query not provided"}), 400)
    
@books_api.route(f'{API_VER_PATH_V1}/books/', methods=['POST'])
@verify_token  
def create_new_book():
    data = request.json

    if data:
        if not data.get("title") or not data.get("isbn") or not data.get("thumbnailUrl"):
            return make_response({"Error": "Title, isbn, status or authors are empty"}, 400) 

        new_book = {
        "_id" : ObjectId(),
        "title" : data.get("title"),
        "isbn" : data.get("isbn"),
        "pageCount" : data.get("pageCount"),
        "publishedDate" : data.get("publishedDate"),
        "thumbnailUrl" : data.get("thumbnailUrl"),
        "longDescription" : data.get("longDescription"),
        "shortDescription" : data.get("shortDescription"),
        "status" : data.get("status"),
        "authors" : data.get("authors"),
        "categories" : data.get("categories"),
        }

        bookCollection.insert_one(new_book)
        return make_response(dumps(bookCollection.find_one({'_id': new_book["_id"] })), 201)
    
    return make_response(dumps({"Error": "JSON Object not provided"}), 400)
    
@books_api.route(f'{API_VER_PATH_V1}/books/<id>/', methods=['PUT'])
@verify_token
def update_book(id):
    data = request.json

    if data:
        if ObjectId.is_valid(id):
            query = { "_id": ObjectId(id) }
            new_values = { "$set": data }

            bookCollection.update_one(query, new_values)
            return make_response(dumps(bookCollection.find_one({'_id': ObjectId(id) })), 200)
        
        query = { "_id": int(id) }
        new_values = { "$set": data }

        bookCollection.update_one(query, new_values)
        return make_response(dumps(bookCollection.find_one({'_id': int(id) })), 200)
    
    return make_response(dumps({"Error": "JSON Object not provided"}), 400)
    
@books_api.route(f'{API_VER_PATH_V1}/books/<id>/', methods=['DELETE'])
@verify_token
@admin 
def delete_book(id):
    if ObjectId.is_valid(id):
        query = { "_id": ObjectId(id) }

        bookCollection.delete_one(query)
        return make_response(dumps({"Deleted Resource": ObjectId(id)}), 200)
    
    query = { "_id": int(id) }

    bookCollection.delete_one(query)
    return make_response(dumps({"Deleted Resource": int(id)}), 200)
        
@books_api.route(f'{API_VER_PATH_V1}/books/<id>/reserve', methods=['PUT'])
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
