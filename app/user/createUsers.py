from pymongo import MongoClient
from bson.objectid import ObjectId
import bcrypt

client = MongoClient()

db = client.books
userCollection = db.userCollection

def create_admin_user():
    new_user = {
        "_id" : ObjectId(),
        "username" : "admin",
        "password" : b"cV2CLWD/sliA/dodN+w=",
        "role" : "admin",
        "amountOwed": 0,
        "books" : []
        }
        
    new_user["password"] = bcrypt.hashpw(new_user["password"], bcrypt.gensalt())

    userCollection.insert_one(new_user)

def create_user():
    new_user = {
        "_id" : ObjectId(),
        "username" : "john_doe",
        "password" : b"5+F0gPlRNS5wxo2o7zQ=",
        "role" : "user",
        "amountOwed": 0,
        "books" : []
        }
        
    new_user["password"] = bcrypt.hashpw(new_user["password"], bcrypt.gensalt())

    userCollection.insert_one(new_user)    

create_admin_user()
create_user()
