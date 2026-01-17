# Schemas Structure

The schemas are organized into separate files by domain for better maintainability:

## Structure

```
app/schemas/
├── __init__.py          # Exports all schemas
├── auth.py              # Authentication schemas (register, login)
├── category.py          # Category schemas (create, update)
├── article.py           # Article schemas (create, update)
├── collection.py        # Collection schemas (create, update, add article)
└── file.py              # File upload schemas
```

## Usage

Import schemas from the main schemas module:

```python
from app.schemas import (
    REGISTER_SCHEMA,
    LOGIN_SCHEMA,
    CREATE_CATEGORY_SCHEMA,
    UPDATE_CATEGORY_SCHEMA,
    CREATE_ARTICLE_SCHEMA,
    UPDATE_ARTICLE_SCHEMA,
    # etc.
)
```

## Adding New Schemas

1. Create a new file in `app/schemas/` (e.g., `comment.py`)
2. Define your schemas using the Schema class:

```python
from app.lib import Schema

CREATE_COMMENT_SCHEMA = Schema({
    'content': Schema.string().min(10).max(500).required(),
    'article_id': Schema.string().required()
})
```

3. Export in `__init__.py`:

```python
from app.schemas.comment import CREATE_COMMENT_SCHEMA

__all__ = [
    # ... existing schemas
    'CREATE_COMMENT_SCHEMA',
]
```

## Pagination

All list endpoints enforce pagination. Use the pagination utilities:

```python
from app.utils.pagination import get_pagination_params, paginate_response

@route('/items', methods=['GET'])
def get_items():
    # Get pagination parameters from query string
    params = get_pagination_params(default_limit=10, max_limit=100)
    
    # Query with pagination
    items = Model.find_many({}, skip=params['skip'], limit=params['limit'])
    total = Model.count({})
    
    # Return paginated response
    response = paginate_response(items, total, params['page'], params['limit'])
    return jsonify(response), 200
```

### Pagination Response Format

```json
{
  "data": [...],
  "meta": {
    "page": 1,
    "limit": 10,
    "total": 45,
    "total_pages": 5,
    "has_next": true,
    "has_prev": false
  }
}
```

### Query Parameters

- `page` - Page number (default: 1, min: 1)
- `limit` - Items per page (default: 10, max: 100)
