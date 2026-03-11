from flask import Blueprint, request, jsonify
from app.extensions import mongo
import bcrypt
from datetime import datetime
from bson import ObjectId

from app.auth.auth_service import generate_token
from app.auth.auth_decorator import token_required


auth_bp = Blueprint("auth", __name__)


# -------------------- REGISTER --------------------

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

    allowed_roles = ["provider", "charity"]

    if role not in allowed_roles:
        return jsonify({"error": "Invalid role. Must be provider or charity"}), 400

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


# -------------------- LOGIN --------------------

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

    # 🔐 Generate JWT manually
    access_token = generate_token(user["_id"])

    return jsonify({
        "message": "Login successful",
        "access_token": access_token
    }), 200


# -------------------- PROFILE --------------------

@auth_bp.route("/profile", methods=["GET"])
@token_required
def profile(current_user):

    return jsonify({
        "name": current_user["name"],
        "email": current_user["email"],
        "role": current_user["role"],
        "city": current_user["city"],
        "created_at": current_user["created_at"]
    }), 200