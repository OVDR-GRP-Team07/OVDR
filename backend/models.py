"""
SQLAlchemy ORM Models for OVDR System
Author: Zixin Ding

This module defines all core database models used in the OVDR system.
These include:

- User: Stores user credentials and uploaded body image
- Clothing: Stores all clothing item metadata and image paths
- Closet: Maps user's favorite clothing items
- Combination: Represents a saved outfit look created by the user
- History: Tracks user browsing behavior for personalization

ORM (Object-Relational Mapping) via SQLAlchemy allows us to treat DB tables as Python classes.
"""

from exts import db
from datetime import datetime, timezone


class User(db.Model):
    __tablename__ = "user"
    user_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    username = db.Column(db.String(255), nullable=False, unique=True)  # cannot equal
    password = db.Column(db.String(255), nullable=False)    # hash password
    image_path = db.Column(db.String(255), default=None)  # full body image

    closet = db.relationship('Closet', backref='user', lazy=True, cascade="all, delete", passive_deletes=True)
    history = db.relationship('History', backref='user', lazy=True, cascade="all, delete", passive_deletes=True)
    combination = db.relationship('Combination', backref='user', lazy=True, cascade="all, delete", passive_deletes=True)

# sql: insert user (username, password_hash) values("zixin", "123456")
# user = User(username = "zixin", password_hash = "123456")

    def __repr__(self):
        return f"<User {self.user_id}, {self.username}>"
    
    # check password (Encrypt with a hash algorithm)
    def check_password(self,password):
        """
        use hash
        return bool
        """
        from werkzeug.security import check_password_hash
        return check_password_hash(self.password_hash, password)

# @app.route("/user/add")
# def add_user():
#     user = User(username = "zixin", password_hash = "123456")
#     db.session.add(user)
#     db.session.commit()
#     return "Register successfully!"

# @app.route("/user/query")
# def query_user():
#     # 1.get查找：根据主键查找
#     User.query.get(1)
#     # 2. filter_by查找多条
#     # 获得Query:类数组（可切片取值）
#     users = User.query.filter_by(username = "zixin").all()
#     for user in users:
#         print(user.username)
#     #获取所有数据
#     users = User.query.all()
#     #获取第一条数据
#     users = User.query.first()

# @app.route("/user/update")
# def update_user():
#     user = User.query.filter_by(username = "zixin").first() 
#     user.password = "22222"
#     db.session.commit()
#     return "Password changed successfully!"

# @app.route("/user/delete")
# def delete_user():
#     user = User.query.get(1)
#     db.session.delete(user)
#     db.session.commit()
#     return "Logout successful!"

class Clothing(db.Model):
    __tablename__ = "clothing"
    cid = db.Column(db.Integer, primary_key=True, autoincrement=True)
    category = db.Column(db.Enum('tops', 'bottoms', 'dresses'), nullable=False)
    caption = db.Column(db.JSON, nullable=True)  # 存储 JSON 格式的描述
    closet_users = db.Column(db.Integer, default=0, nullable=False)
    cloth_path = db.Column(db.String(255))
    cloth_mask_path = db.Column(db.String(255))
    model_tryon_path = db.Column(db.String(255))
    created_at = db.Column(db.TIMESTAMP, server_default=db.text('CURRENT_TIMESTAMP'))

    closet = db.relationship('Closet', backref='clothing', lazy=True, cascade="all, delete-orphan", passive_deletes=True)
    history = db.relationship('History', backref='clothing', lazy=True, cascade="all, delete-orphan", passive_deletes=True)

    def __repr__(self):
        return f"<Clothing {self.cid}, {self.category}>"

class Closet(db.Model):
    __tablename__ = "closet"
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.user_id', ondelete="CASCADE"), nullable=False)
    clothing_id = db.Column(db.Integer, db.ForeignKey('clothing.cid', ondelete="CASCADE"), nullable=False)
    added_at = db.Column(db.TIMESTAMP, server_default=db.text('CURRENT_TIMESTAMP'))

    def __repr__(self):
        return f"<Closet {self.id}, User {self.user_id}, Clothing {self.clothing_id}>"

# Outfits Combination
class Combination(db.Model):
    __tablename__ = "combination"
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.user_id', ondelete="CASCADE"), nullable=False)
    top_id = db.Column(db.Integer, db.ForeignKey('clothing.cid', ondelete="SET NULL"), nullable=True)
    bottom_id = db.Column(db.Integer, db.ForeignKey('clothing.cid', ondelete="SET NULL"), nullable=True)
    dress_id = db.Column(db.Integer, db.ForeignKey('clothing.cid', ondelete="SET NULL"), nullable=True)
    outfit_path = db.Column(db.String(255), nullable=False)
    created_at = db.Column(db.TIMESTAMP, server_default=db.text('CURRENT_TIMESTAMP'))
    
    def __repr__(self):
        return f"<Combination {self.id}, User {self.user_id}, Outfit: Top {self.top_id}, Bottom {self.bottom_id}, Dress {self.dress_id}>"

# Browsing history (for recommending algorithms)
class History(db.Model):
    __tablename__ = "history"
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.user_id', ondelete="CASCADE"), nullable=False)
    clothing_id = db.Column(db.Integer, db.ForeignKey('clothing.cid', ondelete="CASCADE"), nullable=False)
    created_at = db.Column(db.TIMESTAMP, server_default=db.text('CURRENT_TIMESTAMP'))

    def __repr__(self):
        return f"<History {self.id}, User {self.user_id}, Clothing {self.clothing_id}, {self.created_at}>"