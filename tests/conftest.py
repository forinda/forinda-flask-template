"""
Test configuration and fixtures.
"""

import pytest

from app.app import create_app
from app.database import MongoDB


@pytest.fixture
def app():
    """Create and configure a test application instance."""
    app = create_app()
    app.config['TESTING'] = True

    yield app

    # Cleanup
    MongoDB.close()


@pytest.fixture
def client(app):
    """Create a test client for the app."""
    return app.test_client()


@pytest.fixture
def runner(app):
    """Create a test CLI runner."""
    return app.test_cli_runner()


@pytest.fixture
def clean_db():
    """Clean database before tests."""
    # Note: In production, use a separate test database
    db = MongoDB.get_db()

    # Clear test collections
    db.users.delete_many({'email': {'$regex': 'test.*@example.com'}})
    db.categories.delete_many({'slug': {'$regex': '^test-'}})
    db.articles.delete_many({'slug': {'$regex': '^test-'}})

    yield db

    # Cleanup after tests
    db.users.delete_many({'email': {'$regex': 'test.*@example.com'}})
    db.categories.delete_many({'slug': {'$regex': '^test-'}})
    db.articles.delete_many({'slug': {'$regex': '^test-'}})
