from bson import ObjectId
from flask import Blueprint, jsonify, request

from app.models import Article
from app.schemas import CREATE_ARTICLE_SCHEMA, UPDATE_ARTICLE_SCHEMA
from app.utils.decorators import get_user_id_from_token, handle_errors, require_auth, validate_request
from app.utils.logger import get_logger
from app.utils.pagination import get_pagination_params, paginate_response

logger = get_logger(__name__)
articles_bp = Blueprint('articles', __name__, url_prefix='/api/v1/articles')


@articles_bp.route('', methods=['GET'])
@handle_errors
def get_articles():
    """Get all articles with optional filtering
    ---
    tags:
      - Articles
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
      - name: category_id
        in: query
        type: string
        description: Filter by category ID
      - name: search
        in: query
        type: string
        description: Search in title and content
    responses:
      200:
        description: List of articles
        schema:
          type: object
          properties:
            data:
              type: array
              items:
                type: object
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
    category_id = request.args.get('category_id', type=str)
    search = request.args.get('search', type=str)

    query = {}

    if category_id:
        query['category_id'] = category_id

    if search:
        articles = Article.search(search, skip=params['skip'], limit=params['limit'])
        total = len(articles)
    else:
        articles = Article.find_many(query, skip=params['skip'], limit=params['limit'], sort=[('created_at', -1)])
        total = Article.count(query)

    for article in articles:
        article.pop('_id', None)

    response = paginate_response(articles, total, params['page'], params['limit'])
    return jsonify(response), 200


@articles_bp.route('/<article_id>', methods=['GET'])
@handle_errors
def get_article(article_id):
    """Get a specific article
    ---
    tags:
      - Articles
    parameters:
      - name: article_id
        in: path
        type: string
        required: true
        description: Article ID
    responses:
      200:
        description: Article details
      404:
        description: Article not found
    """
    article = Article.find_by_id(article_id)

    if not article:
        return jsonify({'error': 'Article not found'}), 404

    article.pop('_id', None)
    return jsonify(article), 200


@articles_bp.route('', methods=['POST'])
@require_auth
@validate_request(CREATE_ARTICLE_SCHEMA)
@handle_errors
def create_article(validated_data):
    """Create a new article
    ---
    tags:
      - Articles
    security:
      - Bearer: []
    parameters:
      - name: body
        in: body
        required: true
        schema:
          type: object
          required:
            - title
            - slug
            - content
            - category_id
          properties:
            title:
              type: string
              example: My First Article
            slug:
              type: string
              pattern: "^[a-z0-9-]+$"
              example: my-first-article
            content:
              type: string
              example: This is the article content...
            excerpt:
              type: string
              example: Short description
            category_id:
              type: string
            published:
              type: boolean
              default: false
            tags:
              type: array
              items:
                type: string
              example: ["tech", "tutorial"]
    responses:
      201:
        description: Article created successfully
      400:
        description: Validation error or duplicate slug
      401:
        description: Unauthorized
    """
    # Check if slug already exists
    existing = Article.find_by_slug(validated_data['slug'])
    if existing:
        return jsonify({'error': 'Article with this slug already exists'}), 400

    # Add author from token
    validated_data['author_id'] = get_user_id_from_token()

    article_id = Article.insert_one(validated_data)
    logger.info(f'Article created: {validated_data["title"]} (ID: {article_id})')

    return jsonify(message='Article created successfully', article_id=article_id), 201


@articles_bp.route('/<article_id>', methods=['PUT'])
@require_auth
@validate_request(UPDATE_ARTICLE_SCHEMA)
@handle_errors
def update_article(validated_data, article_id):
    """Update an article
    ---
    tags:
      - Articles
    security:
      - Bearer: []
    parameters:
      - name: article_id
        in: path
        type: string
        required: true
        description: Article ID
      - name: body
        in: body
        required: true
        schema:
          type: object
          properties:
            title:
              type: string
            slug:
              type: string
              pattern: "^[a-z0-9-]+$"
            content:
              type: string
            excerpt:
              type: string
            category_id:
              type: string
            published:
              type: boolean
            tags:
              type: array
              items:
                type: string
    responses:
      200:
        description: Article updated successfully
      400:
        description: Validation error or duplicate slug
      401:
        description: Unauthorized
      404:
        description: Article not found
    """
    article = Article.find_by_id(article_id)
    if not article:
        return jsonify({'error': 'Article not found'}), 404

    # Check slug uniqueness if being updated
    if 'slug' in validated_data and validated_data['slug'] != article.get('slug'):
        existing = Article.find_by_slug(validated_data['slug'])
        if existing:
            return jsonify({'error': 'Article with this slug already exists'}), 400

    success = Article.update_one({'_id': ObjectId(article_id)}, {'$set': validated_data})

    if success:
        logger.info(f'Article updated: {article_id}')
        return jsonify(message='Article updated successfully'), 200

    return jsonify({'error': 'Failed to update article'}), 500


@articles_bp.route('/<article_id>', methods=['DELETE'])
@require_auth
@handle_errors
def delete_article(article_id):
    """Delete an article
    ---
    tags:
      - Articles
    security:
      - Bearer: []
    parameters:
      - name: article_id
        in: path
        type: string
        required: true
        description: Article ID
    responses:
      200:
        description: Article deleted successfully
      401:
        description: Unauthorized
      404:
        description: Article not found
    """
    article = Article.find_by_id(article_id)
    if not article:
        return jsonify({'error': 'Article not found'}), 404

    success = Article.delete_one({'_id': ObjectId(article_id)})

    if success:
        logger.info(f'Article deleted: {article_id}')
        return jsonify(message='Article deleted successfully'), 200

    return jsonify({'error': 'Failed to delete article'}), 500


@articles_bp.route('/<article_id>/publish', methods=['POST'])
@require_auth
@handle_errors
def publish_article(article_id):
    """Publish an article
    ---
    tags:
      - Articles
    security:
      - Bearer: []
    parameters:
      - name: article_id
        in: path
        type: string
        required: true
        description: Article ID
    responses:
      200:
        description: Article published successfully
      401:
        description: Unauthorized
      404:
        description: Article not found
    """
    article = Article.find_by_id(article_id)
    if not article:
        return jsonify({'error': 'Article not found'}), 404

    success = Article.update_one({'_id': ObjectId(article_id)}, {'$set': {'published': True}})

    if success:
        logger.info(f'Article published: {article_id}')
        return jsonify(message='Article published successfully'), 200

    return jsonify({'error': 'Failed to publish article'}), 500
