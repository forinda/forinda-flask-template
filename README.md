# Flask REST API

A production-ready Flask REST API with MongoDB, JWT authentication, and comprehensive Swagger documentation.

## Features

- 🔐 **JWT Authentication** - Secure token-based authentication with role-based access control
- 📝 **Swagger/OpenAPI Documentation** - Interactive API documentation at `/`
- ✅ **Zod-like Validation** - Type-safe request validation with detailed error messages
- 🗄️ **MongoDB Integration** - MongoDB with transaction support and optimized indexes
- 🔄 **API Versioning** - Clean `/api/v1` prefix for all endpoints
- 📄 **Pagination** - Built-in pagination utilities for list endpoints
- 🎨 **Code Quality** - Ruff linting and formatting with pre-commit hooks
- 🏗️ **Clean Architecture** - Organized project structure with separation of concerns
- 🔒 **CORS Support** - Configurable CORS settings for frontend integration
- 📊 **Logging** - Comprehensive logging with file rotation

## Tech Stack

- **Python 3.12+**
- **Flask 3.1.2** - Web framework
- **MongoDB 4.0+** - Database with transaction support
- **PyJWT** - JWT token generation and validation
- **Flasgger** - Swagger/OpenAPI documentation
- **Ruff** - Fast Python linter and formatter
- **Pipenv** - Dependency management

## Quick Start

### Prerequisites

- Python 3.12 or higher
- MongoDB 4.0 or higher (running on localhost:27017)
- Pipenv (install with `pip install pipenv`)

### Installation

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd tt-env
   ```

2. **Install dependencies**
   ```bash
   pipenv install
   ```

3. **Activate virtual environment**
   ```bash
   pipenv shell
   ```

4. **Set environment variables** (optional)
   ```bash
   cp .env.example .env
   # Edit .env with your settings
   ```

5. **Run the application**
   ```bash
   ./start.sh
   # Or: flask run --host=0.0.0.0 --port=8000
   ```

6. **Access the API**
   - API: http://localhost:8000
   - Swagger Docs: http://localhost:8000/

## Configuration

Environment variables (create `.env` file):

```env
# Flask
FLASK_APP=main.py
FLASK_ENV=development
DEBUG=True
HOST=0.0.0.0
PORT=8000

# MongoDB
MONGODB_URI=mongodb://localhost:27017/
MONGODB_DB_NAME=flask_app
MONGODB_TIMEOUT=5000

# Security
SECRET_KEY=your-secret-key-change-in-production

# JWT
JWT_EXPIRATION_HOURS=24
JWT_REFRESH_EXPIRATION_DAYS=7

# Logging
LOG_LEVEL=DEBUG
LOG_DIR=logs
```

## API Documentation

### Authentication

All authenticated endpoints require a JWT token in the Authorization header:

```bash
Authorization: Bearer <your-jwt-token>
# Or just the token directly:
Authorization: <your-jwt-token>
```

#### Register a new user
```bash
POST /api/v1/auth/register
Content-Type: application/json

{
  "email": "user@example.com",
  "password": "SecurePassword123!",
  "name": "John Doe"
}
```

#### Login
```bash
POST /api/v1/auth/login
Content-Type: application/json

{
  "email": "user@example.com",
  "password": "SecurePassword123!"
}

