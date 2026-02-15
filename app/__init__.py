from flask import Flask
from config import Config
from flask_bootstrap import Bootstrap5
from app.services import init_services


bootstrap = Bootstrap5()


def create_app(config_class=Config):
    app = Flask(__name__)
    bootstrap.init_app(app)
    app.config.from_object(config_class)
    init_services(app)
    with app.app_context():
        from app.main import main_blueprint

        app.register_blueprint(main_blueprint)

    return app
