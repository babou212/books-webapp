from functools import wraps

def verify(func):
    @wraps(func)
    def jwt_wrapper(*args, **kwargs):
        jwt_token = request.args.get("token")
        if not token:
            return make_response(jsonify({"Error": "Missing token"}), 201)
        try:
            data = jwt.decode(jwt_token, SECRET_KEY, algorithms="HS256")
        except: 
            return make_response(jsonify({"Error": "Token is invalid"}), 401)
        return func(*args, **kwargs)
    return jwt_wrapper
 
