import os
from dataclasses import dataclass, field


@dataclass
class Settings:
    """Application settings and configuration."""

    # Flask settings
    FLASK_APP: str = os.getenv('FLASK_APP', 'main.py')
    FLASK_ENV: str = os.getenv('FLASK_ENV', 'development')
    DEBUG: bool = os.getenv('DEBUG', 'True').lower() == 'true'
    HOST: str = os.getenv('HOST', '0.0.0.0')
    PORT: int = int(os.getenv('PORT', 8000))

    # CORS settings
    CORS_ORIGINS: list[str] = field(
        default_factory=lambda: ['http://localhost:3000', 'http://localhost:5173', 'http://localhost:8080']
    )
    CORS_METHODS: list[str] = field(default_factory=lambda: ['GET', 'POST', 'PUT', 'DELETE', 'OPTIONS', 'PATCH'])
    CORS_ALLOW_HEADERS: list[str] = field(default_factory=lambda: ['Content-Type', 'Authorization'])
    CORS_EXPOSE_HEADERS: list[str] = field(default_factory=lambda: ['Content-Type', 'Authorization'])
    CORS_SUPPORTS_CREDENTIALS: bool = True
    CORS_MAX_AGE: int = 3600

    # Logging settings
    LOG_LEVEL: str = os.getenv('LOG_LEVEL', 'DEBUG' if DEBUG else 'INFO')
    LOG_DIR: str = os.getenv('LOG_DIR', 'logs')
    LOG_MAX_BYTES: int = 10 * 1024 * 1024  # 10MB
    LOG_BACKUP_COUNT: int = 10

    # API settings
    API_TITLE: str = 'Flask API'
    API_VERSION: str = '1.0.0'
    API_DESCRIPTION: str = 'A Flask REST API with Swagger documentation'

    # Swagger settings
    SWAGGER_URL: str = '/'  # '/api/v1/docs'
    SWAGGER_API_URL: str = '/api/swagger.json'

    # MongoDB settings
    MONGODB_URI: str = os.getenv('MONGODB_URI', 'mongodb://localhost:27017/')
    MONGODB_DB_NAME: str = os.getenv('MONGODB_DB_NAME', 'flask_app')
    MONGODB_TIMEOUT: int = int(os.getenv('MONGODB_TIMEOUT', 5000))

    # Database settings (legacy - for migration reference)
    DATABASE_URL: str = os.getenv('DATABASE_URL', 'sqlite:///app.db')

    # Security settings
    SECRET_KEY: str = os.getenv('SECRET_KEY', 'dev-secret-key-change-in-production')

    # JWT settings
    JWT_ALGORITHM: str = 'HS256'
    JWT_EXPIRATION_HOURS: int = int(os.getenv('JWT_EXPIRATION_HOURS', 24))
    JWT_REFRESH_EXPIRATION_DAYS: int = int(os.getenv('JWT_REFRESH_EXPIRATION_DAYS', 7))

    @classmethod
    def load_from_env(cls):
        """Load settings from environment variables."""
        return cls()

    def to_dict(self):
        """Convert settings to dictionary."""
        return {key: getattr(self, key) for key in dir(self) if not key.startswith('_') and key.isupper()}


# Global settings instance
settings = Settings.load_from_env()
