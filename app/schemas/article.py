"""
Article validation schemas.
"""

from app.lib import Schema

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
