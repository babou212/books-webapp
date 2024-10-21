from flask import Flask, request, make_response, jsonify
from pymongo import MongoClient
from bson.json_util import dumps
from bson.objectid import ObjectId
import jwt
import datetime
from functools import wraps
import os

SECRET_KEY = os.getenv("SECRET_KEY")

client = MongoClient()

db = client.books
collection = db.booksCollection

app = Flask(__name__)

API_VER_PATH_V1="/api/v1/"

@app.route(f'{API_VER_PATH_V1}/books/', methods=['GET'])
def get_all_books():
    return make_response(dumps(collection.find({})), 200)

@app.route(f'{API_VER_PATH_V1}/books/<id>/', methods=['GET'])
def get_book_by_id(id):
    if ObjectId.is_valid(id):
        return make_response(dumps(collection.find_one({'_id': ObjectId(id) })), 200)        

    return make_response(dumps(collection.find_one({'_id': int(id) })), 200)
    
@app.route(f'{API_VER_PATH_V1}/books/results/', methods=['GET'])
def get_book_by_text_search():
    query = request.args.get("query", "")
    return make_response(dumps(collection.find({ "$text": { "$search": query } })), 200)
         
@app.route(f'{API_VER_PATH_V1}/books/', methods=['POST'])
def create_new_book():

    data = request.json

    # if data.get("title") or data.get("isbn") or data.get("authors") or data.get("thumbnailUrl") or data.get("status") == "":
    #     return make_response({"Error": "Title, isbn, status or authors are empty"}, 400) 

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

    collection.insert_one(new_book)
    return make_response(dumps(collection.find_one({'_id': new_book["_id"] })), 201)

@app.route(f'{API_VER_PATH_V1}/books/<id>/', methods=['PUT'])
def update_book(id):
    data = request.json

    if ObjectId.is_valid(id):
        query = { "_id": ObjectId(id) }
        new_values = { "$set": data }

        collection.update_one(query, new_values)
        return make_response(dumps(collection.find_one({'_id': ObjectId(id) })), 200)
    
    query = { "_id": int(id) }
    new_values = { "$set": data }

    collection.update_one(query, new_values)
    return make_response(dumps(collection.find_one({'_id': int(id) })), 200)

@app.route(f'{API_VER_PATH_V1}/books/<id>/', methods=['DELETE'])
def delete_book(id):

    if ObjectId.is_valid(id):
        query = { "_id": ObjectId(id) }

        collection.delete_one(query)
        return make_response(dumps({"Deleted Resource": ObjectId(id)}), 200)
    
    query = { "_id": int(id) }

    collection.update_one(query)
    return make_response(dumps({"Deleted Resource": int(id)}), 200)

@app.route(f'{API_VER_PATH_V1}/login/', methods=['POST'])
def user_login():
    data = request.json

    token = jwt.encode({
        "user": data.get("username"),
        "exp": datetime.datetime.now() + datetime.timedelta(minutes=30),
    }, SECRET_KEY, algorithm="HS256")

    return make_response(jsonify({"token": token}), 201)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=105)
