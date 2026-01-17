from flask import Blueprint, jsonify, request, send_file

from app.utils.file_manager import file_manager
from app.utils.logger import get_logger

logger = get_logger(__name__)
files_bp = Blueprint('files', __name__, url_prefix='/api/files')


@files_bp.route('', methods=['GET'])
def list_files():
    """
    List all files
    ---
    tags:
      - Files
    summary: List all uploaded files
    description: Returns a list of all uploaded files
    parameters:
      - in: query
        name: page
        type: integer
        default: 1
        description: Page number
      - in: query
        name: limit
        type: integer
        default: 20
        description: Number of items per page
    responses:
      200:
        description: List of files
        schema:
          type: object
          properties:
            files:
              type: array
              items:
                type: object
                properties:
                  id:
                    type: string
                    example: file123
                  filename:
                    type: string
                    example: document.pdf
                  size:
                    type: integer
                    example: 1024000
                  extension:
                    type: string
                    example: pdf
                  url:
                    type: string
                    example: /api/files/file123/download
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
    limit = request.args.get('limit', 20, type=int)
    search = request.args.get('search', type=str)

    logger.info(f'List files: page={page}, limit={limit}, search={search}')

    result = file_manager.list_files(page=page, limit=limit, search=search)
    return jsonify(result), 200


@files_bp.route('/upload', methods=['POST'])
def upload_file():
    """
    Upload a file
    ---
    tags:
      - Files
    summary: Upload a new file
    description: Upload a file to the server
    security:
      - Bearer: []
    consumes:
      - multipart/form-data
    parameters:
      - in: formData
        name: file
        type: file
        required: true
        description: The file to upload
      - in: formData
        name: description
        type: string
        description: Optional file description
    responses:
      201:
        description: File uploaded successfully
        schema:
          type: object
          properties:
            message:
              type: string
              example: File uploaded successfully
            file:
              type: object
              properties:
                id:
                  type: string
                filename:
                  type: string
                size:
                  type: integer
                url:
                  type: string
      400:
        description: Invalid file or no file provided
      413:
        description: File too large
      401:
        description: Unauthorized
    """
    if 'file' not in request.files:
        logger.warning('Upload attempt without file')
        return jsonify(error='No file part in request'), 400

    file = request.files['file']
    custom_filename = request.form.get('filename')  # Optional custom filename

    success, message, file_info = file_manager.save_file(file, custom_filename)

    if not success:
        return jsonify(error=message), 400

    return jsonify(message=message, file=file_info), 201


@files_bp.route('/<filename>', methods=['GET'])
def get_file_details(filename):
    """
    Get file details
    ---
    tags:
      - Files
    summary: Get file information
    description: Returns detailed information about a specific file
    parameters:
      - in: path
        name: filename
        type: string
        required: true
        description: Name of the file
    responses:
      200:
        description: File details
        schema:
          type: object
          properties:
            id:
              type: string
            filename:
              type: string
            size:
              type: integer
            extension:
              type: string
            url:
              type: string
            created_at:
              type: string
              format: date-time
            modified_at:
              type: string
              format: date-time
      404:
        description: File not found
    """
    file_info = file_manager.get_file_info(filename)

    if not file_info:
        logger.warning(f'File not found: {filename}')
        return jsonify(error='File not found'), 404

    file_info['id'] = filename
    logger.info(f'Get file details: {filename}')
    return jsonify(file_info), 200


@files_bp.route('/<filename>/download', methods=['GET'])
def download_file(filename):
    """
    Download a file
    ---
    tags:
      - Files
    summary: Download a file
    description: Download a specific file
    parameters:
      - in: path
        name: filename
        type: string
        required: true
        description: Name of the file to download
    produces:
      - application/octet-stream
    responses:
      200:
        description: File content
        schema:
          type: file
      404:
        description: File not found
    """
    filepath = file_manager.get_filepath(filename)

    if not filepath:
        logger.warning(f'Download attempt for non-existent file: {filename}')
        return jsonify(error='File not found'), 404

    try:
        logger.info(f'File downloaded: {filename}')
        return send_file(filepath, as_attachment=True, download_name=filename)
    except Exception as e:
        logger.error(f'Error downloading file: {e!s}')
        return jsonify(error='Failed to download file'), 500


@files_bp.route('/<filename>', methods=['DELETE'])
def delete_file(filename):
    """
    Delete a file
    ---
    tags:
      - Files
    summary: Delete a file
    description: Delete a specific file from the server
    security:
      - Bearer: []
    parameters:
      - in: path
        name: filename
        type: string
        required: true
        description: Name of the file to delete
    responses:
      200:
        description: File deleted successfully
        schema:
          type: object
          properties:
            message:
              type: string
              example: File deleted successfully
      404:
        description: File not found
      401:
        description: Unauthorized
    """
    success, message = file_manager.delete_file(filename)

    if not success:
        status_code = 404 if 'not found' in message.lower() else 500
        return jsonify(error=message), status_code

    return jsonify(message=message), 200
