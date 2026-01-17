import logging

from flasgger import Swagger
from flask import Flask, request
from flask_cors import CORS

from app.database import MongoDB, init_db
from app.settings import settings
from app.swagger import get_swagger_config, get_swagger_template
from app.utils.logger import get_logger

logger = get_logger(__name__)


def create_app():
    app = Flask(__name__)

    # Load configuration from settings
    app.config['SECRET_KEY'] = settings.SECRET_KEY
    app.config['DEBUG'] = settings.DEBUG

    # Initialize Swagger first (before CORS)
    swagger = Swagger(app, config=get_swagger_config(), template=get_swagger_template())

    # Configure CORS using settings - exclude Swagger routes
    CORS(
        app,
        resources={
            r'/api/v1/.*': {
                'origins': settings.CORS_ORIGINS,
                'methods': settings.CORS_METHODS,
                'allow_headers': settings.CORS_ALLOW_HEADERS,
                'expose_headers': settings.CORS_EXPOSE_HEADERS,
                'supports_credentials': settings.CORS_SUPPORTS_CREDENTIALS,
                'max_age': settings.CORS_MAX_AGE,
            }
        },
    )

    # Set log level based on debug mode
    if app.debug:
        from app.utils.logger import Logger

        Logger.set_all_levels(logging.DEBUG)

    logger.info(f'Flask application startup (Environment: {settings.FLASK_ENV})')
    logger.info(f'Swagger documentation available at {settings.SWAGGER_URL}')

    @app.before_request
    def log_request_info():
        logger.debug(f'Request: {request.method} {request.path}')
        logger.debug(f'Headers: {dict(request.headers)}')
        if request.data:
            logger.debug(f'Body: {request.get_data(as_text=True)}')

    @app.after_request
    def log_response_info(response):
        logger.debug(f'Response: {response.status_code}')
        return response

    # Register blueprints
    from app.routes.api import api_bp
    from app.routes.articles import articles_bp
    from app.routes.auth import auth_bp
    from app.routes.categories import categories_bp
    from app.routes.collections import collections_bp
    from app.routes.files import files_bp
    from app.routes.health import health_bp
    from app.routes.storage import storage_bp

    app.register_blueprint(health_bp)
    app.register_blueprint(api_bp)
    app.register_blueprint(auth_bp)
    app.register_blueprint(categories_bp)
    app.register_blueprint(articles_bp)
    app.register_blueprint(collections_bp)
    app.register_blueprint(files_bp)
    app.register_blueprint(storage_bp)

    logger.info('All blueprints registered successfully')

    # Initialize MongoDB
    with app.app_context():
        try:
            MongoDB.connect()
            init_db()
            logger.info('MongoDB connected and indexes created successfully')
        except Exception as e:
            logger.error(f'MongoDB connection error: {e!s}')

    # Register teardown handler
    @app.teardown_appcontext
    def shutdown_session(exception=None):
        """Close database connection on app shutdown."""
        try:
            MongoDB.close()
        except Exception as e:
            logger.error(f'Error closing MongoDB connection: {e!s}')

    return app
