"""
Example usage of the validation library.

This file demonstrates how to use the Zod-like validator
in your Flask routes and models.
"""

from flask import jsonify

from app.core.validator import Schema, ValidationError

# ============================================================================
# BASIC EXAMPLES
# ============================================================================

# Simple user registration schema
user_registration_schema = Schema(
    {
        'email': Schema.string().email().required(),
        'password': Schema.string().min(8).required(),
        'name': Schema.string().min(2).max(50).required(),
        'age': Schema.number().int().min(18).optional(),
    }
)

# Article creation schema
article_schema = Schema(
    {
        'title': Schema.string().min(5).max(200).required(),
        'slug': Schema.string().pattern(r'^[a-z0-9-]+$', 'Slug must be lowercase with hyphens').required(),
        'content': Schema.string().min(50).required(),
        'published': Schema.boolean().default(False),
        'category_id': Schema.string().required(),
        'tags': Schema.array(Schema.string()).min(1).max(10).optional(),
    }
)

# Category schema
category_schema = Schema(
    {
        'name': Schema.string().min(2).max(50).required(),
        'slug': Schema.string().pattern(r'^[a-z0-9-]+$').required(),
        'description': Schema.string().max(500).optional(),
    }
)

# User profile update schema
profile_update_schema = Schema(
    {
        'name': Schema.string().min(2).max(50).optional(),
        'bio': Schema.string().max(500).optional(),
        'website': Schema.string().url().optional(),
        'location': Schema.string().max(100).optional(),
    }
)


# ============================================================================
# FLASK ROUTE EXAMPLES
# ============================================================================


def register_route_example():
    """Example of using validator in a registration route."""
    from flask import request

    data = request.get_json()

    # Validate input
    try:
        validated_data = user_registration_schema.validate(data)
        # Use validated_data - it's sanitized and validated
        email = validated_data['email']
        password = validated_data['password']
        name = validated_data['name']

        # Create user...
        return jsonify({'message': 'User created'}), 201

    except ValidationError as e:
        return jsonify({'errors': e.errors}), 400


def create_article_route_example():
    """Example of creating an article with validation."""
    from flask import request

    data = request.get_json()

    # Safe validate returns (success, result_or_errors)
    success, result = article_schema.safe_validate(data)

    if not success:
        return jsonify({'errors': result}), 400

    # Use validated data
    article_data = result
    # Create article...
    return jsonify({'message': 'Article created', 'data': article_data}), 201


# ============================================================================
# ADVANCED EXAMPLES
# ============================================================================

# Nested object validation
user_with_address_schema = Schema(
    {
        'email': Schema.string().email().required(),
        'name': Schema.string().required(),
        'address': Schema.object(
            {
                'street': Schema.string().required(),
                'city': Schema.string().required(),
                'zipcode': Schema.string().pattern(r'^\d{5}$', 'Invalid zipcode').required(),
            }
        ).required(),
    }
)

# Array of objects
order_schema = Schema(
    {
        'customer_id': Schema.string().required(),
        'items': Schema.array(
            Schema.object(
                {
                    'product_id': Schema.string().required(),
                    'quantity': Schema.number().int().min(1).required(),
                    'price': Schema.number().min(0).required(),
                }
            )
        )
        .min(1)
        .required(),
        'status': Schema.enum(['pending', 'processing', 'shipped', 'delivered']).default('pending'),
    }
)

# Custom validation
password_schema = Schema(
    {
        'password': Schema.string()
        .min(8, 'Password must be at least 8 characters')
        .custom(lambda x: any(c.isupper() for c in x), 'Password must contain at least one uppercase letter')
        .custom(lambda x: any(c.isdigit() for c in x), 'Password must contain at least one number')
        .custom(lambda x: any(c in '!@#$%^&*' for c in x), 'Password must contain at least one special character')
        .required()
    }
)

# Email with transformation
email_schema = Schema(
    {
        'email': Schema.string()
        .email()
        .trim()  # Remove whitespace
        .transform(lambda x: x.lower())  # Convert to lowercase
        .required()
    }
)

# Conditional validation based on role
user_with_role_schema = Schema(
    {
        'email': Schema.string().email().required(),
        'name': Schema.string().required(),
        'role': Schema.enum(['admin', 'user', 'guest']).default('user'),
        'permissions': Schema.array(Schema.string()).optional(),
    }
)


# ============================================================================
# PRACTICAL USAGE IN ROUTES
# ============================================================================


