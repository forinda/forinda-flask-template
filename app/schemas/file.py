"""
File upload validation schemas.
"""

from app.lib import Schema

FILE_UPLOAD_SCHEMA = Schema(
    {'description': Schema.string().max(500).optional(), 'tags': Schema.array(Schema.string()).max(10).optional()}
)
