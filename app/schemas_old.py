"""
Validation schemas for API endpoints.
"""

from app.lib import Schema

# ============================================================================
# Authentication Schemas
# ============================================================================

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


# ============================================================================
# Category Schemas
# ============================================================================

CREATE_CATEGORY_SCHEMA = Schema(
    {
        'name': Schema.string().min(2).max(100).trim().required(),
        'slug': Schema.string()
        .pattern(r'^[a-z0-9-]+$', 'Slug must be lowercase letters, numbers, and hyphens only')
        .min(2)
        .max(100)
        .required(),
        'description': Schema.string().max(500).trim().optional(),
    }
)

UPDATE_CATEGORY_SCHEMA = Schema(
    {
        'name': Schema.string().min(2).max(100).trim().optional(),
        'slug': Schema.string()
        .pattern(r'^[a-z0-9-]+$', 'Slug must be lowercase letters, numbers, and hyphens only')
        .min(2)
        .max(100)
        .optional(),
        'description': Schema.string().max(500).trim().optional(),
    }
)


# ============================================================================
# Article Schemas
# ============================================================================

CREATE_ARTICLE_SCHEMA = Schema(
    {
        'title': Schema.string().min(5).max(200).trim().required(),
        'slug': Schema.string()
        .pattern(r'^[a-z0-9-]+$', 'Slug must be lowercase letters, numbers, and hyphens only')
        .min(5)
        .max(200)
        .required(),
        'content': Schema.string().min(50).required(),
        'excerpt': Schema.string().max(500).trim().optional(),
        'category_id': Schema.string().required(),
        'published': Schema.boolean().default(False),
        'tags': Schema.array(Schema.string().min(2).max(50)).max(10).optional(),
    }
)

UPDATE_ARTICLE_SCHEMA = Schema(
    {
        'title': Schema.string().min(5).max(200).trim().optional(),
        'slug': Schema.string()
        .pattern(r'^[a-z0-9-]+$', 'Slug must be lowercase letters, numbers, and hyphens only')
        .min(5)
        .max(200)
        .optional(),
        'content': Schema.string().min(50).optional(),
        'excerpt': Schema.string().max(500).trim().optional(),
        'category_id': Schema.string().optional(),
        'published': Schema.boolean().optional(),
        'tags': Schema.array(Schema.string().min(2).max(50)).max(10).optional(),
    }
)


# ============================================================================
# Collection Schemas
# ============================================================================

CREATE_COLLECTION_SCHEMA = Schema(
    {
        'name': Schema.string().min(2).max(100).trim().required(),
        'description': Schema.string().max(500).trim().optional(),
        'is_public': Schema.boolean().default(False),
    }
)

UPDATE_COLLECTION_SCHEMA = Schema(
    {
        'name': Schema.string().min(2).max(100).trim().optional(),
        'description': Schema.string().max(500).trim().optional(),
        'is_public': Schema.boolean().optional(),
    }
)

ADD_ARTICLE_TO_COLLECTION_SCHEMA = Schema({'article_id': Schema.string().required()})


# ============================================================================
# File Upload Schemas
# ============================================================================

FILE_UPLOAD_SCHEMA = Schema(
    {'description': Schema.string().max(500).optional(), 'tags': Schema.array(Schema.string()).max(10).optional()}
)
