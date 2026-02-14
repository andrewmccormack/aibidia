import os
from dotenv import load_dotenv

basedir = os.path.abspath(os.path.dirname(__file__))
load_dotenv(os.path.join(basedir, ".env"))


class Config:
    SECRET_KEY = "7b117610f157300f7245315bbfbb713fc95d14dedd00b2e7a1514557ed14b17d"
    MAX_FILE_SIZE = 10 * 1024 * 1024
    FILES_ALLOWED = ["csv"]
    UPLOAD_FOLDER = "data/uploads"