Response:
{
  "message": "Login successful",
  "token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "user": {
    "id": "507f1f77bcf86cd799439011",
    "email": "user@example.com",
    "name": "John Doe"
  }
}
```

### Using Swagger UI

1. Navigate to http://localhost:8000/
2. Click **Authorize** button (top right)
3. Paste your JWT token (from login response)
4. Click **Authorize**, then **Close**
5. All requests will now include the auth token

### Available Endpoints

- **Authentication**: `/api/v1/auth/*`
  - `POST /register` - Register new user
  - `POST /login` - Login user
  - `POST /logout` - Logout user (requires auth)
  - `GET /me` - Get current user profile (requires auth)

- **Categories**: `/api/v1/categories/*`
  - `GET /` - List all categories (with pagination)
  - `POST /` - Create category (requires auth)
  - `GET /{id}` - Get category by ID
  - `PUT /{id}` - Update category (requires auth)
  - `DELETE /{id}` - Delete category (requires auth)

- **Articles**: `/api/v1/articles/*`
  - `GET /` - List all articles (with pagination)
  - `POST /` - Create article (requires auth)
  - `GET /{id}` - Get article by ID
  - `PUT /{id}` - Update article (requires auth)
  - `DELETE /{id}` - Delete article (requires auth)
  - `GET /category/{category_id}` - Get articles by category

- **Collections**: `/api/v1/collections/*`
- **Files**: `/api/v1/files/*`
- **Storage**: `/api/v1/storage/*`

## Project Structure

```
tt-env/
├── app/
│   ├── __init__.py
│   ├── app.py                 # Application factory
│   ├── database.py            # MongoDB connection
│   ├── settings.py            # Configuration
│   ├── swagger.py             # Swagger configuration
│   ├── core/
│   │   └── base_model.py      # Base model class
│   ├── lib/
│   │   ├── validator.py       # Zod-like validation
│   │   └── base_model.py      # Model base class
│   ├── models/
│   │   ├── user.py
│   │   ├── category.py
│   │   ├── article.py
│   │   └── ...
│   ├── routes/
│   │   ├── auth.py
│   │   ├── categories.py
│   │   ├── articles.py
│   │   └── ...
│   ├── schemas/
│   │   ├── auth.py            # Auth validation schemas
│   │   ├── category.py
│   │   ├── article.py
│   │   └── ...
│   └── utils/
│       ├── decorators.py      # @login_required, @role_required
│       ├── jwt_utils.py       # JWT token utilities
│       ├── logger.py          # Logging configuration
│       └── pagination.py      # Pagination helpers
├── logs/                      # Application logs
├── uploads/                   # File uploads
├── tests/                     # Test files
├── main.py                    # Application entry point
├── start.sh                   # Startup script
├── Pipfile                    # Dependencies
├── pyproject.toml            # Ruff configuration
└── README.md                 # This file
```

## Development

### Code Quality

**Linting and formatting with Ruff:**
```bash
# Check code
ruff check .

# Fix issues
ruff check --fix .

# Format code
ruff format .

# Run linting script
./lint.sh
```

### Creating New Endpoints

1. **Define validation schema** in `app/schemas/`
2. **Create model** in `app/models/`
3. **Create route** in `app/routes/`
4. **Register blueprint** in `app/app.py`
5. **Add Swagger documentation** in route docstrings

### Using Decorators

```python
from app.utils.decorators import login_required, role_required, validate_request
from app.schemas import MY_SCHEMA

# Require authentication
@bp.route('/protected')
@login_required
def protected_route():
    pass

# Require specific role
@bp.route('/admin')
@role_required('admin')
def admin_only():
    pass

# Multiple roles
@bp.route('/content')
@role_required('admin', 'editor')
def manage_content():
    pass

# Validate request body
@bp.route('/create', methods=['POST'])
@validate_request(MY_SCHEMA)
def create_item(validated_data):
    # validated_data is guaranteed to match schema
    pass
```

### Validation Schemas

Using the Zod-like validator:

```python
from app.lib.validator import Schema

# Define schema
user_schema = Schema({
    'email': Schema.string().email().required(),
    'name': Schema.string().min(2).max(50).required(),
    'age': Schema.number().min(18).optional(),
    'role': Schema.enum(['admin', 'user', 'guest']).default('user'),
})

# Validate data
try:
    validated = user_schema.validate(data)
except ValidationError as e:
    print(e.errors)  # List of validation errors
```

## Testing

```bash
# Run tests
pytest

# Run with coverage
pytest --cov=app

# Run specific test file
pytest tests/test_auth.py
```

## Deployment

### Production Checklist

- [ ] Change `SECRET_KEY` to a strong random value
- [ ] Set `DEBUG=False`
- [ ] Use production MongoDB instance
- [ ] Configure CORS origins for your frontend
- [ ] Set up proper logging
- [ ] Use environment variables for sensitive data
- [ ] Use a production WSGI server (gunicorn)
- [ ] Set up HTTPS/SSL
- [ ] Configure rate limiting
- [ ] Set up monitoring and error tracking

### Running with Gunicorn

```bash
gunicorn -w 4 -b 0.0.0.0:8000 "main:create_app()"
```

## API Response Format

### Success Response
```json
{
  "message": "Operation successful",
  "data": { ... }
}
```

### Error Response
```json
{
  "error": "Error message",
  "errors": [
    {
      "field": "email",
      "message": "Invalid email format"
    }
  ]
}
```

### Paginated Response
```json
{
  "data": [...],
  "meta": {
    "page": 1,
    "limit": 10,
    "total": 100,
    "total_pages": 10,
    "has_next": true,
    "has_prev": false
  }
}
```

## Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## License

This project is licensed under the MIT License.

## Support

For issues and questions, please open an issue on GitHub.
