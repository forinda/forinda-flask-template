# Validator Usage Guide

A Zod-like validation library for Python Flask applications.

## Quick Start

```python
from app.lib import Schema, ValidationError

# Define schema
user_schema = Schema({
    'email': Schema.string().email().required(),
    'name': Schema.string().min(2).max(50).required(),
    'age': Schema.number().int().min(18).optional()
})

# Validate data
try:
    validated = user_schema.validate(data)
    # Use validated data
except ValidationError as e:
    # Handle errors: e.errors is a list of error dictionaries
    return jsonify({'errors': e.errors}), 400
```

## Field Types

### String Field

```python
Schema.string()
    .min(5)                    # Minimum length
    .max(50)                   # Maximum length
    .email()                   # Email format
    .url()                     # URL format
    .pattern(r'^[a-z]+$')     # Regex pattern
    .alpha()                   # Only letters
    .alphanumeric()           # Letters and numbers
    .lowercase()              # Must be lowercase
    .uppercase()              # Must be uppercase
    .trim()                    # Trim whitespace
    .required()               # Field is required
    .optional()               # Field is optional
    .default('value')         # Default value
```

### Number Field

```python
Schema.number()
    .int()                     # Convert to integer
    .min(0)                    # Minimum value
    .max(100)                  # Maximum value
    .positive()               # Must be positive
    .negative()               # Must be negative
    .required()
```

### Boolean Field

```python
Schema.boolean()
    .default(True)
    .required()
```

### Enum Field

```python
Schema.enum(['admin', 'user', 'guest'])
    .default('user')
    .required()
```

### Array Field

```python
# Simple array
Schema.array()
    .min(1)                    # Minimum items
    .max(10)                   # Maximum items
    .required()

# Array with item validation
Schema.array(Schema.string().email())
    .min(1)
    .max(5)
    .required()
```

### Object Field

```python
Schema.object({
    'name': Schema.string().required(),
    'age': Schema.number().int().required()
})
.required()
```

## Common Schemas

### User Registration

```python
user_registration = Schema({
    'email': Schema.string().email().trim().required(),
    'password': Schema.string()
        .min(8, 'Password must be at least 8 characters')
        .custom(
            lambda x: any(c.isupper() for c in x),
            'Password must contain uppercase letter'
        )
        .required(),
    'name': Schema.string().min(2).max(50).required(),
    'terms_accepted': Schema.boolean().required()
})
```

### Article Creation

```python
article_schema = Schema({
    'title': Schema.string().min(5).max(200).required(),
    'slug': Schema.string()
        .pattern(r'^[a-z0-9-]+$', 'Invalid slug format')
        .required(),
    'content': Schema.string().min(50).required(),
    'published': Schema.boolean().default(False),
    'category_id': Schema.string().required(),
    'tags': Schema.array(Schema.string()).max(10).optional()
})
```

### User Login

```python
login_schema = Schema({
    'email': Schema.string().email().required(),
    'password': Schema.string().required()
})
```

### Profile Update

```python
profile_update = Schema({
    'name': Schema.string().min(2).max(50).optional(),
    'bio': Schema.string().max(500).optional(),
    'website': Schema.string().url().optional(),
    'avatar_url': Schema.string().url().optional()
})
```

## Flask Route Integration

### Basic Usage

```python
from flask import Blueprint, request, jsonify
from app.lib import Schema, ValidationError

bp = Blueprint('users', __name__)

user_schema = Schema({
    'email': Schema.string().email().required(),
    'name': Schema.string().required()
})

@bp.route('/users', methods=['POST'])
def create_user():
    data = request.get_json()
    
    try:
        validated = user_schema.validate(data)
        # Use validated data
        return jsonify(validated), 201
    except ValidationError as e:
        return jsonify({'errors': e.errors}), 400
```

### Safe Validate (No Exception)

```python
@bp.route('/users', methods=['POST'])
def create_user():
    data = request.get_json()
    
    success, result = user_schema.safe_validate(data)
    
    if not success:
        return jsonify({'errors': result}), 400
    
    # Use result (validated data)
    return jsonify(result), 201
```

### With Decorator

```python
from functools import wraps

def validate_request(schema):
    """Decorator for validating request data."""
    def decorator(f):
        @wraps(f)
        def wrapper(*args, **kwargs):
            data = request.get_json()
            try:
                validated = schema.validate(data)
                return f(validated, *args, **kwargs)
            except ValidationError as e:
                return jsonify({'errors': e.errors}), 400
        return wrapper
    return decorator

# Usage
@bp.route('/users', methods=['POST'])
@validate_request(user_schema)
def create_user(validated_data):
    # validated_data is already validated
    return jsonify(validated_data), 201
```

## Real-World Examples

### Auth Registration

