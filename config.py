import os
from dotenv import load_dotenv
from sqlalchemy.engine import make_url

load_dotenv()

class Config:
    #  Security
    SECRET_KEY = os.getenv("FLASK_SECRET_KEY", "dev_secret_key")
    WTF_CSRF_ENABLED = True

    #  Database setup
    db_url = os.getenv("DATABASE_URL")
    fallback_sqlite = "sqlite:///fallback.db"

    if db_url:
        try:
            make_url(db_url)  
            SQLALCHEMY_DATABASE_URI = db_url
        except Exception:
            print("Invalid DATABASE_URL, using SQLite fallback.")
            SQLALCHEMY_DATABASE_URI = fallback_sqlite
    else:
        SQLALCHEMY_DATABASE_URI = fallback_sqlite

    SQLALCHEMY_TRACK_MODIFICATIONS = False
