from flask import Blueprint, jsonify, request
from app.utils.logger import get_logger

logger = get_logger(__name__)
articles_bp = Blueprint('articles', __name__, url_prefix='/api/articles')


@articles_bp.route('', methods=['GET'])
def get_articles():
    """
    Get all articles
    ---
    tags:
      - Articles
    summary: Retrieve all articles
    description: Returns a list of all articles with optional filtering and pagination
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
      - in: query
        name: category_id
        type: integer
        description: Filter by category ID
      - in: query
        name: author_id
        type: integer
        description: Filter by author ID
      - in: query
        name: search
        type: string
        description: Search in title and content
    responses:
      200:
        description: List of articles
        schema:
          type: object
          properties:
            articles:
              type: array
              items:
                type: object
                properties:
                  id:
                    type: integer
                    example: 1
                  title:
                    type: string
                    example: Introduction to Flask
                  slug:
                    type: string
                    example: introduction-to-flask
                  content:
                    type: string
                    example: Flask is a micro web framework...
                  excerpt:
                    type: string
                    example: Learn the basics of Flask
                  author:
                    type: object
                    properties:
                      id:
                        type: integer
                      name:
                        type: string
                  category:
                    type: object
                    properties:
                      id:
                        type: integer
                      name:
                        type: string
                  published:
                    type: boolean
                  created_at:
                    type: string
                    format: date-time
                  updated_at:
                    type: string
                    format: date-time
            total:
              type: integer
            page:
              type: integer
            limit:
              type: integer
    """
    page = request.args.get('page', 1, type=int)
    limit = request.args.get('limit', 10, type=int)
    category_id = request.args.get('category_id', type=int)
    author_id = request.args.get('author_id', type=int)
    search = request.args.get('search', type=str)
    
    logger.info(f'Get articles: page={page}, limit={limit}, category={category_id}, search={search}')
    
    # TODO: Implement actual database query
    articles = [
        {
            'id': 1,
            'title': 'Introduction to Flask',
            'slug': 'introduction-to-flask',
            'content': 'Flask is a micro web framework written in Python...',
            'excerpt': 'Learn the basics of Flask',
            'author': {'id': 1, 'name': 'John Doe'},
            'category': {'id': 1, 'name': 'Technology'},
            'published': True,
            'created_at': '2026-01-17T10:00:00Z',
            'updated_at': '2026-01-17T10:00:00Z'
        }
    ]
    
    return jsonify(
        articles=articles,
        total=len(articles),
        page=page,
        limit=limit
    ), 200


@articles_bp.route('/<int:article_id>', methods=['GET'])
def get_article(article_id):
    """
    Get a specific article
    ---
    tags:
      - Articles
    summary: Retrieve a single article
    description: Returns details of a specific article by ID
    parameters:
      - in: path
        name: article_id
        type: integer
        required: true
        description: Article ID
    responses:
      200:
        description: Article details
        schema:
          type: object
          properties:
            id:
              type: integer
            title:
              type: string
            slug:
              type: string
            content:
              type: string
            excerpt:
              type: string
            author:
              type: object
            category:
              type: object
            tags:
              type: array
              items:
                type: string
            published:
              type: boolean
            views:
              type: integer
            created_at:
              type: string
              format: date-time
            updated_at:
              type: string
              format: date-time
      404:
        description: Article not found
    """
    logger.info(f'Get article: {article_id}')
    
    # TODO: Implement actual database query
    return jsonify(
        id=article_id,
        title='Introduction to Flask',
        slug='introduction-to-flask',
        content='Flask is a micro web framework written in Python...',
        excerpt='Learn the basics of Flask',
        author={'id': 1, 'name': 'John Doe', 'email': 'john@example.com'},
        category={'id': 1, 'name': 'Technology'},
        tags=['python', 'flask', 'web-development'],
        published=True,
        views=100,
        created_at='2026-01-17T10:00:00Z',
        updated_at='2026-01-17T10:00:00Z'
    ), 200