def example_auth_routes():
    """Example authentication routes with validation."""
    from flask import Blueprint, request

    auth_bp = Blueprint('auth_validated', __name__, url_prefix='/api/auth')

    @auth_bp.route('/register', methods=['POST'])
    def register():
        """
        Register a new user.
        ---
        tags:
          - Authentication
        parameters:
          - in: body
            name: body
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
                password:
                  type: string
                  minLength: 8
                name:
                  type: string
                  minLength: 2
        responses:
          201:
            description: User registered successfully
          400:
            description: Validation error
        """
        data = request.get_json()

        try:
            validated = user_registration_schema.validate(data)

            # Check if user exists
            from app.models import User

            if User.find_by_email(validated['email']):
                return jsonify({'error': 'Email already registered'}), 400

            # Create user
            user_id = User.insert_one(
                {
                    'email': validated['email'],
                    'password': hash_password(validated['password']),
                    'name': validated['name'],
                    'age': validated.get('age'),
                }
            )

            return jsonify({'message': 'User registered successfully', 'user_id': user_id}), 201

        except ValidationError as e:
            return jsonify({'errors': e.errors}), 400

    @auth_bp.route('/login', methods=['POST'])
    def login():
        """Login with validation."""
        login_schema = Schema({'email': Schema.string().email().required(), 'password': Schema.string().required()})

        data = request.get_json()

        try:
            validated = login_schema.validate(data)

            # Authenticate user...
            return jsonify({'message': 'Login successful', 'token': 'jwt_token'}), 200

        except ValidationError as e:
            return jsonify({'errors': e.errors}), 400

    return auth_bp


def example_article_routes():
    """Example article routes with validation."""
    from flask import Blueprint, request

    articles_bp = Blueprint('articles_validated', __name__, url_prefix='/api/articles')

    @articles_bp.route('', methods=['POST'])
    def create_article():
        """Create article with validation."""
        data = request.get_json()

        success, result = article_schema.safe_validate(data)

        if not success:
            return jsonify({'errors': result}), 400

        # Create article
        from app.models import Article

        article_id = Article.insert_one(result)

        return jsonify({'message': 'Article created', 'article_id': article_id}), 201

    @articles_bp.route('/<article_id>', methods=['PUT'])
    def update_article(article_id):
        """Update article with partial validation."""
        # For updates, make all fields optional
        update_schema = Schema(
            {
                'title': Schema.string().min(5).max(200).optional(),
                'content': Schema.string().min(50).optional(),
                'published': Schema.boolean().optional(),
                'tags': Schema.array(Schema.string()).max(10).optional(),
            }
        )

        data = request.get_json()

        try:
            validated = update_schema.validate(data)

            # Update article
            from bson import ObjectId

            from app.models import Article

            Article.update_one({'_id': ObjectId(article_id)}, {'$set': validated})

            return jsonify({'message': 'Article updated'}), 200

        except ValidationError as e:
            return jsonify({'errors': e.errors}), 400

    return articles_bp


# ============================================================================
# HELPER FUNCTIONS
# ============================================================================


def validate_request(schema: Schema):
    """Decorator for validating request data."""
    from functools import wraps

    from flask import request

    def decorator(f):
        @wraps(f)
        def wrapper(*args, **kwargs):
            data = request.get_json()

            try:
                validated_data = schema.validate(data)
                # Pass validated data to the route function
                return f(validated_data, *args, **kwargs)
            except ValidationError as e:
                return jsonify({'errors': e.errors}), 400

        return wrapper

    return decorator


# Usage with decorator
def example_with_decorator():
    """Example using validation decorator."""
    from flask import Blueprint

    bp = Blueprint('example', __name__)

    @bp.route('/users', methods=['POST'])
    @validate_request(user_registration_schema)
    def create_user(validated_data):
        # validated_data is already validated
        # No need for manual validation
        return jsonify({'message': 'User created', 'data': validated_data}), 201


def hash_password(password: str) -> str:
    """Placeholder for password hashing."""
    # In real app, use bcrypt or similar
    return password


if __name__ == '__main__':
    # Test examples
    print('Testing validation examples...')

    # Test valid data
    valid_user = {'email': 'user@example.com', 'password': 'SecurePass123', 'name': 'John Doe', 'age': 25}

    try:
        result = user_registration_schema.validate(valid_user)
        print('✓ Valid user data:', result)
    except ValidationError as e:
        print('✗ Validation failed:', e.errors)

    # Test invalid data
    invalid_user = {
        'email': 'not-an-email',
        'password': '123',  # Too short
        'name': 'J',  # Too short
    }

    try:
        result = user_registration_schema.validate(invalid_user)
        print('✗ Should have failed')
    except ValidationError as e:
        print('✓ Correctly caught errors:', e.errors)
