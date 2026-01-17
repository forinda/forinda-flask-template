from flask import Blueprint, jsonify, request

from app.models import Category
from app.utils.decorators import handle_errors
from app.utils.logger import get_logger

logger = get_logger(__name__)
categories_bp = Blueprint('categories', __name__, url_prefix='/api/categories')


@categories_bp.route('', methods=['GET'])
@handle_errors
def get_categories():
    """
    Get all categories
    ---
    tags:
      - Categories
    summary: Retrieve all categories
    description: Returns a list of all categories with optional pagination
    parameters:
      - in: query
        name: page
        type: integer
        default: 1
        description: Page number
      - in: query
        name: limit
        type: integer
        default: 10
        description: Number of items per page
    responses:
      200:
        description: List of categories
        schema:
          type: object
          properties:
            categories:
              type: array
              items:
                type: object
                properties:
                  id:
                    type: string
                    example: 507f1f77bcf86cd799439011
                  name:
                    type: string
                    example: Technology
                  slug:
                    type: string
                    example: technology
                  description:
                    type: string
                    example: Technology related articles
                  created_at:
                    type: string
                    format: date-time
            total:
              type: integer
              example: 50
            page:
              type: integer
              example: 1
            limit:
              type: integer
              example: 10
    """
    page = request.args.get('page', 1, type=int)
    limit = request.args.get('limit', 10, type=int)

    skip = (page - 1) * limit

    categories = Category.find_many({}, skip=skip, limit=limit, sort=[('created_at', -1)])
    total = Category.count({})

    logger.info(f'Get categories: page={page}, limit={limit}, total={total}')

    # Remove MongoDB _id from response
    for cat in categories:
        cat.pop('_id', None)

    return jsonify(categories=categories, total=total, page=page, limit=limit), 200


@categories_bp.route('/<int:category_id>', methods=['GET'])
def get_category(category_id):
    """
    Get a specific category
    ---
    tags:
      - Categories
    summary: Retrieve a single category
    description: Returns details of a specific category by ID
    parameters:
      - in: path
        name: category_id
        type: integer
        required: true
        description: Category ID
    responses:
      200:
        description: Category details
        schema:
          type: object
          properties:
            id:
              type: integer
              example: 1
            name:
              type: string
              example: Technology
            slug:
              type: string
              example: technology
            description:
              type: string
              example: Technology related articles
            created_at:
              type: string
              format: date-time
      404:
        description: Category not found
    """
    logger.info(f'Get category: {category_id}')

    # TODO: Implement actual database query
    return jsonify(
        id=category_id,
        name='Technology',
        slug='technology',
        description='Technology related articles',
        created_at='2026-01-17T10:00:00Z',
    ), 200


@categories_bp.route('', methods=['POST'])
def create_category():
    """
    Create a new category
    ---
    tags:
      - Categories
    summary: Create a new category
    description: Creates a new category
    security:
      - Bearer: []
    parameters:
      - in: body
        name: body
        description: Category data
        required: true
        schema:
          type: object
          required:
            - name
            - slug
          properties:
            name:
              type: string
              example: Technology
            slug:
              type: string
              example: technology
            description:
              type: string
              example: Technology related articles
    responses:
      201:
        description: Category created successfully
        schema:
          type: object
          properties:
            message:
              type: string
              example: Category created successfully
            category:
              type: object
      400:
        description: Invalid input
      401:
        description: Unauthorized
    """
    data = request.get_json()

    if not data or not all(key in data for key in ['name', 'slug']):
        logger.warning('Create category attempt with missing fields')
        return jsonify(error='Missing required fields: name, slug'), 400

    logger.info(f'Create category: {data.get("name")}')

    # TODO: Implement actual database insertion
    return jsonify(
        message='Category created successfully',
        category={
            'id': 1,
            'name': data['name'],
            'slug': data['slug'],
            'description': data.get('description', ''),
            'created_at': '2026-01-17T10:00:00Z',
        },
    ), 201


@categories_bp.route('/<int:category_id>', methods=['PUT'])
def update_category(category_id):
    """
    Update a category
    ---
    tags:
      - Categories
    summary: Update an existing category
    description: Updates category information
    security:
      - Bearer: []
    parameters:
      - in: path
        name: category_id
        type: integer
        required: true
        description: Category ID
      - in: body
        name: body
        description: Category data to update
        schema:
          type: object
          properties:
            name:
              type: string
              example: Technology
            slug:
              type: string
              example: technology
            description:
              type: string
              example: Updated description
    responses:
      200:
        description: Category updated successfully
        schema:
          type: object
          properties:
            message:
              type: string
              example: Category updated successfully
            category:
              type: object
      404:
        description: Category not found
      401:
        description: Unauthorized
    """
    data = request.get_json()
    logger.info(f'Update category: {category_id}')

    # TODO: Implement actual database update
    return jsonify(
        message='Category updated successfully',
        category={
            'id': category_id,
            'name': data.get('name', 'Technology'),
            'slug': data.get('slug', 'technology'),
            'description': data.get('description', ''),
            'updated_at': '2026-01-17T10:00:00Z',
        },
    ), 200


@categories_bp.route('/<int:category_id>', methods=['DELETE'])
def delete_category(category_id):
    """
    Delete a category
    ---
    tags:
      - Categories
    summary: Delete a category
    description: Deletes a category by ID
    security:
      - Bearer: []
    parameters:
      - in: path
        name: category_id
        type: integer
        required: true
        description: Category ID
    responses:
      200:
        description: Category deleted successfully
        schema:
          type: object
          properties:
            message:
              type: string
              example: Category deleted successfully
      404:
        description: Category not found
      401:
        description: Unauthorized
    """
    logger.info(f'Delete category: {category_id}')

    # TODO: Implement actual database deletion
    return jsonify(message='Category deleted successfully'), 200
