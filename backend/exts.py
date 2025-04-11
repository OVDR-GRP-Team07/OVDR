# This file is to avoid circular reference problem
"""
Extension Initialization File
Author: Zixin Ding

Purpose:
    This file defines global plugin instances and an `initPlugins` function 
    to initialize all third-party Flask extensions. It helps avoid circular imports
    by separating plugin definitions from their usage in the main application.

Includes:
    - SQLAlchemy: For ORM-based database operations
    - Flask-Mail: For sending verification or result emails
    - Flask-CORS: For allowing frontend-backend cross-origin communication

Usage:
    from exts import db, mail, cors, initPlugins
    initPlugins(app)
"""

# flask_sqlalchemy
from flask_sqlalchemy import SQLAlchemy
from flask_mail import Mail
from flask_cors import CORS

db = SQLAlchemy()
mail = Mail()
cors = CORS() 

# Initialization
def initPlugins(app):
    db.init_app(app)
    mail.init_app(app)
    cors.init_app(app, resources=app.config["CORS_RESOURCES"]) # Allow cross-domain requests