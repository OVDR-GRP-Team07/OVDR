"""
User Authentication & Registration Routes
Author: Zixin Ding

This module handles:
- User login and session management
- User registration with unique username enforcement
- (Optional) Email-based verification for registration

Dependencies:
- Flask session for login state management
- Werkzeug security for password hashing
- Flask-Mail for sending email verification

Routes:
- POST /login
- POST /register
- GET /captcha/email (email verification placeholder)
- GET /test (email sending test endpoint)
"""
from models import User
from exts import mail, db
from .forms import LoginForm, RegisterForm
from flask import Blueprint, jsonify, request, session
from werkzeug.security import generate_password_hash,check_password_hash

import random
import string
from flask_mail import Message

import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../..")))

from backend.exts import mail

auth_bp = Blueprint("auth", __name__)

# http://127.0.0.1:5000
@auth_bp.route("/login", methods = ['POST'])
def login():
    form = LoginForm(request.form)
    if form.validate():
        username = form.username.data
        password = form.password.data
        user = User.query.filter_by(username = username).first()
        if not user:
            return jsonify({"error": "Username does not exist."}), 400
        if check_password_hash(user.password, password):
            # cookie: Only suitable for storing small amounts of data, typically used for storing login credentials and authorization information
            # In flask, the session is stored in cookies after being encrypted and signed for security
            session['user_id'] = user.user_id
            return jsonify({"success": f"Login successful!", "username": username, "user_id": user.user_id}), 200
        else:
            return jsonify({"error": "Password entered incorrectly."}), 400
        
    else:
        print(form.errors)
        return jsonify({"error": "Invalid input"}), 400


@auth_bp.route("/register", methods = ['POST'])
def user_register():
    form = RegisterForm(request.form)
    if form.validate():
        username = form.username.data
        password = form.password.data
        
        user = User(username = username, password = generate_password_hash(password))
        db.session.add(user)
        db.session.commit()

        return jsonify({"message": "User registration succeeded!"}), 201
    else:
        return jsonify({"error": list(form.errors.values())}), 400 


##################################################
# To be expanded: email registeration with captcha
@auth_bp.route("/captcha/email")
def get_email_captcha():
    email = request.args.get("email")

    # Generate Verification Code
    source = string.digits*4
    captcha = random.sample(source, 4)
    captcha = "".join(captcha)
    
    message = Message(subject="Verification Code", recipients=[email], body=f"Your Verification Code is: {captcha}")
    mail.send(message)
    # memcached/redis
    return "success"

# To be expanded: email registeration with verification code
@auth_bp.route("/test")
def test():
    message = Message(subject="ovdr test", recipients=["spectateurlin@gmail.com"], body="This is a test")
    mail.send(message)
    return "Send successfully"