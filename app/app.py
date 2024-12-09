from flask import Flask, Response, request
from flask_cors import CORS
from book.booksAPI import books_api
from user.usersAPI import users_api
from admin.adminAPI import admin_api

app = Flask(__name__)
CORS(app)

@app.before_request
def handle_preflight():
    if request.method == "OPTIONS":
        res = Response()
        res.headers['X-Content-Type-Options'] = '*'
        return res

app.register_blueprint(books_api)
app.register_blueprint(users_api)
app.register_blueprint(admin_api)

if __name__ == '__main__':
    app.run(debug=True)
