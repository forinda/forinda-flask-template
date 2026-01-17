"""
Tests for authentication endpoints.
"""

import json


class TestRegister:
    """Test user registration endpoint."""

    def test_register_success(self, client, clean_db):
        """Test successful user registration."""
        response = client.post(
            '/api/auth/register',
            data=json.dumps({'email': 'testuser@example.com', 'password': 'SecurePass123', 'name': 'Test User'}),
            content_type='application/json',
        )

        assert response.status_code == 201
        data = json.loads(response.data)
        assert data['message'] == 'User registered successfully'
        assert 'user' in data
        assert data['user']['email'] == 'testuser@example.com'

    def test_register_duplicate_email(self, client, clean_db):
        """Test registration with duplicate email."""
        # Register first user
        client.post(
            '/api/auth/register',
            data=json.dumps({'email': 'testdup@example.com', 'password': 'SecurePass123', 'name': 'Test User'}),
            content_type='application/json',
        )

        # Try to register again with same email
        response = client.post(
            '/api/auth/register',
            data=json.dumps({'email': 'testdup@example.com', 'password': 'AnotherPass123', 'name': 'Another User'}),
            content_type='application/json',
        )

        assert response.status_code == 400
        data = json.loads(response.data)
        assert 'error' in data

    def test_register_invalid_email(self, client):
        """Test registration with invalid email."""
        response = client.post(
            '/api/auth/register',
            data=json.dumps({'email': 'not-an-email', 'password': 'SecurePass123', 'name': 'Test User'}),
            content_type='application/json',
        )

        assert response.status_code == 400
        data = json.loads(response.data)
        assert 'errors' in data

    def test_register_weak_password(self, client):
        """Test registration with weak password."""
        response = client.post(
            '/api/auth/register',
            data=json.dumps({'email': 'test@example.com', 'password': 'weak', 'name': 'Test User'}),
            content_type='application/json',
        )

        assert response.status_code == 400
        data = json.loads(response.data)
        assert 'errors' in data

    def test_register_missing_fields(self, client):
        """Test registration with missing fields."""
        response = client.post(
            '/api/auth/register', data=json.dumps({'email': 'test@example.com'}), content_type='application/json'
        )

        assert response.status_code == 400


class TestLogin:
    """Test user login endpoint."""

    def test_login_success(self, client, clean_db):
        """Test successful login."""
        # Register user first
        client.post(
            '/api/auth/register',
            data=json.dumps({'email': 'testlogin@example.com', 'password': 'SecurePass123', 'name': 'Test User'}),
            content_type='application/json',
        )

        # Login
        response = client.post(
            '/api/auth/login',
            data=json.dumps({'email': 'testlogin@example.com', 'password': 'SecurePass123'}),
            content_type='application/json',
        )

        assert response.status_code == 200
        data = json.loads(response.data)
        assert 'token' in data
        assert 'user' in data

    def test_login_invalid_credentials(self, client, clean_db):
        """Test login with invalid credentials."""
        response = client.post(
            '/api/auth/login',
            data=json.dumps({'email': 'nonexistent@example.com', 'password': 'WrongPass123'}),
            content_type='application/json',
        )

        assert response.status_code == 401
        data = json.loads(response.data)
        assert 'error' in data

    def test_login_missing_fields(self, client):
        """Test login with missing fields."""
        response = client.post(
            '/api/auth/login', data=json.dumps({'email': 'test@example.com'}), content_type='application/json'
        )

        assert response.status_code == 400


class TestProtectedEndpoints:
    """Test protected endpoints requiring authentication."""

    def test_logout_requires_auth(self, client):
        """Test that logout requires authentication."""
        response = client.post('/api/auth/logout')
        assert response.status_code == 401

    def test_get_profile_requires_auth(self, client):
        """Test that getting profile requires authentication."""
        response = client.get('/api/auth/me')
        assert response.status_code == 401

    def test_get_profile_with_auth(self, client):
        """Test getting profile with valid token."""
        response = client.get('/api/auth/me', headers={'Authorization': 'Bearer mock_token'})

        # Should return 200 or 404 depending on if mock user exists
        assert response.status_code in [200, 404]
