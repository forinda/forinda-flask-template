"""
Category validation schemas.
"""

from app.lib import Schema

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
