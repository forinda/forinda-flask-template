"""
Tests for category endpoints.
"""

import json


class TestGetCategories:
    """Test retrieving categories."""

    def test_get_categories(self, client):
        """Test getting list of categories."""
        response = client.get('/api/categories')

        assert response.status_code == 200
        data = json.loads(response.data)
        assert 'data' in data
        assert 'meta' in data
        assert 'page' in data['meta']
        assert 'limit' in data['meta']
        assert 'total' in data['meta']
        assert 'total_pages' in data['meta']

    def test_get_categories_pagination(self, client):
        """Test category pagination."""
        response = client.get('/api/categories?page=1&limit=5')

        assert response.status_code == 200
        data = json.loads(response.data)
        assert data['meta']['page'] == 1
        assert data['meta']['limit'] == 5


class TestCreateCategory:
    """Test creating categories."""

    def test_create_category_success(self, client, clean_db):
        """Test successful category creation."""
        response = client.post(
            '/api/categories',
            data=json.dumps({'name': 'Test Category', 'slug': 'test-category', 'description': 'A test category'}),
            content_type='application/json',
            headers={'Authorization': 'Bearer mock_token'},
        )

        assert response.status_code == 201
        data = json.loads(response.data)
        assert data['message'] == 'Category created successfully'
        assert 'category_id' in data

    def test_create_category_duplicate_slug(self, client, clean_db):
        """Test creating category with duplicate slug."""
        # Create first category
        client.post(
            '/api/categories',
            data=json.dumps({'name': 'Test Category', 'slug': 'test-dup-category', 'description': 'Test'}),
            content_type='application/json',
            headers={'Authorization': 'Bearer mock_token'},
        )

        # Try to create with same slug
        response = client.post(
            '/api/categories',
            data=json.dumps({'name': 'Another Category', 'slug': 'test-dup-category', 'description': 'Test'}),
            content_type='application/json',
            headers={'Authorization': 'Bearer mock_token'},
        )

        assert response.status_code == 400
        data = json.loads(response.data)
        assert 'error' in data

    def test_create_category_invalid_slug(self, client):
        """Test creating category with invalid slug."""
        response = client.post(
            '/api/categories',
            data=json.dumps({'name': 'Test', 'slug': 'Invalid Slug!', 'description': 'Test'}),
            content_type='application/json',
            headers={'Authorization': 'Bearer mock_token'},
        )

        assert response.status_code == 400
        data = json.loads(response.data)
        assert 'errors' in data

    def test_create_category_requires_auth(self, client):
        """Test that creating category requires authentication."""
        response = client.post(
            '/api/categories',
            data=json.dumps({'name': 'Test', 'slug': 'test', 'description': 'Test'}),
            content_type='application/json',
        )

        assert response.status_code == 401


class TestUpdateCategory:
    """Test updating categories."""

    def test_update_category(self, client, clean_db):
        """Test updating a category."""
        # Create category first
        create_response = client.post(
            '/api/categories',
            data=json.dumps({'name': 'Original Name', 'slug': 'test-update-cat', 'description': 'Original'}),
            content_type='application/json',
            headers={'Authorization': 'Bearer mock_token'},
        )
        category_id = json.loads(create_response.data)['category_id']

        # Update category
        response = client.put(
            f'/api/categories/{category_id}',
            data=json.dumps({'name': 'Updated Name', 'description': 'Updated description'}),
            content_type='application/json',
            headers={'Authorization': 'Bearer mock_token'},
        )

        assert response.status_code == 200
        data = json.loads(response.data)
        assert data['message'] == 'Category updated successfully'

    def test_update_nonexistent_category(self, client):
        """Test updating non-existent category."""
        response = client.put(
            '/api/categories/507f1f77bcf86cd799439011',
            data=json.dumps({'name': 'Updated'}),
            content_type='application/json',
            headers={'Authorization': 'Bearer mock_token'},
        )

        assert response.status_code == 404


class TestDeleteCategory:
    """Test deleting categories."""

    def test_delete_category(self, client, clean_db):
        """Test deleting a category."""
        # Create category first
        create_response = client.post(
            '/api/categories',
            data=json.dumps({'name': 'To Delete', 'slug': 'test-delete-cat', 'description': 'Will be deleted'}),
            content_type='application/json',
            headers={'Authorization': 'Bearer mock_token'},
        )
        category_id = json.loads(create_response.data)['category_id']

        # Delete category
        response = client.delete(f'/api/categories/{category_id}', headers={'Authorization': 'Bearer mock_token'})

        assert response.status_code == 200
        data = json.loads(response.data)
        assert data['message'] == 'Category deleted successfully'

    def test_delete_nonexistent_category(self, client):
        """Test deleting non-existent category."""
        response = client.delete(
            '/api/categories/507f1f77bcf86cd799439011', headers={'Authorization': 'Bearer mock_token'}
        )

        assert response.status_code == 404
