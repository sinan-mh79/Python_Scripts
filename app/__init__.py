from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from dotenv import load_dotenv
import os

# Load environment variables
load_dotenv()

db = SQLAlchemy()
limiter = Limiter(key_func=get_remote_address)

def create_app():
    app = Flask(__name__)
    app.secret_key = os.environ.get("FLASK_SECRET_KEY") or "dev_secret_key"

    # --- Local SQLite database ---
    app.config["SQLALCHEMY_DATABASE_URI"] = os.environ.get("DATABASE_URL", "sqlite:///database.db")
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

    db.init_app(app)
    limiter.init_app(app)

    from . import routes
    app.register_blueprint(routes.main)

    # Create tables if not exist
    with app.app_context():
        db.create_all()

    return app
