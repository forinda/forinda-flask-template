from bson import ObjectId
from flask import Blueprint, jsonify

from app.models import Category
from app.schemas import CREATE_CATEGORY_SCHEMA, UPDATE_CATEGORY_SCHEMA
from app.utils.decorators import handle_errors, require_auth, validate_request
from app.utils.logger import get_logger
from app.utils.pagination import get_pagination_params, paginate_response

logger = get_logger(__name__)
categories_bp = Blueprint('categories', __name__, url_prefix='/api/v1/categories')


@categories_bp.route('', methods=['GET'])
@handle_errors
def get_categories():
    """Get all categories with pagination
    ---
    tags:
      - Categories
    parameters:
      - name: page
        in: query
        type: integer
        default: 1
        description: Page number
      - name: limit
        in: query
        type: integer
        default: 10
        description: Items per page (max 100)
    responses:
      200:
        description: List of categories
        schema:
          type: object
          properties:
            data:
              type: array
              items:
                type: object
                properties:
                  id:
                    type: string
                  name:
                    type: string
                  slug:
                    type: string
                  description:
                    type: string
                  created_at:
                    type: string
            meta:
              type: object
              properties:
                page:
                  type: integer
                limit:
                  type: integer
                total:
                  type: integer
                total_pages:
                  type: integer
                has_next:
                  type: boolean
                has_prev:
                  type: boolean
    """
    params = get_pagination_params(default_limit=10, max_limit=100)

    categories = Category.find_many({}, skip=params['skip'], limit=params['limit'], sort=[('created_at', -1)])
    total = Category.count({})

    for cat in categories:
        cat.pop('_id', None)

    response = paginate_response(categories, total, params['page'], params['limit'])
    return jsonify(response), 200


@categories_bp.route('/<category_id>', methods=['GET'])
@handle_errors
def get_category(category_id):
    """Get a specific category by ID
    ---
    tags:
      - Categories
    parameters:
      - name: category_id
        in: path
        type: string
        required: true
        description: Category ID
    responses:
      200:
        description: Category details
        schema:
          type: object
          properties:
            id:
              type: string
            name:
              type: string
            slug:
              type: string
            description:
              type: string
            created_at:
              type: string
      404:
        description: Category not found
    """
    category = Category.find_by_id(category_id)

    if not category:
        return jsonify({'error': 'Category not found'}), 404

    category.pop('_id', None)
    return jsonify(category), 200


@categories_bp.route('', methods=['POST'])
@require_auth
@validate_request(CREATE_CATEGORY_SCHEMA)
@handle_errors
def create_category(validated_data):
    """Create a new category
    ---
    tags:
      - Categories
    security:
      - Bearer: []
    parameters:
      - name: body
        in: body
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
              pattern: "^[a-z0-9-]+$"
              example: technology
            description:
              type: string
              example: Technology related articles
    responses:
      201:
        description: Category created successfully
      400:
        description: Validation error or duplicate slug
      401:
        description: Unauthorized
    """
    # Check if slug already exists
    existing = Category.find_by_slug(validated_data['slug'])
    if existing:
        return jsonify({'error': 'Category with this slug already exists'}), 400

    category_id = Category.insert_one(validated_data)
    logger.info(f'Category created: {validated_data["name"]} (ID: {category_id})')

    return jsonify(message='Category created successfully', category_id=category_id), 201


@categories_bp.route('/<category_id>', methods=['PUT'])
@require_auth
@validate_request(UPDATE_CATEGORY_SCHEMA)
@handle_errors
def update_category(validated_data, category_id):
    """Update a category
    ---
    tags:
      - Categories
    security:
      - Bearer: []
    parameters:
      - name: category_id
        in: path
        type: string
        required: true
        description: Category ID
      - name: body
        in: body
        required: true
        schema:
          type: object
          properties:
            name:
              type: string
            slug:
              type: string
              pattern: "^[a-z0-9-]+$"
            description:
              type: string
    responses:
      200:
        description: Category updated successfully
      400:
        description: Validation error or duplicate slug
      401:
        description: Unauthorized
      404:
        description: Category not found
    """
    category = Category.find_by_id(category_id)
    if not category:
        return jsonify({'error': 'Category not found'}), 404

    # Check slug uniqueness if slug is being updated
    if 'slug' in validated_data and validated_data['slug'] != category.get('slug'):
        existing = Category.find_by_slug(validated_data['slug'])
        if existing:
            return jsonify({'error': 'Category with this slug already exists'}), 400

    success = Category.update_one({'_id': ObjectId(category_id)}, {'$set': validated_data})

    if success:
        logger.info(f'Category updated: {category_id}')
        return jsonify(message='Category updated successfully'), 200

    return jsonify({'error': 'Failed to update category'}), 500


@categories_bp.route('/<category_id>', methods=['DELETE'])
@require_auth
@handle_errors
def delete_category(category_id):
    """Delete a category
    ---
    tags:
      - Categories
    security:
      - Bearer: []
    parameters:
      - name: category_id
        in: path
        type: string
        required: true
        description: Category ID
    responses:
      200:
        description: Category deleted successfully
      401:
        description: Unauthorized
      404:
        description: Category not found
    """
    category = Category.find_by_id(category_id)
    if not category:
        return jsonify({'error': 'Category not found'}), 404

    success = Category.delete_one({'_id': ObjectId(category_id)})

    if success:
        logger.info(f'Category deleted: {category_id}')
        return jsonify(message='Category deleted successfully'), 200

    return jsonify({'error': 'Failed to delete category'}), 500
