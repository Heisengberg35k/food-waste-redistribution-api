from flask import Flask
from .config import Config
from .extensions import mongo

def create_app():
    app = Flask(__name__)
    
    app.config.from_object(Config)
    
    mongo.init_app(app)
    
    from .routes.auth_routes import auth_bp
    app.register_blueprint(auth_bp, url_prefix="/api/auth")
    
    from .routes.food_routes import food_bp
    app.register_blueprint(food_bp, url_prefix="/api/food")

    return app