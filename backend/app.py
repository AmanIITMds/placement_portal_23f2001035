from flask import Flask, jsonify
from flask_jwt_extended import JWTManager
from flask_cors import CORS
from config import Config
from models.models import db

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

    # Create instance folder if it doesn't exist
    import os
    os.makedirs(os.path.join(app.root_path, "instance"), exist_ok=True)
    os.makedirs(os.path.join(app.root_path, "uploads"), exist_ok=True)

    # Initialize extensions
    db.init_app(app)
    JWTManager(app)
    CORS(app, resources={r"/api/*": {"origins": "*"}})

    # Register blueprints (routes)
    from routes.auth    import auth_bp
    from routes.admin   import admin_bp
    from routes.company import company_bp
    from routes.student import student_bp

    app.register_blueprint(auth_bp,    url_prefix="/api/auth")
    app.register_blueprint(admin_bp,   url_prefix="/api/admin")
    app.register_blueprint(company_bp, url_prefix="/api/company")
    app.register_blueprint(student_bp, url_prefix="/api/student")

    # Create all tables
    with app.app_context():
        db.create_all()

    @app.route("/")
    def index():
        return jsonify({"message": "Placement Portal API is running!", "version": "2.0"})

    return app


if __name__ == "__main__":
    app = create_app()
    app.run(debug=True, port=5000)