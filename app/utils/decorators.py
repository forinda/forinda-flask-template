"""
Utility decorators and helpers for API routes.
"""

from functools import wraps

from flask import jsonify, request

from app.core.validator import ValidationError
from app.utils.jwt_utils import get_user_from_token
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
    Extract user ID from JWT token.

    Returns:
        User ID string if token is valid, None otherwise
    """
    user = get_user_from_token()
    return user['user_id'] if user else None


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


def login_required(f):
    """
    Decorator to require user login.
    Alias for require_auth with more explicit naming.

    Usage:
        @bp.route('/dashboard')
        @login_required
        def dashboard():
            user_id = get_user_id_from_token()
            # Your code here
    """

    @wraps(f)
    def wrapper(*args, **kwargs):
        user = get_user_from_token()
        if not user:
            logger.warning(f'{request.path}: Login required - unauthorized access attempt')
            return jsonify({'error': 'Login required'}), 401
        return f(*args, **kwargs)

    return wrapper


def role_required(*allowed_roles):
    """
    Decorator to require specific user roles.

    Usage:
        @bp.route('/admin')
        @role_required('admin')
        def admin_panel():
            # Your code here

        @bp.route('/content')
        @role_required('admin', 'editor')
        def manage_content():
            # Your code here
    """

    def decorator(f):
        @wraps(f)
        def wrapper(*args, **kwargs):
            user = get_user_from_token()
            if not user:
                logger.warning(f'{request.path}: Authentication required for role check')
                return jsonify({'error': 'Authentication required'}), 401

            # Get user role from token or database
            user_role = user.get('role')

            # If no role in token, fetch from database
            if not user_role:
                from app.models import User

                user_doc = User.find_one({'_id': user['user_id']})
                user_role = user_doc.get('role') if user_doc else None

            if not user_role or user_role not in allowed_roles:
                logger.warning(f'{request.path}: Forbidden - user role "{user_role}" not in {allowed_roles}')
                return jsonify(
                    {'error': 'Forbidden', 'message': f'Requires one of these roles: {", ".join(allowed_roles)}'}
                ), 403

            return f(*args, **kwargs)

        return wrapper

    return decorator
