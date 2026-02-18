import logging
from flask import Flask
from flask_wtf import CSRFProtect
from flask_wtf.csrf import CSRFError
from config import Config
from flask_bootstrap import Bootstrap5
from app.services import init_services

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

csrf = CSRFProtect()
bootstrap = Bootstrap5()

def create_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(config_class)

    @app.after_request
    def add_no_cache_headers(response):
        # Don't cache HTML pages (they contain CSRF tokens)
        if response.content_type and 'text/html' in response.content_type:
            response.headers['Cache-Control'] = 'no-store, no-cache, must-revalidate, max-age=0'
            response.headers['Pragma'] = 'no-cache'
            response.headers['Expires'] = '0'
        return response

    # Add CSRF error handler to see what's going wrong
    @app.errorhandler(CSRFError)
    def handle_csrf_error(e):
        print(f"CSRF Error: {e.description}")
        return f"CSRF Error: {e.description}", 403

    logger.info(f"Starting app with config: {app.config}")
    bootstrap.init_app(app)
    csrf.init_app(app)
    init_services(app)
    with app.app_context():
        from app.main import main_blueprint

        app.register_blueprint(main_blueprint)

    return app
