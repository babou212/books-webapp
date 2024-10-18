import json
from flask import Flask, request, make_response
from pymongo import MongoClient
from bson.json_util import dumps
import random

client = MongoClient()

db = client.books
collection = db.booksCollection

app = Flask(__name__)

API_VER_PATH="/api/v1/"

@app.route(f'{API_VER_PATH}/books/', methods=['GET'])
def get_all_books():
    return make_response(dumps(collection.find({})), 200)

@app.route(f'{API_VER_PATH}/books/<int:id>/', methods=['GET'])
def get_book_by_id(id):
    return make_response(dumps(collection.find_one({'_id': id })), 200)

@app.route(f'{API_VER_PATH}/books/', methods=['POST'])
def create_new_book():

    data = request.json

    new_book = {
    "_id" : random.randint(796, 100000),
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

    data = request.json
    print(data)

    collection.insert_one(new_book)
    return make_response(dumps(collection.find_one({'_id': new_book["_id"] })), 201)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=105)
