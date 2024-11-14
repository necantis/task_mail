import os
import logging
from flask import Flask, jsonify, request
from flask_cors import CORS
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import DeclarativeBase
from werkzeug.exceptions import HTTPException

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class Base(DeclarativeBase):
    pass

db = SQLAlchemy(model_class=Base)
app = Flask(__name__)

# Enable CORS
CORS(app)

# Setup configurations
app.secret_key = os.environ.get("FLASK_SECRET_KEY", "default-secret-key")

# Configure database URL with proper formatting
db_url = os.environ.get("DATABASE_URL")
if db_url and db_url.startswith("postgres://"):
    db_url = db_url.replace("postgres://", "postgresql://", 1)

app.config["SQLALCHEMY_DATABASE_URI"] = db_url
app.config["SQLALCHEMY_ENGINE_OPTIONS"] = {
    "pool_recycle": 300,
    "pool_pre_ping": True,
}
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max file size

# Initialize database
db.init_app(app)

# Request logging
@app.before_request
def log_request_info():
    logger.info('Headers: %s', request.headers)
    logger.info('Body: %s', request.get_data())

# Error handlers
@app.errorhandler(400)
def bad_request_error(error):
    logger.error(f"400 Bad Request: {error}")
    return jsonify({"error": str(error)}), 400

@app.errorhandler(404)
def not_found_error(error):
    logger.error(f"404 Not Found: {error}")
    return jsonify({"error": "Resource not found"}), 404

@app.errorhandler(500)
def internal_error(error):
    logger.error(f"500 Internal Server Error: {error}")
    return jsonify({"error": "Internal server error"}), 500

@app.errorhandler(HTTPException)
def handle_http_error(error):
    logger.error(f"HTTP Exception: {error}")
    response = jsonify({
        "error": str(error.description),
        "code": error.code
    })
    return response, error.code

@app.errorhandler(Exception)
def handle_exception(error):
    logger.error(f"Unhandled Exception: {error}", exc_info=True)
    return jsonify({
        "error": "An unexpected error occurred",
        "details": str(error)
    }), 500

# Register blueprints
from routes import upload_bp
app.register_blueprint(upload_bp)

# Create all database tables
with app.app_context():
    import models
    db.create_all()
