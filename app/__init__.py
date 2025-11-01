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

    from .models import User
    from .routes import main
    app.register_blueprint(main)

    login_manager = LoginManager(app)
    login_manager.login_view = 'main.login'
    login_manager.login_message_category = 'info'

    @login_manager.user_loader
    def load_user(user_id):
        return User.query.get(int(user_id))

    with app.app_context():
        try:
            with db.engine.connect() as conn:
                conn.execute(text("SELECT 1"))
            db.create_all()
            print(" Connected to MySQL and tables created.")
        except Exception as e:
            print(f"⚠️ MySQL connection failed: {e}")
            app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///fallback.db"
            db.init_app(app)
            with db.engine.connect() as conn:
                conn.execute(text("SELECT 1"))
            db.create_all()
            print(" Using SQLite fallback database.")

    return app
