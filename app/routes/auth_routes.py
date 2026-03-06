from flask import Blueprint, request, jsonify
from app.extensions import mongo
import bcrypt
from datetime import datetime


auth_bp = Blueprint("auth", __name__)

@auth_bp.route("/register", methods=["POST"])
def register():
    data = request.get_json()

    name = data.get("name")
    email = data.get("email")
    password = data.get("password")
    role = data.get("role")
    city = data.get("city")

    if not all([name, email, password, role, city]):
        return jsonify({"error": "All fields are required"}), 400

    existing_user = mongo.db.users.find_one({"email": email})
    if existing_user:
        return jsonify({"error": "Email already exists"}), 400

    hashed_password = bcrypt.hashpw(password.encode("utf-8"), bcrypt.gensalt())

    user_data = {
        "name": name,
        "email": email,
        "password": hashed_password,
        "role": role,
        "city": city,
        "created_at": datetime.utcnow()
    }

    mongo.db.users.insert_one(user_data)

    return jsonify({"message": "User registered successfully"}), 201


from flask_jwt_extended import create_access_token

@auth_bp.route("/login", methods=["POST"])
def login():
    data = request.get_json()

    email = data.get("email")
    password = data.get("password")

    if not email or not password:
        return jsonify({"error": "Email and password required"}), 400

    user = mongo.db.users.find_one({"email": email})

    if not user:
        return jsonify({"error": "Invalid credentials"}), 401

    if not bcrypt.checkpw(password.encode("utf-8"), user["password"]):
        return jsonify({"error": "Invalid credentials"}), 401

    access_token = create_access_token(identity=str(user["_id"]))

    return jsonify({
        "message": "Login successful",
        "access_token": access_token
    }), 200



from flask_jwt_extended import jwt_required, get_jwt_identity
from bson import ObjectId

@auth_bp.route("/profile", methods=["GET"])
@jwt_required()
def profile():
    # Get user ID stored inside JWT
    user_id = get_jwt_identity()

    # Find user in database using ObjectId
    user = mongo.db.users.find_one({"_id": ObjectId(user_id)})

    if not user:
        return jsonify({"error": "User not found"}), 404

    return jsonify({
        "name": user["name"],
        "email": user["email"],
        "role": user["role"],
        "city": user["city"],
        "created_at": user["created_at"]
    }), 200