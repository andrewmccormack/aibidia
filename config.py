import os
from dotenv import load_dotenv

basedir = os.path.abspath(os.path.dirname(__file__))
load_dotenv(os.path.join(basedir, ".env"))


class Config:
    SECRET_KEY = os.environ.get("SECRET_KEY") or "7b117610f157300f7245315bbfbb713fc95d14dedd00b2e7a1514557ed14b17d"
    MAX_FILE_SIZE = 10 * 1024 * 1024
    FILES_ALLOWED = ["csv"]
    UPLOAD_FOLDER = "data/uploads"
    SCHEMA_FOLDER = "data/schemas"
    WTF_CSRF_TRUSTED_ORIGINS = [
        'http://localhost:5000',
        'http://127.0.0.1:5000',
        'http://0.0.0.0:5000'
    ]
    # Flask-WTF: allow HTTP in dev/Docker (no HTTPS); avoids 403 on form submit
    WTF_CSRF_SSL_STRICT = False
    # Optional: set WTF_CSRF_ENABLED=0 in env to disable CSRF (e.g. local/Docker only)
    WTF_CSRF_ENABLED = False
    WTF_CSRF_TIME_LIMIT = None
    SESSION_COOKIE_SECURE = False
    SESSION_COOKIE_SAMESITE = 'Lax'
    SESSION_COOKIE_DOMAIN = None
