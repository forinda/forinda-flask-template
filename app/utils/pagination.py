"""
Pagination utility functions.
"""

from typing import Any

from flask import request


def get_pagination_params(default_limit: int = 10, max_limit: int = 100) -> dict[str, int]:
    """
    Extract pagination parameters from request query string.

    Args:
        default_limit: Default number of items per page
        max_limit: Maximum allowed items per page

    Returns:
        Dictionary with 'page', 'limit', and 'skip' values
    """
    try:
        page = int(request.args.get('page', 1))
        page = max(1, page)  # Ensure page is at least 1
    except (ValueError, TypeError):
        page = 1

    try:
        limit = int(request.args.get('limit', default_limit))
        limit = max(1, min(limit, max_limit))  # Clamp between 1 and max_limit
    except (ValueError, TypeError):
        limit = default_limit

    skip = (page - 1) * limit

    return {'page': page, 'limit': limit, 'skip': skip}


def create_pagination_meta(page: int, limit: int, total: int, data: list[Any] = None) -> dict[str, Any]:
    """
    Create pagination metadata for API responses.

    Args:
        page: Current page number
        limit: Items per page
        total: Total number of items
        data: Optional list of data items to include

    Returns:
        Dictionary with pagination metadata and optional data
    """
    total_pages = (total + limit - 1) // limit if limit > 0 else 0
    has_next = page < total_pages
    has_prev = page > 1

    meta = {
        'page': page,
        'limit': limit,
        'total': total,
        'total_pages': total_pages,
        'has_next': has_next,
        'has_prev': has_prev,
    }

    if data is not None:
        return {'data': data, 'meta': meta}

    return meta


def paginate_response(items: list[Any], total: int, page: int = None, limit: int = None) -> dict[str, Any]:
    """
    Create a complete paginated response.

    Args:
        items: List of items for current page
        total: Total number of items across all pages
        page: Current page number (if None, extracted from request)
        limit: Items per page (if None, extracted from request)

    Returns:
        Dictionary with items and pagination metadata
    """
    if page is None or limit is None:
        params = get_pagination_params()
        page = page or params['page']
        limit = limit or params['limit']

    return create_pagination_meta(page, limit, total, items)
