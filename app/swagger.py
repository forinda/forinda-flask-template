"""
Swagger/OpenAPI configuration for the Flask API.
"""

from app.settings import settings


def get_swagger_config():
    """Return Swagger UI configuration."""
    return {
        'headers': [],
        'specs': [
            {
                'endpoint': 'apispec',
                'route': settings.SWAGGER_API_URL,
                'rule_filter': lambda rule: True,
                'model_filter': lambda tag: True,
            }
        ],
        'static_url_path': '/flasgger_static',
        'swagger_ui': True,
        'specs_route': settings.SWAGGER_URL,
    }


def get_swagger_template():
    """Return Swagger template with API information."""
    return {
        'swagger': '2.0',
        'info': {
            'title': settings.API_TITLE,
            'description': settings.API_DESCRIPTION,
            'version': settings.API_VERSION,
            'contact': {'name': 'API Support', 'email': 'support@example.com'},
        },
        'host': 'localhost:8000',
        'basePath': '/api/v1',
        'schemes': ['http', 'https'],
        'consumes': ['application/json'],
        'produces': ['application/json'],
        'securityDefinitions': {
            'Bearer': {
                'type': 'apiKey',
                'name': 'Authorization',
                'in': 'header',
                'description': "JWT Authorization header using the Bearer scheme. Example: 'Authorization: Bearer {token}'",
            }
        },
        'tags': [
            {'name': 'Health', 'description': 'Health check endpoints'},
            {'name': 'API', 'description': 'General API endpoints'},
            {'name': 'Authentication', 'description': 'User authentication and authorization'},
            {'name': 'Categories', 'description': 'Category management endpoints'},
            {'name': 'Articles', 'description': 'Article management endpoints'},
            {'name': 'Collections', 'description': 'Collection management endpoints'},
            {'name': 'Files', 'description': 'File upload and management endpoints'},
        ],
    }
