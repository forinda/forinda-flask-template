# Project Structure - Models Organization

## Directory Structure

```
app/
├── lib/                          # Reusable library classes
│   ├── __init__.py
│   └── base_model.py            # BaseModel with CRUD operations
│
├── models/                       # Individual model files
│   ├── __init__.py              # Exports all models
│   ├── user.py                  # User model
│   ├── article.py               # Article model
│   ├── category.py              # Category model
│   ├── collection.py            # Collection model
│   └── file.py                  # File model
│
├── routes/                       # API route blueprints
├── utils/                        # Utility functions
├── app.py                        # Flask application factory
├── database.py                   # MongoDB connection
└── settings.py                   # Configuration
```

## Import Examples

### Importing Models

```python
# Import all models
from app.models import User, Article, Category, Collection, File

# Import specific models
from app.models import User
from app.models.article import Article
```

### Importing BaseModel

```python
# For extending BaseModel in new models
from app.lib import BaseModel
from app.lib.base_model import BaseModel  # Alternative
```

### Using Models in Routes

```python
from flask import Blueprint, jsonify, request
from app.models import User, Article

@bp.route('/users', methods=['GET'])
def get_users():
    users = User.find_many(limit=20)
    return jsonify(users), 200

@bp.route('/articles/<slug>', methods=['GET'])
def get_article(slug):
    article = Article.find_by_slug(slug)
    if not article:
        return jsonify({'error': 'Not found'}), 404
    return jsonify(article), 200
```

## Model Files Overview

### app/lib/base_model.py
**Purpose**: Reusable base class with common CRUD operations

**Methods**:
- `get_collection()` - Get MongoDB collection
- `find_one(query, session=None)` - Find single document
- `find_many(query, skip, limit, sort, session=None)` - Find multiple documents
- `count(query, session=None)` - Count documents
- `insert_one(document, session=None)` - Insert document
- `update_one(query, update, session=None)` - Update document
- `delete_one(query, session=None)` - Delete document
- `find_by_id(doc_id, session=None)` - Find by ID

### app/models/user.py
**Collection**: `users`  
**Indexes**: `email` (unique), `created_at`

**Custom Methods**:
- `find_by_email(email, session=None)` - Find user by email

**Usage**:
```python
from app.models import User

# Create user
user_id = User.insert_one({
    'email': 'user@example.com',
    'name': 'John Doe',
    'password': 'hashed_password'
})

# Find user
user = User.find_by_email('user@example.com')
```

### app/models/article.py
**Collection**: `articles`  
**Indexes**: `slug` (unique), `category_id`, `author_id`, `published`, `created_at`, text search

**Custom Methods**:
- `find_by_slug(slug, session=None)` - Find by slug
- `find_by_category(category_id, skip, limit, session=None)` - Find by category
- `search(search_term, skip, limit, session=None)` - Full-text search

**Usage**:
```python
from app.models import Article

# Create article
article_id = Article.insert_one({
    'title': 'My Article',
    'slug': 'my-article',
    'content': 'Article content...',
    'author_id': user_id,
    'published': True
})

# Find by slug
article = Article.find_by_slug('my-article')

# Search articles
results = Article.search('python programming', limit=10)
```

### app/models/category.py
**Collection**: `categories`  
**Indexes**: `slug` (unique), `name`

**Custom Methods**:
- `find_by_slug(slug, session=None)` - Find by slug

**Usage**:
```python
from app.models import Category

# Create category
category_id = Category.insert_one({
    'name': 'Technology',
    'slug': 'technology',
    'description': 'Tech articles'
})

# Find by slug
category = Category.find_by_slug('technology')
```

### app/models/collection.py
**Collection**: `collections`  
**Indexes**: `user_id`, `is_public`, `created_at`

**Custom Methods**:
- `find_by_user(user_id, skip, limit, session=None)` - Find user's collections
- `add_article(collection_id, article_id, session=None)` - Add article to collection
- `remove_article(collection_id, article_id, session=None)` - Remove article from collection

**Usage**:
```python
from app.models import Collection

# Create collection
collection_id = Collection.insert_one({
    'name': 'Favorites',
    'user_id': user_id,
    'article_ids': [],
    'is_public': False
})

# Add article to collection
Collection.add_article(collection_id, article_id)

# Get user's collections
collections = Collection.find_by_user(user_id)
```

### app/models/file.py
**Collection**: `files`  
**Indexes**: `filename` (unique), `created_at`

**Custom Methods**:
- `find_by_filename(filename, session=None)` - Find by filename

**Usage**:
```python
from app.models import File

# Create file record
file_id = File.insert_one({
    'filename': 'document.pdf',
    'original_name': 'My Document.pdf',
    'size': 1024000,
    'mime_type': 'application/pdf',
    'user_id': user_id
})

# Find by filename
file = File.find_by_filename('document.pdf')
```

## Creating New Models

To create a new model, inherit from `BaseModel`:

```python
# app/models/comment.py
from typing import Optional, Dict, List
from app.lib.base_model import BaseModel


class Comment(BaseModel):
    """Comment model for article comments."""
    
    collection_name = 'comments'
    
    @classmethod
    def find_by_article(cls, article_id: str, skip: int = 0, limit: int = 10, session=None) -> List[Dict]:
        """Find comments for an article."""
        return cls.find_many(
            {'article_id': article_id},
            skip=skip,
            limit=limit,
            sort=[('created_at', -1)],
            session=session
        )
```

Then add to `app/models/__init__.py`:

```python
from app.models.comment import Comment

__all__ = ['User', 'Article', 'Category', 'Collection', 'File', 'Comment']
```

## Transaction Support

All model methods support transactions via the optional `session` parameter:

```python
from app.database import MongoDB
from app.models import User, Article

with MongoDB.transaction() as session:
    # Create user in transaction
    user_id = User.insert_one({
        'email': 'user@example.com',
        'name': 'John Doe'
    }, session=session)
    
    # Create article in same transaction
    Article.insert_one({
        'title': 'First Post',
        'author_id': user_id,
        'published': True
    }, session=session)
```

## Benefits of This Structure

### ✅ Separation of Concerns
- **app/lib/** - Reusable library classes (BaseModel)
- **app/models/** - Business-specific models (User, Article, etc.)
- Clear distinction between framework and application code

### ✅ Maintainability
- Each model in its own file
- Easy to locate and modify specific models
- Reduced merge conflicts in team environments

### ✅ Scalability
- Add new models without modifying existing files
- BaseModel can be extended with new functionality
- Models are independently testable

### ✅ Reusability
- BaseModel can be used across multiple projects
- Common patterns extracted to library
- DRY (Don't Repeat Yourself) principle

### ✅ Organization
- Logical file structure
- Easy navigation
- Self-documenting code organization

## Testing Models

```python
# tests/test_models.py
from app.models import User

def test_user_creation():
    user_id = User.insert_one({
        'email': 'test@example.com',
        'name': 'Test User'
    })
    assert user_id is not None
    
    user = User.find_by_id(user_id)
    assert user['email'] == 'test@example.com'

def test_user_find_by_email():
    user = User.find_by_email('test@example.com')
    assert user is not None
    assert user['name'] == 'Test User'
```

## Migration Notes

The old monolithic `app/models.py` has been backed up to `app/models.py.backup`.

All imports remain compatible:
- `from app.models import User` ✅ Still works
- All existing code continues to function
- No breaking changes to the API

To remove the backup file:
```bash
rm app/models.py.backup
```
