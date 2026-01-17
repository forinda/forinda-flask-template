"""
Swagger/OpenAPI configuration for the Flask API.
"""

def get_swagger_config():
    """Return Swagger UI configuration."""
    return {
        "headers": [],
        "specs": [
            {
                "endpoint": 'apispec',
                "route": '/api/swagger.json',
                "rule_filter": lambda rule: True,
                "model_filter": lambda tag: True,
            }
        ],
        "static_url_path": "/flasgger_static",
        "swagger_ui": True,
        "specs_route": "/api/docs"
    }


def get_swagger_template():
    """Return Swagger template with API information."""
    return {
        "swagger": "2.0",
        "info": {
            "title": "Flask API",
            "description": "A Flask REST API with Swagger documentation",
            "version": "1.0.0",
            "contact": {
                "name": "API Support",
                "email": "support@example.com"
            }
        },
        "host": "localhost:8000",
        "basePath": "/",
        "schemes": ["http", "https"],
        "consumes": ["application/json"],
        "produces": ["application/json"],
        "securityDefinitions": {
            "Bearer": {
                "type": "apiKey",
                "name": "Authorization",
                "in": "header",
                "description": "JWT Authorization header using the Bearer scheme. Example: 'Authorization: Bearer {token}'"
            }
        },
        "tags": [
            {
                "name": "Health",
                "description": "Health check endpoints"
            },
            {
                "name": "API",
                "description": "General API endpoints"
            },
            {
                "name": "Authentication",
                "description": "User authentication and authorization"
            },
            {
                "name": "Categories",
                "description": "Category management endpoints"
            },
            {
                "name": "Articles",
                "description": "Article management endpoints"
            },
            {
                "name": "Collections",
                "description": "Collection management endpoints"
            },
            {
                "name": "Files",
                "description": "File upload and management endpoints"
            }
        ]
    }
