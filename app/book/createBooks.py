from pymongo import MongoClient
from bson.objectid import ObjectId

client = MongoClient()

db = client.books
bookCollection = db.booksCollection

def create_java_book():
    new_book = {
        "_id" : ObjectId(),
        "title" : "Java Persistence with Hibernate",
        "isbn" : 1932394885,
        "pageCount" : 880,
        "publishedDate" : { "$date" : "2006-11-01T00:00:00.000-0800" },
        "thumbnailUrl" : "https://s3.amazonaws.com/AKIAJC5RLADLUMVRPFDQ.book-thumb-images/bauer2.jpg",
        "description" : "\"...this book is the ultimate solution. If you are going to use Hibernate in your application, you have no other choice, go rush to the store and get this book.\" --JavaLobby",
        "reserved" : False,
        "price" : 13.99,
        "authors" : [
            "Gavin King",
            "Christian Bauer"
        ],
        "categories" : [
            "Java"
        ],
        }
        
    bookCollection.insert_one(new_book)

def create_linux_book():
    new_book = {
        "_id" : ObjectId(),
        "title" : "The Linux Command Line: A Complete Introduction",
        "isbn" : 9781593273897,
        "pageCount" : 480,
        "publishedDate" : { "$date" : "2011-12-12T00:00:00.000-0800" },
        "thumbnailUrl" : "https://m.media-amazon.com/images/I/71PfXiJBq1L._SL1500_.jpg",
        "description" : "You've experienced the shiny, point-and-click surface of your Linux computer--now dive below and explore its depths with the power of the command line.The Linux Command Line takes you from your very first terminal keystrokes to writing full programs in Bash",
        "reserved" : False,
        "price" : 12.00,
        "authors" : [
            "William E. Shotts",
        ],
        "categories" : [
            "Linux"
        ],
        }
        
    bookCollection.insert_one(new_book) 

def create_spring_book():
    new_book = {
        "_id" : ObjectId(),
        "title" : "Learning Spring Boot 3.0",
        "isbn" : 1803233303,
        "pageCount" : 270,
        "publishedDate" : { "$date" : "2012-12-31T00:00:00.000-0800" },
        "thumbnailUrl" : "https://m.media-amazon.com/images/I/61t3Z9ty8sL._SL1360_.jpg",
        "description" : "Build Java web apps without wasting any time with this third edition of the best-selling Spring Boot guide for beginners, updated and enhanced with defining features of Spring Boot 3",
        "reserved" : False,
        "price" : 12.99,
        "authors" : [
            "Greg L. Turnquist",
        ],
        "categories" : [
            "Java",
            "Spring"
        ],
        }
        
    bookCollection.insert_one(new_book) 

def create_development_book():
    new_book = {
        "_id" : ObjectId(),
        "title" : "Learning Web Design",
        "isbn" : 1491960205,
        "pageCount" : 700,
        "publishedDate" : { "$date" : "2013-09-19T00:00:00.000-0700" },
        "thumbnailUrl" : "https://m.media-amazon.com/images/I/A1O2e-E1WkL._SL1500_.jpg",
        "description" : "Do you want to build web pages but have no prior experience? This friendly guide is the perfect place to start. Youll begin at square one, learning how the web and web pages work, and then steadily build from there. By the end of the book, youll have the skills to create a simple site with multicolumn pages that adapt for mobile devices",
        "reserved" : False,
        "price" : 10.00,
        "authors" : [
            "Jennifer Nieder Robbins",
        ],
        "categories" : [
            "Software",
            "Development",
            "Engineering"
        ],
        }
        
    bookCollection.insert_one(new_book) 

create_java_book()
create_linux_book()
create_spring_book()
create_development_book()
