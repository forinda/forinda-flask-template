from flask import Blueprint, jsonify

from app.utils.logger import get_logger

logger = get_logger(__name__)
health_bp = Blueprint('health', __name__, url_prefix='/api')


@health_bp.route('/health', methods=['GET'])
def health_check():
    """
    Health Check Endpoint
    ---
    tags:
      - Health
    summary: Check API health status
    description: Returns the health status of the API
    responses:
      200:
        description: API is healthy
        schema:
          type: object
          properties:
            status:
              type: string
              example: healthy
            service:
              type: string
              example: flask-app
    """
    logger.info('Health check endpoint called')
    return jsonify(status='healthy', service='flask-app'), 200
