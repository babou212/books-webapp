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

books_api = Blueprint("books_api", __name__)

@books_api.route(f'{API_VER_PATH_V1}/books', methods=['GET'])
def get_books():
    no_of_docs_each_page = request.args.get("ps", "")
    current_page_number =  request.args.get("pn", "")

    if no_of_docs_each_page and current_page_number:
        return make_response(dumps(bookCollection.find({})
                                .skip(int(no_of_docs_each_page) * (int(current_page_number)-1))
                                .limit(int(no_of_docs_each_page))), 200)
    
    return make_response(dumps(bookCollection.find({})), 200)

@books_api.route(f'{API_VER_PATH_V1}/books/<id>/', methods=['GET'])
def get_book_by_id(id):
    book = bookCollection.find_one({'_id': ObjectId(id)})
    if book:
        return make_response(dumps(book), 200)
    else:
        return make_response(dumps({"Error": "Book not found"}), 404)
    
@books_api.route(f'{API_VER_PATH_V1}/books/category/', methods=['GET'])
def get_book_by_category():
    no_of_docs_each_page = request.args.get("ps", "")
    current_page_number =  request.args.get("pn", "")
    category = request.args.get("category", "")

    if category and bookCollection.count_documents({"categories": category}) > 0:
        if no_of_docs_each_page and current_page_number:
            books = bookCollection.find({"categories": category})\
            .skip(int(no_of_docs_each_page) * (int(current_page_number)-1)).limit(int(no_of_docs_each_page))
            return make_response(dumps(books), 200)
        return make_response(dumps(bookCollection.find({"categories": category})))
    
    return make_response({"Error": "Please provide a valid category"}, 400)

@books_api.route(f'{API_VER_PATH_V1}/books/results/', methods=['GET'])
def get_book_by_text_search():
    no_of_docs_each_page = request.args.get("ps", "")
    current_page_number =  request.args.get("pn", "")
    query = request.args.get("query", "")

    if query and no_of_docs_each_page and current_page_number:
        books = bookCollection.find({ "$text": { "$search": query } })\
        .skip(int(no_of_docs_each_page) * (int(current_page_number)-1)).limit(int(no_of_docs_each_page))
        return make_response(dumps(books), 200)
    
    return make_response(dumps({"Error": "Search Query not provided"}), 400)

@books_api.route(f'{API_VER_PATH_V1}/books/results/price/', methods=['GET'])
def get_book_by_price():
    query = request.args.get("p", "")

    books = bookCollection.find({"price": {"$lte": int(query)}})
    return make_response(dumps(books), 200)
    
@books_api.route(f'{API_VER_PATH_V1}/books/', methods=['POST'])
@verify_token
@admin  
def create_new_book():
    data = request.json

    if data:
        if not data.get("title") or not data.get("isbn") or not data.get("thumbnailUrl"):
            return make_response({"Error": "Title, isbn or thumbnail empty"}, 400) 

        new_book = {
        "_id" : ObjectId(),
        "title" : data.get("title"),
        "isbn" : data.get("isbn"),
        "pageCount" : data.get("pageCount"),
        "publishedDate" : data.get("publishedDate"),
        "thumbnailUrl" : data.get("thumbnailUrl"),
        "description" : data.get("description"),
        "reserved" : False,
        "price" : data.get("price"),
        "authors" : data.get("authors"),
        "categories" : data.get("categories"),
        }

        bookCollection.insert_one(new_book)
        return make_response(dumps(bookCollection.find_one({'_id': new_book["_id"]})), 201)
    
    return make_response(dumps({"Error": "JSON Object not provided"}), 400)
    
@books_api.route(f'{API_VER_PATH_V1}/books/<id>/', methods=['PUT'])
@verify_token
@admin
def update_book(id):
    data = request.json

    if data:
        query = {"_id": ObjectId(id)}
        new_values = {"$set": data}

        activity = {
        "Action": "Book Updated",
        "Book_id": ObjectId(id)
        }

        activityCollection.insert_one(activity)
        bookCollection.update_one(query, new_values)
        return make_response(dumps(bookCollection.find_one({'_id': ObjectId(id)})), 200)
            
    return make_response(dumps({"Error": "JSON Object not provided"}), 400)
    
@books_api.route(f'{API_VER_PATH_V1}/books/<id>/', methods=['DELETE'])
@verify_token
@admin 
def delete_book(id):
    query = {"_id": ObjectId(id)}

    activity = {
        "Action": "Book Deleted",
        "Book_id": ObjectId(id)
        }

    activityCollection.insert_one(activity)
    bookCollection.delete_one(query)
    return make_response(dumps({"Deleted Resource": ObjectId(id)}), 200)
