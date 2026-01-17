from flask import Blueprint, jsonify
from app.utils.logger import get_logger
from app.utils.file_manager import file_manager

logger = get_logger(__name__)
storage_bp = Blueprint('storage', __name__, url_prefix='/api/storage')


@storage_bp.route('/info', methods=['GET'])
def get_storage_info():
    """
    Get storage information
    ---
    tags:
      - Files
    summary: Get storage statistics
    description: Returns information about file storage usage
    responses:
      200:
        description: Storage information
        schema:
          type: object
          properties:
            total_files:
              type: integer
              example: 42
            total_size:
              type: integer
              example: 10485760
            total_size_human:
              type: string
              example: 10.00 MB
            upload_folder:
              type: string
              example: uploads
    """
    logger.info('Get storage info')
    storage_info = file_manager.get_storage_info()
    return jsonify(storage_info), 200
