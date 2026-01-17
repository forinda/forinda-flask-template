# Flask API with MongoDB

A RESTful API built with Flask and MongoDB featuring authentication, file management, and comprehensive documentation.

## Features

- 🗄️ **MongoDB Database** - NoSQL database integration
- 🔐 **Authentication API** - User registration, login, and session management
- 📁 **File Management** - Upload, download, and manage files
- 📝 **Articles & Categories** - Content management system
- 📚 **Collections** - Organize articles into collections
- 📊 **Swagger Documentation** - Interactive API documentation
- 🔒 **CORS Support** - Cross-origin resource sharing
- 📝 **Logging** - Comprehensive logging with rotation
- ⚙️ **Settings Management** - Centralized configuration

## Prerequisites

- Python 3.12+
- pipenv
- MongoDB 4.4+ (running locally or remotely)

## Quick Start

### 1. Install MongoDB

**Ubuntu/Debian:**
```bash
sudo apt-get install mongodb
sudo systemctl start mongodb
```

**macOS:**
```bash
brew tap mongodb/brew
brew install mongodb-community
brew services start mongodb-community
```

**Docker:**
```bash
docker run -d -p 27017:27017 --name mongodb mongo:latest
```

### 2. Setup Project

Clone and install dependencies:
```bash
git clone <repository-url>
cd tt-env
pipenv install
```

### 3. Configure Environment

Generate environment file:
```bash
# Using Python script (recommended)
python generate_env.py

# Or using bash script
./generate_env.sh
```

Update `.env` with your MongoDB connection:
```env
MONGODB_URI=mongodb://localhost:27017/
MONGODB_DB_NAME=flask_app
```

### 4. Start Application

```bash
./start.sh
```

The API will be available at `http://localhost:8000`

## MongoDB Setup

### Local MongoDB
```env
MONGODB_URI=mongodb://localhost:27017/
```

### MongoDB Atlas (Cloud)
```env
MONGODB_URI=mongodb+srv://username:password@cluster.mongodb.net/?retryWrites=true&w=majority
```

### MongoDB with Authentication
```env
MONGODB_URI=mongodb://username:password@localhost:27017/
```

## Database Models

### Collections

- **users** - User accounts and authentication
- **articles** - Blog posts and content
- **categories** - Content categories
- **collections** - User-created article collections
- **files** - File metadata

### Indexes

The application automatically creates indexes for:
- User emails (unique)
- Article slugs (unique)
- Category slugs (unique)
- Text search on articles
- Timestamps for sorting

## API Documentation

Interactive API documentation: **http://localhost:8000/api/docs**

## API Endpoints

### Health
- `GET /api/health` - Health check

### Authentication
- `POST /api/auth/register` - Register new user
- `POST /api/auth/login` - User login
- `POST /api/auth/logout` - User logout
- `GET /api/auth/me` - Get current user

### Categories
- `GET /api/categories` - List categories
- `POST /api/categories` - Create category
- `GET /api/categories/{id}` - Get category
- `PUT /api/categories/{id}` - Update category
- `DELETE /api/categories/{id}` - Delete category

### Articles
- `GET /api/articles` - List articles
- `POST /api/articles` - Create article
- `GET /api/articles/{id}` - Get article
- `PUT /api/articles/{id}` - Update article
- `DELETE /api/articles/{id}` - Delete article
- `POST /api/articles/{id}/publish` - Publish article

### Collections
- `GET /api/collections` - List collections
- `POST /api/collections` - Create collection
- `GET /api/collections/{id}` - Get collection
- `PUT /api/collections/{id}` - Update collection
- `DELETE /api/collections/{id}` - Delete collection
- `POST /api/collections/{id}/articles` - Add article
- `DELETE /api/collections/{id}/articles/{article_id}` - Remove article

### Files
- `GET /api/files` - List files
- `POST /api/files/upload` - Upload file
- `GET /api/files/{filename}` - Get file details
- `GET /api/files/{filename}/download` - Download file
- `DELETE /api/files/{filename}` - Delete file

### Storage
- `GET /api/storage/info` - Storage statistics

## Project Structure

```
tt-env/
├── app/
│   ├── __init__.py
│   ├── app.py              # Application factory
│   ├── database.py         # MongoDB connection
│   ├── models.py           # MongoDB models
│   ├── settings.py         # Configuration
│   ├── swagger.py          # API documentation config
│   ├── routes/             # API blueprints
│   └── utils/              # Utilities
├── logs/                   # Application logs
├── uploads/                # Uploaded files
├── .env.example            # Environment template
├── .gitignore             # Git ignore rules
├── .gitattributes         # Git attributes
├── generate_env.py        # Env generator (Python)
├── generate_env.sh        # Env generator (Bash)
├── main.py                # Entry point
├── Pipfile                # Dependencies
└── README.md              # Documentation
```

## Development

### MongoDB Shell

Connect to database:
```bash
mongosh
use flask_app
db.users.find()
```

### View Collections

```bash
mongosh --eval "use flask_app; show collections"
```

### Backup Database

```bash
mongodump --db flask_app --out ./backup
```

### Restore Database

```bash
mongorestore --db flask_app ./backup/flask_app
```

## Production Deployment

1. Set environment to production:
```env
FLASK_ENV=production
DEBUG=False
```

2. Use production MongoDB:
```env
MONGODB_URI=mongodb+srv://user:pass@cluster.mongodb.net/
```

3. Deploy with gunicorn:
```bash
pipenv run gunicorn -w 4 -b 0.0.0.0:8000 'app.app:create_app()'
```

## Troubleshooting

### MongoDB Connection Error

```bash
# Check MongoDB is running
sudo systemctl status mongodb

# Check connection
mongosh --eval "db.adminCommand('ping')"
```

### Permission Issues

```bash
# Fix MongoDB permissions
sudo chown -R mongodb:mongodb /var/lib/mongodb
sudo systemctl restart mongodb
```

## License

[Your License]

## Contributing

[Contributing Guidelines]