```python
from app.lib import Schema, ValidationError
from app.models import User

registration_schema = Schema({
    'email': Schema.string().email().trim().transform(str.lower).required(),
    'password': Schema.string().min(8).required(),
    'name': Schema.string().min(2).max(50).trim().required()
})

@auth_bp.route('/register', methods=['POST'])
def register():
    data = request.get_json()
    
    try:
        validated = registration_schema.validate(data)
        
        # Check if user exists
        if User.find_by_email(validated['email']):
            return jsonify({'error': 'Email already registered'}), 400
        
        # Create user
        user_id = User.insert_one({
            'email': validated['email'],
            'password': hash_password(validated['password']),
            'name': validated['name']
        })
        
        return jsonify({'user_id': user_id}), 201
        
    except ValidationError as e:
        return jsonify({'errors': e.errors}), 400
```

### Article with Nested Data

```python
article_with_author = Schema({
    'title': Schema.string().min(5).required(),
    'content': Schema.string().min(50).required(),
    'author': Schema.object({
        'name': Schema.string().required(),
        'email': Schema.string().email().required()
    }).required(),
    'tags': Schema.array(Schema.string().min(2)).max(10).optional(),
    'metadata': Schema.object({
        'views': Schema.number().int().default(0),
        'likes': Schema.number().int().default(0)
    }).optional()
})
```

### Bulk Operations

```python
bulk_update_schema = Schema({
    'items': Schema.array(
        Schema.object({
            'id': Schema.string().required(),
            'status': Schema.enum(['active', 'inactive']).required()
        })
    ).min(1).max(100).required()
})

@bp.route('/bulk-update', methods=['POST'])
def bulk_update():
    data = request.get_json()
    
    try:
        validated = bulk_update_schema.validate(data)
        # Process bulk update
        for item in validated['items']:
            # Update item
            pass
        return jsonify({'updated': len(validated['items'])}), 200
    except ValidationError as e:
        return jsonify({'errors': e.errors}), 400
```

## Custom Validators

```python
def is_strong_password(password):
    """Custom password strength validator."""
    has_upper = any(c.isupper() for c in password)
    has_lower = any(c.islower() for c in password)
    has_digit = any(c.isdigit() for c in password)
    has_special = any(c in '!@#$%^&*()_+-=[]{}|;:,.<>?' for c in password)
    return has_upper and has_lower and has_digit and has_special

password_schema = Schema({
    'password': Schema.string()
        .min(8)
        .custom(is_strong_password, 'Password too weak')
        .required()
})
```

## Error Handling

### Error Response Format

```python
{
    "errors": [
        {
            "field": "email",
            "message": "Invalid email address"
        },
        {
            "field": "password",
            "message": "String must be at least 8 characters"
        }
    ]
}
```

### Custom Error Messages

```python
Schema({
    'email': Schema.string()
        .email('Please provide a valid email address')
        .required('Email is required'),
    'age': Schema.number()
        .int()
        .min(18, 'You must be at least 18 years old')
        .required('Age is required')
})
```

## Transformations

```python
# Trim and lowercase email
Schema.string()
    .email()
    .trim()
    .transform(str.lower)
    .required()

# Custom transformation
Schema.string()
    .transform(lambda x: x.strip().title())
    .required()
```

## Comparison with Zod (TypeScript)

### Zod (TypeScript)
```typescript
const userSchema = z.object({
  email: z.string().email(),
  age: z.number().int().min(18).optional()
});
```

### Our Validator (Python)
```python
user_schema = Schema({
    'email': Schema.string().email().required(),
    'age': Schema.number().int().min(18).optional()
})
```

## Best Practices

1. **Define schemas once, reuse everywhere**
```python
# schemas.py
USER_REGISTRATION = Schema({...})
USER_LOGIN = Schema({...})

# In routes
from schemas import USER_REGISTRATION
```

2. **Use safe_validate for non-critical paths**
```python
success, result = schema.safe_validate(data)
if not success:
    logger.warning(f'Validation failed: {result}')
```

3. **Combine with database models**
```python
validated = user_schema.validate(data)
user_id = User.insert_one(validated)
```

4. **Use transforms for data cleaning**
```python
Schema.string().trim().transform(str.lower)
```

5. **Provide clear error messages**
```python
Schema.string().min(8, 'Password must be at least 8 characters long')
```

## Testing

```python
def test_user_validation():
    schema = Schema({
        'email': Schema.string().email().required(),
        'name': Schema.string().required()
    })
    
    # Valid data
    result = schema.validate({
        'email': 'test@example.com',
        'name': 'Test User'
    })
    assert result['email'] == 'test@example.com'
    
    # Invalid data
    try:
        schema.validate({'email': 'invalid'})
        assert False, 'Should have raised ValidationError'
    except ValidationError as e:
        assert len(e.errors) > 0
```

## Available in

```python
from app.lib import Schema, ValidationError
```

## Summary

- ✅ Zod-like API for Python
- ✅ Type-safe validation
- ✅ Clear error messages
- ✅ Support for nested objects and arrays
- ✅ Custom validators
- ✅ Transformations
- ✅ Default values
- ✅ Flask-friendly
