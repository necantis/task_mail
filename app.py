import os
from flask import Flask
from extensions import db

def create_app():
    app = Flask(__name__)
    app.secret_key = os.environ.get("FLASK_SECRET_KEY") or "a secret key"
    app.config["SQLALCHEMY_DATABASE_URI"] = os.environ.get("DATABASE_URL")
    app.config["SQLALCHEMY_ENGINE_OPTIONS"] = {
        "pool_recycle": 300,
        "pool_pre_ping": True,
    }
    db.init_app(app)

    with app.app_context():
        from models import Task, PDFAnalysis, GeneratedEmail
        db.create_all()

    from routes import main_bp
    app.register_blueprint(main_bp)

    return app
