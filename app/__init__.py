from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from sqlalchemy import text
from config import Config

# Initialize SQLAlchemy globally
db = SQLAlchemy()

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

    # Initialize database
    db.init_app(app)

    # Import models AFTER db is initialized
    from .models import User

    # Register blueprints
    from .routes import main, user, auth
    app.register_blueprint(main)
    app.register_blueprint(user, url_prefix="/user")
    app.register_blueprint(auth, url_prefix="/auth")

    
    login_manager = LoginManager()
    login_manager.login_view = "auth.login"
    login_manager.login_message_category = "info"
    login_manager.init_app(app)

    @login_manager.user_loader
    def load_user(user_id):
        return User.query.get(int(user_id))

    
    
    
    with app.app_context():
        try:
            with db.engine.connect() as conn:
                conn.execute(text("SELECT 1"))
            db.create_all()
            print(" Connected to MySQL and ensured all tables exist.")
        except Exception as e:
            print(f" MySQL connection failed: {e}")
            print(" Switching to SQLite fallback database...")
            app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///fallback.db"
            db.init_app(app)
            with app.app_context():
                db.create_all()
            print(" SQLite fallback initialized and tables created.")

    return app
