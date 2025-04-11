"""
Configuration File
Author:  Zixin Ding

This module loads environment variables from a `.env` file and sets up
configuration options for Flask, database, email, and CORS.

Usage:
    from config import Config
    app.config.from_object(Config)
"""
 
import os
from dotenv import load_dotenv

# Load the.env file
load_dotenv()

class Config:
    # Database configuration
    SQLALCHEMY_DATABASE_URI = f"mysql+pymysql://{os.getenv('USER_NAME')}:{os.getenv('PASSWORD')}@{os.getenv('HOSTNAME')}:{os.getenv('PORT')}/{os.getenv('DATABASE')}?charset=utf8mb4"
    
    # Email Configuration
    MAIL_SERVER = os.getenv("MAIL_SERVER")
    MAIL_PORT = int(os.getenv("MAIL_PORT", 465))
    MAIL_USE_SSL = os.getenv("MAIL_USE_SSL") == "True"
    MAIL_USERNAME = os.getenv("MAIL_USERNAME")
    MAIL_PASSWORD = os.getenv("MAIL_PASSWORD")
    MAIL_DEFAULT_SENDER = os.getenv("MAIL_DEFAULT_SENDER")

    # Flask & CORS 配置
    SECRET_KEY = os.getenv("SECRET_KEY")
    CORS_HEADERS = "Content-Type"
    CORS_RESOURCES = {r"/*": {"origins": "*"}}
