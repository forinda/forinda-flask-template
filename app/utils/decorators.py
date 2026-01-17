"""
Utility decorators and helpers for API routes.
"""

from functools import wraps

from flask import jsonify, request

from app.lib import ValidationError
from app.utils.logger import get_logger

logger = get_logger(__name__)


def validate_request(schema):
    """
    Decorator to validate request JSON data against a schema.

    Usage:
        @bp.route('/users', methods=['POST'])
        @validate_request(user_schema)
        def create_user(validated_data):
            # validated_data is already validated
            pass
    """

    def decorator(f):
        @wraps(f)
        def wrapper(*args, **kwargs):
            data = request.get_json()

            if data is None:
                logger.warning(f'{request.path}: No JSON data provided')
                return jsonify({'error': 'No JSON data provided'}), 400

            try:
                validated_data = schema.validate(data)
                return f(validated_data, *args, **kwargs)
            except ValidationError as e:
                logger.warning(f'{request.path}: Validation failed - {e.errors}')
                return jsonify({'errors': e.errors}), 400

        return wrapper

    return decorator


def handle_errors(f):
    """
    Decorator to handle common exceptions in routes.

    Usage:
        @bp.route('/users/<user_id>')
        @handle_errors
        def get_user(user_id):
            # Your code here
            pass
    """

    @wraps(f)
    def wrapper(*args, **kwargs):
        try:
            return f(*args, **kwargs)
        except ValidationError as e:
            logger.warning(f'{request.path}: Validation error - {e.errors}')
            return jsonify({'errors': e.errors}), 400
        except ValueError as e:
            logger.warning(f'{request.path}: Value error - {e!s}')
            return jsonify({'error': str(e)}), 400
        except Exception as e:
            logger.error(f'{request.path}: Unexpected error - {e!s}', exc_info=True)
            return jsonify({'error': 'Internal server error'}), 500

    return wrapper


def get_user_id_from_token():
    """
    Extract user ID from JWT token (placeholder).
    In production, implement proper JWT validation.
    """
    # TODO: Implement JWT token validation
    # For now, return a mock user ID
    auth_header = request.headers.get('Authorization')
    if auth_header and auth_header.startswith('Bearer '):
        # In production, decode and validate JWT
        return 'mock_user_id_123'
    return None


def require_auth(f):
    """
    Decorator to require authentication.

    Usage:
        @bp.route('/profile')
        @require_auth
        def get_profile():
            user_id = get_user_id_from_token()
            # Your code here
    """

    @wraps(f)
    def wrapper(*args, **kwargs):
        user_id = get_user_id_from_token()
        if not user_id:
            logger.warning(f'{request.path}: Unauthorized access attempt')
            return jsonify({'error': 'Authentication required'}), 401
        return f(*args, **kwargs)

    return wrapper
