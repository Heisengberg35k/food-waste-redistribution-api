from functools import wraps
from flask import request, jsonify, current_app
import jwt
from bson import ObjectId
from app.extensions import mongo

def token_required(f):

    @wraps(f)
    def decorated(*args, **kwargs):

        token = None

        if "Authorization" in request.headers:
            auth_header = request.headers["Authorization"]
            parts = auth_header.split(" ")

            if len(parts) == 2 and parts[0] == "Bearer":
                token = parts[1]

        if not token:
            return jsonify({"error": "Token is missing"}), 401

        try:
            data = jwt.decode(
                token,
                current_app.config["SECRET_KEY"],
                algorithms=["HS256"]
            )

            current_user = mongo.db.users.find_one(
                {"_id": ObjectId(data["user_id"])}
            )

            if not current_user:
                return jsonify({"error": "User not found"}), 404

        except jwt.ExpiredSignatureError:
            return jsonify({"error": "Token expired"}), 401

        except jwt.InvalidTokenError:
            return jsonify({"error": "Invalid token"}), 401

        return f(current_user, *args, **kwargs)

    return decorated