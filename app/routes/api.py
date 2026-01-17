from flask import Blueprint, jsonify, request
from flasgger import swag_from
from app.utils.logger import get_logger

logger = get_logger(__name__)
api_bp = Blueprint('api', __name__, url_prefix='/api/v1')


@api_bp.route('/example', methods=['GET'])
def example():
    """
    Example Endpoint
    ---
    tags:
      - API
    summary: Example API endpoint
    description: Returns a simple example message
    responses:
      200:
        description: Success
        schema:
          type: object
          properties:
            message:
              type: string
              example: This is an example endpoint
    """
    logger.info('Example endpoint called')
    return jsonify(message='This is an example endpoint'), 200


@api_bp.route('/data', methods=['POST'])
def create_data():
    """
    Create Data
    ---
    tags:
      - API
    summary: Create new data
    description: Accepts JSON data and returns it back
    parameters:
      - in: body
        name: body
        description: Data to create
        required: true
        schema:
          type: object
          properties:
            name:
              type: string
              example: John Doe
            email:
              type: string
              example: john@example.com
    responses:
      201:
        description: Data created successfully
        schema:
          type: object
          properties:
            message:
              type: string
              example: Data received
            data:
              type: object
      400:
        description: Invalid input
    """
    data = request.get_json()
    logger.info(f'Data received: {data}')
    return jsonify(message='Data received', data=data), 201
