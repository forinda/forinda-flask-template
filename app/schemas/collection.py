"""
Collection validation schemas.
"""

from app.lib import Schema

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
