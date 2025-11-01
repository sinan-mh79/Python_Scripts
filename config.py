import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    SECRET_KEY = os.getenv("FLASK_SECRET_KEY", "dev_secret_key")
    WTF_CSRF_ENABLED = True
    
    # MySQL on AlwaysData — fallback to SQLite locally
    SQLALCHEMY_DATABASE_URI = os.getenv(
        "DATABASE_URL",
        "mysql+pymysql://sapp:Sinan7975@mysql-sapp.alwaysdata.net/sapp_app"
    )
    
    SQLALCHEMY_TRACK_MODIFICATIONS = False
