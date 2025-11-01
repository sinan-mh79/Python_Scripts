from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from config import Config
from sqlalchemy import text

db = SQLAlchemy()


def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

    db.init_app(app)

    # ✅ Import models *after* db is initialized
    from .models import User

    # ✅ Import and register all blueprints
    from .routes import main, user, auth
    app.register_blueprint(main)
    app.register_blueprint(user, url_prefix="/user")
    app.register_blueprint(auth, url_prefix="/auth")

    # ✅ Setup Login Manager
    login_manager = LoginManager()
    login_manager.login_view = "auth.login"  # Redirect unauthorized users to login page
    login_manager.login_message_category = "info"
    login_manager.init_app(app)

    @login_manager.user_loader
    def load_user(user_id):
        return User.query.get(int(user_id))

    # ✅ Ensure database connectivity and fallback setup
    with app.app_context():
        try:
            with db.engine.connect() as conn:
                conn.execute(text("SELECT 1"))
            db.create_all()
            print("✅ Connected to MySQL and tables created.")
        except Exception as e:
            print(f"⚠️ MySQL connection failed: {e}")
            app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///fallback.db"
            db.init_app(app)
            with app.app_context():
                db.create_all()
            print("⚙️ Using SQLite fallback database.")

    return app
