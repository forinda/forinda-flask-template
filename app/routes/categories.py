from bson import ObjectId
from flask import Blueprint, jsonify

from app.models import Category
from app.schemas import CREATE_CATEGORY_SCHEMA, UPDATE_CATEGORY_SCHEMA
from app.utils.decorators import handle_errors, require_auth, validate_request
from app.utils.logger import get_logger
from app.utils.pagination import get_pagination_params, paginate_response

logger = get_logger(__name__)
categories_bp = Blueprint('categories', __name__, url_prefix='/api/categories')


@categories_bp.route('', methods=['GET'])
@handle_errors
def get_categories():
    """Get all categories with pagination"""
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
    """Get a specific category by ID"""
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
    """Create a new category"""
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
    """Update a category"""
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
    """Delete a category"""
    category = Category.find_by_id(category_id)
    if not category:
        return jsonify({'error': 'Category not found'}), 404

    success = Category.delete_one({'_id': ObjectId(category_id)})

    if success:
        logger.info(f'Category deleted: {category_id}')
        return jsonify(message='Category deleted successfully'), 200

    return jsonify({'error': 'Failed to delete category'}), 500
