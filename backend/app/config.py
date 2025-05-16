import os
from datetime import timedelta
from dotenv import load_dotenv

BASE_DIR = os.path.abspath(os.path.dirname(__file__))

load_dotenv()

class Config:
    SECRET_KEY = os.environ.get("SECRET_KEY")
    SQLALCHEMY_DATABASE_URI = f"sqlite:///{os.path.join(os.path.abspath(os.path.dirname(__file__)), '../instance/app.db')}"
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    BACKUP_DIR = os.path.join(os.path.abspath(os.path.dirname(__file__)), '../instance/backups')

    # JWT token configuration
    JWT_SECRET_KEY = os.environ.get("JWT_SECRET_KEY")
    JWT_ACCESS_TOKEN_EXPIRES = timedelta(days=7)
    JWT_TOKEN_LOCATION = ["cookies"]
    JWT_COOKIE_SECURE = False ## OBS ENDRE TIL True FØR ME LEVERE
    JWT_COOKIE_CSRF_PROTECT = True
    JWT_CSFR_IN_COOKIES = True

    # Flask Mail configuration
    MAIL_SERVER = 'smtp.gmail.com'
    MAIL_PORT = 587
    MAIL_USE_TLS = True
    MAIL_USERNAME = os.environ.get("MAIL_USERNAME")
    MAIL_PASSWORD = os.environ.get("MAIL_PASSWORD")
    MAIL_DEFAULT_SENDER ='trulsovrebo@gmail.com'



