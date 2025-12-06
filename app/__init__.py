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
    
    # Ensure data directory exists (use absolute path)
    data_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'data')
    os.makedirs(data_dir, exist_ok=True)
    
    # Update database URI with absolute path
    if app.config['DATABASE_URL'].startswith('sqlite:///data/'):
        db_file = os.path.join(data_dir, 'sentiment.db')
        app.config['SQLALCHEMY_DATABASE_URI'] = f'sqlite:///{db_file}'
    
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
