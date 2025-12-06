"""
Flask application initialization.
"""
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from app.config import Config
from app.database.models import db
import os


def create_app(config_class=Config):
    """Create and configure the Flask application."""
    app = Flask(__name__)
    app.config.from_object(config_class)
    
    # Ensure data directory exists
    os.makedirs('data', exist_ok=True)
    
    # Initialize database
    db.init_app(app)
    
    # Create tables
    with app.app_context():
        db.create_all()
    
    # Register blueprints
    from app.routes import main_bp, api_bp
    app.register_blueprint(main_bp)
    app.register_blueprint(api_bp, url_prefix='/api')
    
    return app
