"""
Tests for pagination utility functions.
"""

from app.utils.pagination import create_pagination_meta, get_pagination_params, paginate_response


class TestGetPaginationParams:
    """Test get_pagination_params function."""

    def test_default_params(self, app):
        """Test default pagination parameters."""
        with app.test_request_context('/?'):
            params = get_pagination_params()

            assert params['page'] == 1
            assert params['limit'] == 10
            assert params['skip'] == 0

    def test_custom_page(self, app):
        """Test custom page parameter."""
        with app.test_request_context('/?page=3'):
            params = get_pagination_params()

            assert params['page'] == 3
            assert params['skip'] == 20  # (3-1) * 10

    def test_custom_limit(self, app):
        """Test custom limit parameter."""
        with app.test_request_context('/?limit=25'):
            params = get_pagination_params()

            assert params['limit'] == 25

    def test_max_limit_enforcement(self, app):
        """Test that max_limit is enforced."""
        with app.test_request_context('/?limit=200'):
            params = get_pagination_params(max_limit=100)

            assert params['limit'] == 100  # Clamped to max

    def test_min_page_enforcement(self, app):
        """Test that page cannot be less than 1."""
        with app.test_request_context('/?page=0'):
            params = get_pagination_params()

            assert params['page'] == 1

        with app.test_request_context('/?page=-5'):
            params = get_pagination_params()

            assert params['page'] == 1

    def test_invalid_values(self, app):
        """Test handling of invalid parameter values."""
        with app.test_request_context('/?page=abc&limit=xyz'):
            params = get_pagination_params()

            assert params['page'] == 1
            assert params['limit'] == 10


class TestCreatePaginationMeta:
    """Test create_pagination_meta function."""

    def test_basic_meta(self):
        """Test basic pagination metadata."""
        meta = create_pagination_meta(page=1, limit=10, total=45)

        assert meta['page'] == 1
        assert meta['limit'] == 10
        assert meta['total'] == 45
        assert meta['total_pages'] == 5
        assert meta['has_next'] is True
        assert meta['has_prev'] is False

    def test_middle_page(self):
        """Test metadata for middle page."""
        meta = create_pagination_meta(page=3, limit=10, total=50)

        assert meta['page'] == 3
        assert meta['has_next'] is True
        assert meta['has_prev'] is True

    def test_last_page(self):
        """Test metadata for last page."""
        meta = create_pagination_meta(page=5, limit=10, total=45)

        assert meta['page'] == 5
        assert meta['has_next'] is False
        assert meta['has_prev'] is True

    def test_with_data(self):
        """Test metadata with data included."""
        data = [{'id': 1}, {'id': 2}, {'id': 3}]
        result = create_pagination_meta(page=1, limit=10, total=3, data=data)

        assert 'data' in result
        assert 'meta' in result
        assert result['data'] == data
        assert result['meta']['total'] == 3

    def test_empty_results(self):
        """Test pagination with no results."""
        meta = create_pagination_meta(page=1, limit=10, total=0)

        assert meta['total'] == 0
        assert meta['total_pages'] == 0
        assert meta['has_next'] is False
        assert meta['has_prev'] is False


class TestPaginateResponse:
    """Test paginate_response function."""

    def test_basic_response(self, app):
        """Test basic paginated response."""
        items = [{'id': i} for i in range(10)]

        with app.test_request_context('/?page=1&limit=10'):
            response = paginate_response(items, total=45)

            assert 'data' in response
            assert 'meta' in response
            assert len(response['data']) == 10
            assert response['meta']['total'] == 45
            assert response['meta']['page'] == 1

    def test_with_explicit_params(self):
        """Test response with explicit page and limit."""
        items = [{'id': i} for i in range(5)]
        response = paginate_response(items, total=25, page=2, limit=5)

        assert response['meta']['page'] == 2
        assert response['meta']['limit'] == 5
        assert response['meta']['total'] == 25
        assert response['meta']['total_pages'] == 5

    def test_empty_results(self, app):
        """Test response with empty results."""
        with app.test_request_context('/?'):
            response = paginate_response([], total=0)

            assert response['data'] == []
            assert response['meta']['total'] == 0
            assert response['meta']['total_pages'] == 0


class TestPaginationCalculations:
    """Test pagination calculation edge cases."""

    def test_total_pages_calculation(self):
        """Test correct total_pages calculation."""
        # Exact division
        meta = create_pagination_meta(page=1, limit=10, total=100)
        assert meta['total_pages'] == 10

        # With remainder
        meta = create_pagination_meta(page=1, limit=10, total=105)
        assert meta['total_pages'] == 11

        # Less than one page
        meta = create_pagination_meta(page=1, limit=10, total=5)
        assert meta['total_pages'] == 1

    def test_skip_calculation(self, app):
        """Test skip value calculation."""
        # Page 1
        with app.test_request_context('/?page=1&limit=10'):
            params = get_pagination_params()
            assert params['skip'] == 0

        # Page 2
        with app.test_request_context('/?page=2&limit=10'):
            params = get_pagination_params()
            assert params['skip'] == 10

        # Page 3 with custom limit
        with app.test_request_context('/?page=3&limit=25'):
            params = get_pagination_params()
            assert params['skip'] == 50  # (3-1) * 25
