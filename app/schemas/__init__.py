"""
Validation schemas for API endpoints.
"""

from app.schemas.article import CREATE_ARTICLE_SCHEMA, UPDATE_ARTICLE_SCHEMA
from app.schemas.auth import LOGIN_SCHEMA, REGISTER_SCHEMA
from app.schemas.category import CREATE_CATEGORY_SCHEMA, UPDATE_CATEGORY_SCHEMA
from app.schemas.collection import ADD_ARTICLE_TO_COLLECTION_SCHEMA, CREATE_COLLECTION_SCHEMA, UPDATE_COLLECTION_SCHEMA
from app.schemas.file import FILE_UPLOAD_SCHEMA

__all__ = [
    # Auth
    'REGISTER_SCHEMA',
    'LOGIN_SCHEMA',
    # Category
    'CREATE_CATEGORY_SCHEMA',
    'UPDATE_CATEGORY_SCHEMA',
    # Article
    'CREATE_ARTICLE_SCHEMA',
    'UPDATE_ARTICLE_SCHEMA',
    # Collection
    'CREATE_COLLECTION_SCHEMA',
    'UPDATE_COLLECTION_SCHEMA',
    'ADD_ARTICLE_TO_COLLECTION_SCHEMA',
    # File
    'FILE_UPLOAD_SCHEMA',
]
