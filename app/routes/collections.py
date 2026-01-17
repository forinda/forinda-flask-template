from flask import Blueprint, jsonify, request

from app.utils.logger import get_logger

logger = get_logger(__name__)
collections_bp = Blueprint('collections', __name__, url_prefix='/api/collections')


@collections_bp.route('', methods=['GET'])
def get_collections():
    """
    Get all collections
    ---
    tags:
      - Collections
    summary: Retrieve all collections
    description: Returns a list of all collections with optional pagination
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
        name: user_id
        type: integer
        description: Filter by user ID
    responses:
      200:
        description: List of collections
        schema:
          type: object
          properties:
            collections:
              type: array
              items:
                type: object
                properties:
                  id:
                    type: integer
                    example: 1
                  name:
                    type: string
                    example: My Favorites
                  description:
                    type: string
                    example: Collection of my favorite articles
                  user:
                    type: object
                    properties:
                      id:
                        type: integer
                      name:
                        type: string
                  article_count:
                    type: integer
                    example: 5
                  is_public:
                    type: boolean
                    example: true
                  created_at:
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
    user_id = request.args.get('user_id', type=int)

    logger.info(f'Get collections: page={page}, limit={limit}, user_id={user_id}')

    # TODO: Implement actual database query
    collections = [
        {
            'id': 1,
            'name': 'My Favorites',
            'description': 'Collection of my favorite articles',
            'user': {'id': 1, 'name': 'John Doe'},
            'article_count': 5,
            'is_public': True,
            'created_at': '2026-01-17T10:00:00Z',
        }
    ]

    return jsonify(collections=collections, total=len(collections), page=page, limit=limit), 200


@collections_bp.route('/<int:collection_id>', methods=['GET'])
def get_collection(collection_id):
    """
    Get a specific collection
    ---
    tags:
      - Collections
    summary: Retrieve a single collection
    description: Returns details of a specific collection including its articles
    parameters:
      - in: path
        name: collection_id
        type: integer
        required: true
        description: Collection ID
    responses:
      200:
        description: Collection details
        schema:
          type: object
          properties:
            id:
              type: integer
            name:
              type: string
            description:
              type: string
            user:
              type: object
            articles:
              type: array
              items:
                type: object
            is_public:
              type: boolean
            created_at:
              type: string
              format: date-time
            updated_at:
              type: string
              format: date-time
      404:
        description: Collection not found
    """
    logger.info(f'Get collection: {collection_id}')

    # TODO: Implement actual database query
    return jsonify(
        id=collection_id,
        name='My Favorites',
        description='Collection of my favorite articles',
        user={'id': 1, 'name': 'John Doe'},
        articles=[
            {
                'id': 1,
                'title': 'Introduction to Flask',
                'slug': 'introduction-to-flask',
                'excerpt': 'Learn the basics of Flask',
            }
        ],
        is_public=True,
        created_at='2026-01-17T10:00:00Z',
        updated_at='2026-01-17T10:00:00Z',
    ), 200


@collections_bp.route('', methods=['POST'])
def create_collection():
    """
    Create a new collection
    ---
    tags:
      - Collections
    summary: Create a new collection
    description: Creates a new collection for organizing articles
    security:
      - Bearer: []
    parameters:
      - in: body
        name: body
        description: Collection data
        required: true
        schema:
          type: object
          required:
            - name
          properties:
            name:
              type: string
              example: My Favorites
            description:
              type: string
              example: Collection of my favorite articles
            is_public:
              type: boolean
              example: true
    responses:
      201:
        description: Collection created successfully
        schema:
          type: object
          properties:
            message:
              type: string
              example: Collection created successfully
            collection:
              type: object
      400:
        description: Invalid input
      401:
        description: Unauthorized
    """
    data = request.get_json()

    if not data or 'name' not in data:
        logger.warning('Create collection attempt with missing fields')
        return jsonify(error='Missing required field: name'), 400

    logger.info(f'Create collection: {data.get("name")}')

    # TODO: Implement actual database insertion
    return jsonify(
        message='Collection created successfully',
        collection={
            'id': 1,
            'name': data['name'],
            'description': data.get('description', ''),
            'is_public': data.get('is_public', False),
            'created_at': '2026-01-17T10:00:00Z',
        },
    ), 201


@collections_bp.route('/<int:collection_id>', methods=['PUT'])
def update_collection(collection_id):
    """
    Update a collection
    ---
    tags:
      - Collections
    summary: Update an existing collection
    description: Updates collection information
    security:
      - Bearer: []
    parameters:
      - in: path
        name: collection_id
        type: integer
        required: true
        description: Collection ID
      - in: body
        name: body
        description: Collection data to update
        schema:
          type: object
          properties:
            name:
              type: string
            description:
              type: string
            is_public:
              type: boolean
    responses:
      200:
        description: Collection updated successfully
        schema:
          type: object
          properties:
            message:
              type: string
              example: Collection updated successfully
            collection:
              type: object
      404:
        description: Collection not found
      401:
        description: Unauthorized
    """
    data = request.get_json()
    logger.info(f'Update collection: {collection_id}')

    # TODO: Implement actual database update
    return jsonify(
        message='Collection updated successfully',
        collection={
            'id': collection_id,
            'name': data.get('name', 'My Collection'),
            'description': data.get('description', ''),
            'is_public': data.get('is_public', False),
            'updated_at': '2026-01-17T10:00:00Z',
        },
    ), 200


@collections_bp.route('/<int:collection_id>', methods=['DELETE'])
def delete_collection(collection_id):
    """
    Delete a collection
    ---
    tags:
      - Collections
    summary: Delete a collection
    description: Deletes a collection by ID
    security:
      - Bearer: []
    parameters:
      - in: path
        name: collection_id
        type: integer
        required: true
        description: Collection ID
    responses:
      200:
        description: Collection deleted successfully
        schema:
          type: object
          properties:
            message:
              type: string
              example: Collection deleted successfully
      404:
        description: Collection not found
      401:
        description: Unauthorized
    """
    logger.info(f'Delete collection: {collection_id}')

    # TODO: Implement actual database deletion
    return jsonify(message='Collection deleted successfully'), 200


@collections_bp.route('/<int:collection_id>/articles', methods=['POST'])
def add_article_to_collection(collection_id):
    """
    Add article to collection
    ---
    tags:
      - Collections
    summary: Add an article to a collection
    description: Adds an existing article to the specified collection
    security:
      - Bearer: []
    parameters:
      - in: path
        name: collection_id
        type: integer
        required: true
        description: Collection ID
      - in: body
        name: body
        required: true
        schema:
          type: object
          required:
            - article_id
          properties:
            article_id:
              type: integer
              example: 1
    responses:
      200:
        description: Article added to collection successfully
        schema:
          type: object
          properties:
            message:
              type: string
              example: Article added to collection successfully
      400:
        description: Invalid input or article already in collection
      404:
        description: Collection or article not found
      401:
        description: Unauthorized
    """
    data = request.get_json()

    if not data or 'article_id' not in data:
        logger.warning('Add article to collection attempt with missing article_id')
        return jsonify(error='Missing required field: article_id'), 400

    article_id = data['article_id']
    logger.info(f'Add article {article_id} to collection {collection_id}')

    # TODO: Implement actual database insertion
    return jsonify(message='Article added to collection successfully'), 200


@collections_bp.route('/<int:collection_id>/articles/<int:article_id>', methods=['DELETE'])
def remove_article_from_collection(collection_id, article_id):
    """
    Remove article from collection
    ---
    tags:
      - Collections
    summary: Remove an article from a collection
    description: Removes an article from the specified collection
    security:
      - Bearer: []
    parameters:
      - in: path
        name: collection_id
        type: integer
        required: true
        description: Collection ID
      - in: path
        name: article_id
        type: integer
        required: true
        description: Article ID
    responses:
      200:
        description: Article removed from collection successfully
        schema:
          type: object
          properties:
            message:
              type: string
              example: Article removed from collection successfully
      404:
        description: Collection or article not found
      401:
        description: Unauthorized
    """
    logger.info(f'Remove article {article_id} from collection {collection_id}')

    # TODO: Implement actual database deletion
    return jsonify(message='Article removed from collection successfully'), 200
