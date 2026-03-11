from flask import Blueprint, request, jsonify
from app.extensions import mongo
from bson import ObjectId
from datetime import datetime

from app.auth.auth_decorator import token_required

food_bp = Blueprint("food", __name__)


# -------------------- CREATE FOOD --------------------

@food_bp.route("/", methods=["POST"])
@token_required
def create_food(current_user):

    user_id = str(current_user["_id"])

    if current_user["role"] != "provider":
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


# -------------------- GET ALL FOOD --------------------

@food_bp.route("/", methods=["GET"])
def get_all_food():

    city = request.args.get("city")
    status = request.args.get("status")

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


# -------------------- UPDATE FOOD --------------------

@food_bp.route("/<food_id>", methods=["PUT"])
@token_required
def update_food(current_user, food_id):

    user_id = str(current_user["_id"])

    if current_user["role"] != "provider":
        return jsonify({"error": "Only providers can update listings"}), 403

    food = mongo.db.food.find_one({"_id": ObjectId(food_id)})

    if not food:
        return jsonify({"error": "Food listing not found"}), 404

    if food["provider_id"] != user_id:
        return jsonify({"error": "You can only update your own listings"}), 403

    data = request.get_json()

    update_fields = {}

    if "title" in data:
        update_fields["title"] = data["title"]

    if "description" in data:
        update_fields["description"] = data["description"]

    if "quantity" in data:
        if not isinstance(data["quantity"], int) or data["quantity"] <= 0:
            return jsonify({"error": "Quantity must be positive integer"}), 400
        update_fields["quantity"] = data["quantity"]

    if "expiry_date" in data:
        update_fields["expiry_date"] = data["expiry_date"]

    if "location" in data:
        update_fields["location"] = data["location"]

    if not update_fields:
        return jsonify({"error": "No valid fields provided"}), 400

    mongo.db.food.update_one(
        {"_id": ObjectId(food_id)},
        {"$set": update_fields}
    )

    return jsonify({"message": "Food listing updated successfully"}), 200


# -------------------- DELETE FOOD --------------------

@food_bp.route("/<food_id>", methods=["DELETE"])
@token_required
def delete_food(current_user, food_id):

    user_id = str(current_user["_id"])

    if current_user["role"] != "provider":
        return jsonify({"error": "Only providers can delete listings"}), 403

    food = mongo.db.food.find_one({"_id": ObjectId(food_id)})

    if not food:
        return jsonify({"error": "Food listing not found"}), 404

    if food["provider_id"] != user_id:
        return jsonify({"error": "You can only delete your own listings"}), 403

    if food["status"] != "available":
        return jsonify({"error": "Cannot delete non-available listings"}), 400

    mongo.db.food.delete_one({"_id": ObjectId(food_id)})

    return jsonify({"message": "Food listing deleted successfully"}), 200


# -------------------- REQUEST FOOD --------------------

@food_bp.route("/<food_id>/request", methods=["POST"])
@token_required
def request_food(current_user, food_id):

    user_id = str(current_user["_id"])

    if current_user["role"] != "charity":
        return jsonify({"error": "Only charities can request food"}), 403

    food = mongo.db.food.find_one({"_id": ObjectId(food_id)})

    if not food:
        return jsonify({"error": "Food listing not found"}), 404

    if food["status"] != "available":
        return jsonify({"error": "Food is not available"}), 400

    mongo.db.food.update_one(
        {"_id": ObjectId(food_id)},
        {
            "$set": {
                "status": "requested",
                "requested_by": user_id,
                "requested_at": datetime.utcnow()
            }
        }
    )

    return jsonify({"message": "Food requested successfully"}), 200

@food_bp.route("/<food_id>/approve", methods=["POST"])
@token_required
def approve_food(current_user, food_id):

    user_id = str(current_user["_id"])

    if current_user["role"] != "provider":
        return jsonify({"error": "Only providers can approve requests"}), 403

    food = mongo.db.food.find_one({"_id": ObjectId(food_id)})

    if not food:
        return jsonify({"error": "Food listing not found"}), 404

    if food["provider_id"] != user_id:
        return jsonify({"error": "You can only approve your own listings"}), 403

    if food["status"] != "requested":
        return jsonify({"error": "Food must be requested first"}), 400

    mongo.db.food.update_one(
        {"_id": ObjectId(food_id)},
        {
            "$set": {
                "status": "approved",
                "approved_at": datetime.utcnow()
            }
        }
    )

    return jsonify({"message": "Food request approved"}), 200

@food_bp.route("/<food_id>/complete", methods=["POST"])
@token_required
def complete_food(current_user, food_id):

    user_id = str(current_user["_id"])

    if current_user["role"] != "provider":
        return jsonify({"error": "Only providers can mark as completed"}), 403

    food = mongo.db.food.find_one({"_id": ObjectId(food_id)})

    if not food:
        return jsonify({"error": "Food listing not found"}), 404

    if food["provider_id"] != user_id:
        return jsonify({"error": "You can only complete your own listings"}), 403

    if food["status"] != "approved":
        return jsonify({"error": "Food must be approved before completion"}), 400

    mongo.db.food.update_one(
        {"_id": ObjectId(food_id)},
        {
            "$set": {
                "status": "completed",
                "completed_at": datetime.utcnow()
            }
        }
    )

    return jsonify({"message": "Food marked as completed"}), 200