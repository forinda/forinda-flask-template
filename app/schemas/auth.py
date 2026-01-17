"""
Authentication validation schemas.
"""

from app.core import Schema

REGISTER_SCHEMA = Schema(
    {
        'email': Schema.string().email().trim().transform(str.lower).required(),
        'password': Schema.string()
        .min(8, 'Password must be at least 8 characters')
        .custom(lambda x: any(c.isupper() for c in x), 'Password must contain at least one uppercase letter')
        .custom(lambda x: any(c.islower() for c in x), 'Password must contain at least one lowercase letter')
        .custom(lambda x: any(c.isdigit() for c in x), 'Password must contain at least one number')
        .required(),
        'name': Schema.string().min(2).max(100).trim().required(),
    }
)

LOGIN_SCHEMA = Schema(
    {'email': Schema.string().email().trim().transform(str.lower).required(), 'password': Schema.string().required()}
)
