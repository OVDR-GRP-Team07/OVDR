def register_blueprints(app):
    from routes.auth import auth_bp
    from routes.user_image import user_image_bp
    from routes.history import history_bp
    from routes.closet import closet_bp
    from routes.process import process_bp
    from routes.email import email_bp
    from routes.combination import combinations_bp
    from routes.search import search_bp
    from routes.recommend import recommend_bp

    app.register_blueprint(auth_bp)
    app.register_blueprint(user_image_bp)
    app.register_blueprint(history_bp)
    app.register_blueprint(closet_bp)
    app.register_blueprint(process_bp)
    app.register_blueprint(email_bp)
    app.register_blueprint(combinations_bp)
    app.register_blueprint(search_bp)
    app.register_blueprint(recommend_bp)