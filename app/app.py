from flask import Flask
from book.booksAPI import books_api
from user.usersAPI import users_api
from admin.adminAPI import admin_api

app = Flask(__name__)

app.register_blueprint(books_api)
app.register_blueprint(users_api)
app.register_blueprint(admin_api)

if __name__ == '__main__':
    app.run(debug=True)
