"""
OVDR Backend Initialization Module
Author: Zixin Ding

This module defines `create_app()` which initializes and configures the Flask backend.
It sets up plugins (e.g., SQLAlchemy, CORS), registers route blueprints, connects the database,
and serves static resources like user images and try-on outputs.

Usage:
    from backend import create_app
    app = create_app()

Structure:
    1. Load Flask app
    2. Initialize plugins and migrations
    3. Register route blueprints
    4. Register static resource route
    5. Root route for health check
    6. Optional: test database connection
"""

import os
from flask import Flask
from flask_cors import CORS
from config import Config
from exts import db, initPlugins
from flask_migrate import Migrate
from sqlalchemy import text
from routes import register_blueprints
from utils.static_serve import register_static_routes

#  Suppress TensorFlow log outputs (optional)
os.environ["TF_ENABLE_ONEDNN_OPTS"] = "0"
os.environ["TF_CPP_MIN_LOG_LEVEL"] = "3"

BASE_DATA_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'data'))

def create_app():
    # 1. Initialize the Flask app
    app = Flask(__name__)  
    app.config.from_object(Config)
    CORS(app)  # Enable Cross-Origin Resource Sharing

    # 2. Initialize plugins and migrations
    initPlugins(app)
    
    # Initialize database migrations
    # Usage (CLI):
    # 1. flask db init        - Initialize migration folder (only needed once)
    # 2. flask db migrate -m "message"  - Detect changes in models and generate migration script
    # 3. flask db upgrade     - Apply the migration script and update the actual database schema
    migrate = Migrate(app, db)

    # 3. Register route blueprints
    register_blueprints(app)

    # 4. Register static resource route
    register_static_routes(app)

    # 5. Optional: test database connection
    # Test whether the database is connected successfully
    with app.app_context():
        try:
            with db.engine.connect() as conn:
                rs = conn.execute(text("SELECT 1")) 
                print("The database connection is successful:", rs.fetchone())  # (1,)
        except Exception as e:
            print("DB Connection Error:", e)
    

    return app
