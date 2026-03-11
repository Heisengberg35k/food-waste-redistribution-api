# -------------------- LOAD ENV FIRST --------------------
from dotenv import load_dotenv
load_dotenv()

import os
print("MONGO_URI being used:", os.getenv("MONGO_URI"))

from app import create_app
from app.extensions import mongo
import bcrypt
from datetime import datetime, timedelta
import random

app = create_app()

with app.app_context():

    # -------------------- CLEAR OLD DATA --------------------
    mongo.db.users.delete_many({})
    mongo.db.food.delete_many({})
    print("Old data cleared.")

    # -------------------- PROVIDERS (10) --------------------
    providers_data = [
        "Tesco Express Stratford",
        "Sainsbury's Local Camden",
        "Greggs Central London",
        "Pret A Manger Canary Wharf",
        "Marks & Spencer Foodhall Kensington",
        "Co-op Food Shoreditch",
        "Lidl Birmingham City Centre",
        "Asda Manchester Arndale",
        "Waitrose Westminster",
        "Iceland Croydon"
    ]

    providers = []

    for i, name in enumerate(providers_data):
        hashed_pw = bcrypt.hashpw("123456".encode("utf-8"), bcrypt.gensalt())

        provider = {
            "name": name,
            "email": name.lower().replace(" ", "").replace("'", "") + "@foodconnect.org",
            "password": hashed_pw,
            "role": "provider",
            "city": random.choice(["London", "Birmingham", "Manchester"]),
            "created_at": datetime.utcnow()
        }

        result = mongo.db.users.insert_one(provider)
        provider["_id"] = result.inserted_id
        providers.append(provider)

    # -------------------- CHARITIES (10) --------------------
    charities_data = [
        "London Food Bank Network",
        "East London Community Kitchen",
        "Camden Homeless Support",
        "Birmingham Hope Shelter",
        "Manchester Community Outreach",
        "Croydon Family Support",
        "Westminster Night Shelter",
        "North London Soup Kitchen",
        "Manchester Youth Aid",
        "Birmingham Community Relief"
    ]

    for name in charities_data:
        hashed_pw = bcrypt.hashpw("123456".encode("utf-8"), bcrypt.gensalt())

        charity = {
            "name": name,
            "email": name.lower().replace(" ", "").replace("'", "") + "@foodconnect.org",
            "password": hashed_pw,
            "role": "charity",
            "city": random.choice(["London", "Birmingham", "Manchester"]),
            "created_at": datetime.utcnow()
        }

        mongo.db.users.insert_one(charity)

    print("10 providers and 10 charities inserted.")

    # -------------------- FOOD LISTINGS (100) --------------------
    food_samples = [
        "Surplus Fresh Bread",
        "Unsold Sandwich Packs",
        "Cooked Pasta Meals",
        "Fruit & Veg Boxes",
        "Bakery Pastries",
        "Chicken Wraps",
        "Dairy Products",
        "Ready-to-Eat Salads",
        "Rice & Curry Meals",
        "Canned Food Packs",
        "Fresh Fruit Packs",
        "Vegetarian Meals",
        "Soup Containers",
        "Mixed Grocery Boxes",
        "Bottled Drinks"
    ]

    cities = ["London", "Birmingham", "Manchester"]

    base_date = datetime.utcnow()

    for i in range(100):

        provider = random.choice(providers)

        expiry_offset = random.randint(1, 10)
        expiry_date = base_date + timedelta(days=expiry_offset)

        created_offset = random.randint(0, 3)
        created_at = expiry_date - timedelta(days=created_offset)

        food_item = {
            "title": random.choice(food_samples),
            "description": "Surplus food suitable for redistribution to charities.",
            "quantity": random.randint(10, 200),
            "expiry_date": expiry_date.strftime("%Y-%m-%d"),
            "location": random.choice(cities),
            "provider_id": str(provider["_id"]),
            "provider_name": provider["name"],  # ✅ Denormalised for performance
            "status": "available",
            "created_at": created_at
        }

        mongo.db.food.insert_one(food_item)

    print("100 realistic food listings inserted.")
    print("Seeding completed successfully.")