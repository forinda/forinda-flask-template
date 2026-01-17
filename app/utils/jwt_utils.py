"""JWT token utilities for authentication."""

from datetime import datetime, timedelta

import jwt
from flask import request

from app.settings import settings
from app.utils.logger import get_logger

logger = get_logger(__name__)


def generate_token(user_id: str, email: str, role: str = 'user', expires_in_hours: int = 24) -> str:
    """
    Generate a JWT token for a user.

    Args:
        user_id: User's unique identifier
        email: User's email address
        role: User's role (default 'user')
        expires_in_hours: Token expiration time in hours (default 24)

    Returns:
        JWT token string
    """
    payload = {
        'user_id': user_id,
        'email': email,
        'role': role,
        'exp': datetime.utcnow() + timedelta(hours=expires_in_hours),
        'iat': datetime.utcnow(),
    }

    token = jwt.encode(payload, settings.SECRET_KEY, algorithm='HS256')
    logger.debug(f'Generated token for user: {email} (role: {role})')
    return token


def decode_token(token: str) -> dict | None:
    """
    Decode and validate a JWT token.

    Args:
        token: JWT token string

    Returns:
        Decoded payload dict if valid, None otherwise
    """
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=['HS256'])
        return payload
    except jwt.ExpiredSignatureError:
        logger.warning('Token has expired')
        return None
    except jwt.InvalidTokenError as e:
        logger.warning(f'Invalid token: {e}')
        return None


def get_token_from_header() -> str | None:
    """
    Extract JWT token from Authorization header.

    Returns:
        Token string if present, None otherwise
    """
    auth_header = request.headers.get('Authorization')
    if auth_header and auth_header.startswith('Bearer '):
        return auth_header.split(' ')[1]
    return None


def get_user_from_token() -> dict | None:
    """
    Get user information from JWT token in request headers.

    Returns:
        User payload dict if token is valid, None otherwise
    """
    token = get_token_from_header()
    if not token:
        return None

    return decode_token(token)


def refresh_token(old_token: str, expires_in_hours: int = 24) -> str | None:
    """
    Refresh an existing JWT token.

    Args:
        old_token: Current JWT token
        expires_in_hours: New token expiration time in hours

    Returns:
        New JWT token string if old token is valid, None otherwise
    """
    payload = decode_token(old_token)
    if not payload:
        return None

    return generate_token(payload['user_id'], payload['email'], payload.get('role', 'user'), expires_in_hours)