@articles_bp.route('', methods=['POST'])
def create_article():
    """
    Create a new article
    ---
    tags:
      - Articles
    summary: Create a new article
    description: Creates a new article
    security:
      - Bearer: []
    parameters:
      - in: body
        name: body
        description: Article data
        required: true
        schema:
          type: object
          required:
            - title
            - content
            - category_id
          properties:
            title:
              type: string
              example: Introduction to Flask
            slug:
              type: string
              example: introduction-to-flask
            content:
              type: string
              example: Flask is a micro web framework...
            excerpt:
              type: string
              example: Learn the basics of Flask
            category_id:
              type: integer
              example: 1
            tags:
              type: array
              items:
                type: string
              example: ["python", "flask"]
            published:
              type: boolean
              example: true
    responses:
      201:
        description: Article created successfully
        schema:
          type: object
          properties:
            message:
              type: string
              example: Article created successfully
            article:
              type: object
      400:
        description: Invalid input
      401:
        description: Unauthorized
    """
    data = request.get_json()
    
    if not data or not all(key in data for key in ['title', 'content', 'category_id']):
        logger.warning('Create article attempt with missing fields')
        return jsonify(error='Missing required fields: title, content, category_id'), 400
    
    logger.info(f'Create article: {data.get("title")}')
    
    # TODO: Implement actual database insertion
    return jsonify(
        message='Article created successfully',
        article={
            'id': 1,
            'title': data['title'],
            'slug': data.get('slug', data['title'].lower().replace(' ', '-')),
            'content': data['content'],
            'excerpt': data.get('excerpt', ''),
            'category_id': data['category_id'],
            'tags': data.get('tags', []),
            'published': data.get('published', False),
            'created_at': '2026-01-17T10:00:00Z'
        }
    ), 201


@articles_bp.route('/<int:article_id>', methods=['PUT'])
def update_article(article_id):
    """
    Update an article
    ---
    tags:
      - Articles
    summary: Update an existing article
    description: Updates article information
    security:
      - Bearer: []
    parameters:
      - in: path
        name: article_id
        type: integer
        required: true
        description: Article ID
      - in: body
        name: body
        description: Article data to update
        schema:
          type: object
          properties:
            title:
              type: string
            content:
              type: string
            excerpt:
              type: string
            category_id:
              type: integer
            tags:
              type: array
              items:
                type: string
            published:
              type: boolean
    responses:
      200:
        description: Article updated successfully
        schema:
          type: object
          properties:
            message:
              type: string
              example: Article updated successfully
            article:
              type: object
      404:
        description: Article not found
      401:
        description: Unauthorized
    """
    data = request.get_json()
    logger.info(f'Update article: {article_id}')
    
    # TODO: Implement actual database update
    return jsonify(
        message='Article updated successfully',
        article={
            'id': article_id,
            'title': data.get('title', 'Updated Article'),
            'content': data.get('content', ''),
            'updated_at': '2026-01-17T10:00:00Z'
        }
    ), 200


@articles_bp.route('/<int:article_id>', methods=['DELETE'])
def delete_article(article_id):
    """
    Delete an article
    ---
    tags:
      - Articles
    summary: Delete an article
    description: Deletes an article by ID
    security:
      - Bearer: []
    parameters:
      - in: path
        name: article_id
        type: integer
        required: true
        description: Article ID
    responses:
      200:
        description: Article deleted successfully
        schema:
          type: object
          properties:
            message:
              type: string
              example: Article deleted successfully
      404:
        description: Article not found
      401:
        description: Unauthorized
    """
    logger.info(f'Delete article: {article_id}')
    
    # TODO: Implement actual database deletion
    return jsonify(message='Article deleted successfully'), 200


@articles_bp.route('/<int:article_id>/publish', methods=['POST'])
def publish_article(article_id):
    """
    Publish an article
    ---
    tags:
      - Articles
    summary: Publish or unpublish an article
    description: Change the published status of an article
    security:
      - Bearer: []
    parameters:
      - in: path
        name: article_id
        type: integer
        required: true
        description: Article ID
      - in: body
        name: body
        schema:
          type: object
          properties:
            published:
              type: boolean
              example: true
    responses:
      200:
        description: Article publish status updated
        schema:
          type: object
          properties:
            message:
              type: string
              example: Article published successfully
      404:
        description: Article not found
      401:
        description: Unauthorized
    """
    data = request.get_json()
    published = data.get('published', True)
    
    logger.info(f'{"Publish" if published else "Unpublish"} article: {article_id}')
    
    # TODO: Implement actual database update
    return jsonify(
        message=f'Article {"published" if published else "unpublished"} successfully'
    ), 200
