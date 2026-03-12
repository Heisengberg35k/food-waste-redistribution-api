from flask import Blueprint, jsonify
from app.extensions import mongo
from datetime import datetime, timedelta

analytics_bp = Blueprint("analytics", __name__)

@analytics_bp.route("/summary", methods=["GET"])
def summary():

    # ---------------- Basic Counts ----------------
    total_listings = mongo.db.food.count_documents({})
    available = mongo.db.food.count_documents({"status": "available"})
    requested = mongo.db.food.count_documents({"status": "requested"})
    approved = mongo.db.food.count_documents({"status": "approved"})
    completed = mongo.db.food.count_documents({"status": "completed"})

    # ---------------- Total Quantity Redistributed ----------------
    redistribution_pipeline = [
        {"$match": {"status": "completed"}},
        {"$group": {"_id": None, "total_quantity": {"$sum": "$quantity"}}}
    ]

    redistribution_result = list(mongo.db.food.aggregate(redistribution_pipeline))
    total_redistributed = (
        redistribution_result[0]["total_quantity"]
        if redistribution_result else 0
    )

    # ---------------- City Distribution ----------------
    city_pipeline = [
        {"$group": {"_id": "$location", "count": {"$sum": 1}}},
        {"$sort": {"count": -1}}
    ]

    city_distribution = list(mongo.db.food.aggregate(city_pipeline))

    # ---------------- Near Expiry Risk Analysis ----------------
    today = datetime.utcnow()
    three_days = today + timedelta(days=3)
    one_day = today + timedelta(days=1)

    near_expiry_pipeline = [
        {
            "$addFields": {
                "expiry_date_converted": {
                    "$dateFromString": {
                        "dateString": "$expiry_date"
                    }
                }
            }
        },
        {
            "$match": {
                "expiry_date_converted": {
                    "$lte": three_days,
                    "$gte": today
                },
                "status": "available"
            }
        },
        {
            "$group": {
                "_id": None,
                "count": {"$sum": 1},
                "total_quantity": {"$sum": "$quantity"}
            }
        }
    ]

    near_expiry_result = list(mongo.db.food.aggregate(near_expiry_pipeline))
    near_expiry_data = near_expiry_result[0] if near_expiry_result else {
        "count": 0,
        "total_quantity": 0
    }

    # ---------------- Critical (Within 24 Hours) ----------------
    critical_pipeline = [
        {
            "$addFields": {
                "expiry_date_converted": {
                    "$dateFromString": {
                        "dateString": "$expiry_date"
                    }
                }
            }
        },
        {
            "$match": {
                "expiry_date_converted": {
                    "$lte": one_day,
                    "$gte": today
                },
                "status": "available"
            }
        },
        {
            "$count": "critical_count"
        }
    ]

    critical_result = list(mongo.db.food.aggregate(critical_pipeline))
    critical_count = (
        critical_result[0]["critical_count"]
        if critical_result else 0
    )

    # ---------------- Provider Leaderboard ----------------
    provider_pipeline = [
        {"$match": {"status": "completed"}},
        {
            "$group": {
                "_id": "$provider_name",
                "total_redistributed": {"$sum": "$quantity"},
                "completed_count": {"$sum": 1}
            }
        },
        {"$sort": {"total_redistributed": -1}}
    ]

    provider_leaderboard = list(mongo.db.food.aggregate(provider_pipeline))

    # ---------------- Final Response ----------------
    return jsonify({
        "total_listings": total_listings,
        "status_breakdown": {
            "available": available,
            "requested": requested,
            "approved": approved,
            "completed": completed
        },
        "total_quantity_redistributed": total_redistributed,
        "city_distribution": city_distribution,
        "near_expiry": {
            "within_3_days": near_expiry_data["count"],
            "total_quantity_at_risk": near_expiry_data["total_quantity"],
            "critical_within_24_hours": critical_count
        },
        "top_providers": provider_leaderboard
    }), 200