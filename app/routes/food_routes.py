from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from app.extensions import mongo
from bson import ObjectId
from datetime import datetime

food_bp = Blueprint("food", __name__)

@food_bp.route("/", methods=["POST"])
@jwt_required()
def create_food():

    user_id = get_jwt_identity()
    user = mongo.db.users.find_one({"_id": ObjectId(user_id)})

    if not user:
        return jsonify({"error": "User not found"}), 404

    if user["role"] != "provider":
        return jsonify({"error": "Only providers can create listings"}), 403

    data = request.get_json()

    title = data.get("title")
    description = data.get("description")
    quantity = data.get("quantity")
    expiry_date = data.get("expiry_date")
    location = data.get("location")

    if not all([title, description, quantity, expiry_date, location]):
        return jsonify({"error": "All fields are required"}), 400
    
    if not isinstance(quantity, int) or quantity <= 0:
        return jsonify({"error": "Quantity must be a positive integer"}), 400


    food_data = {
        "title": title,
        "description": description,
        "quantity": quantity,
        "expiry_date": expiry_date,
        "location": location,
        "provider_id": user_id,
        "status": "available",
        "created_at": datetime.utcnow()
    }

    mongo.db.food.insert_one(food_data)

    return jsonify({"message": "Food listing created successfully"}), 201

@food_bp.route("/", methods=["GET"])
def get_all_food():
    """
    Retrieve food listings with optional filtering.
    """

    # Get query parameters from URL
    city = request.args.get("city")
    status = request.args.get("status")

    # Build dynamic query
    query = {}

    if city:
        query["location"] = city

    if status:
        query["status"] = status

    foods = mongo.db.food.find(query)

    food_list = []

    for food in foods:
        food_list.append({
            "id": str(food["_id"]),
            "title": food["title"],
            "description": food["description"],
            "quantity": food["quantity"],
            "expiry_date": food["expiry_date"],
            "location": food["location"],
            "status": food["status"],
            "provider_id": food["provider_id"],
            "created_at": food["created_at"]
        })

    return jsonify(food_list), 200