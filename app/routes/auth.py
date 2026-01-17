import hashlib

from flask import Blueprint, jsonify

from app.models import User
from app.schemas import LOGIN_SCHEMA, REGISTER_SCHEMA
from app.utils.decorators import get_user_id_from_token, handle_errors, require_auth, validate_request
from app.utils.logger import get_logger

logger = get_logger(__name__)
auth_bp = Blueprint('auth', __name__, url_prefix='/api/v1/auth')


def hash_password(password: str) -> str:
    """Hash password using SHA256 (use bcrypt in production)."""
    return hashlib.sha256(password.encode()).hexdigest()


def verify_password(password: str, hashed: str) -> bool:
    """Verify password against hash."""
    return hash_password(password) == hashed


@auth_bp.route('/register', methods=['POST'])
@validate_request(REGISTER_SCHEMA)
@handle_errors
def register(validated_data):
    """
    Register a new user
    ---
    tags:
      - Authentication
    summary: Register a new user account
    description: Create a new user account with email and password
    parameters:
      - in: body
        name: body
        description: User registration data
        required: true
        schema:
          type: object
          required:
            - email
            - password
            - name
          properties:
            email:
              type: string
              format: email
              example: user@example.com
            password:
              type: string
              format: password
              example: SecurePassword123!
            name:
              type: string
              example: John Doe
    responses:
      201:
        description: User registered successfully
        schema:
          type: object
          properties:
            message:
              type: string
              example: User registered successfully
            user:
              type: object
              properties:
                id:
                  type: string
                  example: 507f1f77bcf86cd799439011
                email:
                  type: string
                  example: user@example.com
                name:
                  type: string
                  example: John Doe
      400:
        description: Invalid input or user already exists
        schema:
          type: object
          properties:
            error:
              type: string
              example: User already exists
    """
    # Check if user already exists
    existing_user = User.find_by_email(validated_data['email'])
    if existing_user:
        logger.warning(f'Registration attempt with existing email: {validated_data["email"]}')
        return jsonify({'error': 'User already exists'}), 400

    # Create new user
    user_data = {
        'email': validated_data['email'],
        'password': hash_password(validated_data['password']),
        'name': validated_data['name'],
        'role': 'user',
    }

    user_id = User.insert_one(user_data)
    logger.info(f'User registered successfully: {validated_data["email"]} (ID: {user_id})')

    return jsonify(
        message='User registered successfully',
        user={'id': user_id, 'email': validated_data['email'], 'name': validated_data['name']},
    ), 201


@auth_bp.route('/login', methods=['POST'])
@validate_request(LOGIN_SCHEMA)
@handle_errors
def login(validated_data):
    """
    User login
    ---
    tags:
      - Authentication
    summary: Login to the system
    description: Authenticate user and return access token
    parameters:
      - in: body
        name: body
        description: Login credentials
        required: true
        schema:
          type: object
          required:
            - email
            - password
          properties:
            email:
              type: string
              format: email
              example: user@example.com
            password:
              type: string
              format: password
              example: SecurePassword123!
    responses:
      200:
        description: Login successful
        schema:
          type: object
          properties:
            message:
              type: string
              example: Login successful
            token:
              type: string
              example: eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
            user:
              type: object
              properties:
                id:
                  type: string
                  example: 507f1f77bcf86cd799439011
                email:
                  type: string
                  example: user@example.com
                name:
                  type: string
                  example: John Doe
      401:
        description: Invalid credentials
        schema:
          type: object
          properties:
            error:
              type: string
              example: Invalid email or password
    """
    # Find user by email
    user = User.find_by_email(validated_data['email'])

    if not user or not verify_password(validated_data['password'], user.get('password', '')):
        logger.warning(f'Failed login attempt: {validated_data["email"]}')
        return jsonify({'error': 'Invalid email or password'}), 401

    # TODO: Generate actual JWT token
    token = f'mock_token_for_{user["id"]}'

    logger.info(f'User logged in successfully: {validated_data["email"]}')

    return jsonify(
        message='Login successful',
        token=token,
        user={'id': user['id'], 'email': user['email'], 'name': user.get('name', '')},
    ), 200


@auth_bp.route('/logout', methods=['POST'])
@require_auth
@handle_errors
def logout():
    """
    User logout
    ---
    tags:
      - Authentication
    summary: Logout from the system
    description: Invalidate the current user session
    security:
      - Bearer: []
    responses:
      200:
        description: Logout successful
        schema:
          type: object
          properties:
            message:
              type: string
              example: Logout successful
      401:
        description: Unauthorized
    """
    # TODO: Implement token blacklist/invalidation
    user_id = get_user_id_from_token()
    logger.info(f'User logout: {user_id}')

    return jsonify(message='Logout successful'), 200


@auth_bp.route('/me', methods=['GET'])
@require_auth
@handle_errors
def get_current_user():
    """
    Get current user profile
    ---
    tags:
      - Authentication
    summary: Get authenticated user information
    description: Returns the profile of the currently authenticated user
    security:
      - Bearer: []
    responses:
      200:
        description: User profile retrieved successfully
        schema:
          type: object
          properties:
            id:
              type: string
              example: 507f1f77bcf86cd799439011
            email:
              type: string
              example: user@example.com
            name:
              type: string
              example: John Doe
            created_at:
              type: string
              format: date-time
              example: 2026-01-17T10:30:00Z
      401:
        description: Unauthorized
    """
    user_id = get_user_id_from_token()
    user = User.find_by_id(user_id)

    if not user:
        return jsonify({'error': 'User not found'}), 404

    logger.info(f'Get user profile: {user_id}')

    # Remove password from response
    user.pop('password', None)
    user.pop('_id', None)

    return jsonify(user), 200
