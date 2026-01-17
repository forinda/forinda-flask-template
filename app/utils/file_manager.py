"""
File management utility module.
Handles file upload, validation, storage, and retrieval.
"""

import os
import shutil
from datetime import datetime

from werkzeug.datastructures import FileStorage
from werkzeug.utils import secure_filename

from app.utils.logger import get_logger

logger = get_logger(__name__)


class FileManager:
    """Manages file operations including upload, download, and deletion."""

    def __init__(self, upload_folder: str = 'uploads', max_size: int = 16 * 1024 * 1024):
        """
        Initialize FileManager.

        Args:
            upload_folder: Directory where files will be stored
            max_size: Maximum file size in bytes (default: 16MB)
        """
        self.upload_folder = upload_folder
        self.max_size = max_size
        self.allowed_extensions = {
            'txt',
            'pdf',
            'png',
            'jpg',
            'jpeg',
            'gif',
            'svg',
            'webp',
            'doc',
            'docx',
            'xls',
            'xlsx',
            'ppt',
            'pptx',
            'zip',
            'tar',
            'gz',
            '7z',
            'mp3',
            'mp4',
            'avi',
            'mov',
            'wav',
            'csv',
            'json',
            'xml',
            'yaml',
            'yml',
        }

        # Ensure upload folder exists
        self._ensure_upload_folder()

    def _ensure_upload_folder(self):
        """Create upload folder if it doesn't exist."""
        if not os.path.exists(self.upload_folder):
            os.makedirs(self.upload_folder)
            logger.info(f'Created upload folder: {self.upload_folder}')

    def allowed_file(self, filename: str) -> bool:
        """
        Check if file extension is allowed.

        Args:
            filename: Name of the file

        Returns:
            True if file extension is allowed, False otherwise
        """
        return '.' in filename and filename.rsplit('.', 1)[1].lower() in self.allowed_extensions

    def get_file_extension(self, filename: str) -> str | None:
        """
        Get file extension.

        Args:
            filename: Name of the file

        Returns:
            File extension or None
        """
        return filename.rsplit('.', 1)[1].lower() if '.' in filename else None

    def get_unique_filename(self, filename: str) -> str:
        """
        Generate a unique filename if file already exists.

        Args:
            filename: Original filename

        Returns:
            Unique filename
        """
        base_name, extension = os.path.splitext(filename)
        counter = 1
        unique_filename = filename

        while os.path.exists(os.path.join(self.upload_folder, unique_filename)):
            unique_filename = f'{base_name}_{counter}{extension}'
            counter += 1

        return unique_filename

    def get_file_size(self, filename: str) -> int | None:
        """
        Get file size in bytes.

        Args:
            filename: Name of the file

        Returns:
            File size in bytes or None if file doesn't exist
        """
        filepath = os.path.join(self.upload_folder, filename)
        if os.path.exists(filepath):
            return os.path.getsize(filepath)
        return None

    def get_file_info(self, filename: str) -> dict | None:
        """
        Get detailed file information.

        Args:
            filename: Name of the file

        Returns:
            Dictionary with file information or None if file doesn't exist
        """
        filepath = os.path.join(self.upload_folder, filename)

        if not os.path.exists(filepath):
            return None

        try:
            stats = os.stat(filepath)
            return {
                'filename': filename,
                'size': stats.st_size,
                'size_human': self._human_readable_size(stats.st_size),
                'extension': self.get_file_extension(filename),
                'created_at': datetime.fromtimestamp(stats.st_ctime).isoformat(),
                'modified_at': datetime.fromtimestamp(stats.st_mtime).isoformat(),
                'path': filepath,
                'url': f'/api/files/{filename}/download',
            }
        except Exception as e:
            logger.error(f'Error getting file info for {filename}: {e!s}')
            return None

    def _human_readable_size(self, size: int) -> str:
        """
        Convert bytes to human-readable format.

        Args:
            size: Size in bytes

        Returns:
            Human-readable size string
        """
        for unit in ['B', 'KB', 'MB', 'GB', 'TB']:
            if size < 1024.0:
                return f'{size:.2f} {unit}'
            size /= 1024.0
        return f'{size:.2f} PB'

    def validate_file(self, file: FileStorage) -> tuple[bool, str | None]:
        """
        Validate uploaded file.

        Args:
            file: FileStorage object from request

        Returns:
            Tuple of (is_valid, error_message)
        """
        # Check if file exists
        if not file or file.filename == '':
            return False, 'No file selected'

        # Check file extension
        if not self.allowed_file(file.filename):
            return False, f'File type not allowed. Allowed types: {", ".join(self.allowed_extensions)}'

        # Check file size (if possible)
        file.seek(0, os.SEEK_END)
        file_size = file.tell()
        file.seek(0)  # Reset file pointer

        if file_size > self.max_size:
            max_mb = self.max_size / (1024 * 1024)
            return False, f'File too large. Maximum size: {max_mb:.2f} MB'

        return True, None

    def save_file(self, file: FileStorage, custom_filename: str | None = None) -> tuple[bool, str, dict | None]:
        """
        Save uploaded file.

        Args:
            file: FileStorage object from request
            custom_filename: Optional custom filename to use

        Returns:
            Tuple of (success, message, file_info_dict)
        """
        try:
            # Validate file
            is_valid, error_msg = self.validate_file(file)
            if not is_valid:
                logger.warning(f'File validation failed: {error_msg}')
                return False, error_msg, None

            # Get secure filename
            if custom_filename:
                filename = secure_filename(custom_filename)
            else:
                filename = secure_filename(file.filename)

            # Ensure extension is preserved
            original_ext = self.get_file_extension(file.filename)
            if original_ext and not filename.endswith(f'.{original_ext}'):
                filename = f'{filename}.{original_ext}'

            # Get unique filename
            filename = self.get_unique_filename(filename)

            # Save file
            filepath = os.path.join(self.upload_folder, filename)
            file.save(filepath)

            logger.info(f'File saved successfully: {filename}')

            # Get file info
            file_info = self.get_file_info(filename)

            return True, 'File uploaded successfully', file_info

        except Exception as e:
            error_msg = f'Failed to save file: {e!s}'
            logger.error(error_msg)
            return False, error_msg, None

    def delete_file(self, filename: str) -> tuple[bool, str]:
        """
        Delete a file.

        Args:
            filename: Name of the file to delete

        Returns:
            Tuple of (success, message)
        """
        filepath = os.path.join(self.upload_folder, filename)

        if not os.path.exists(filepath):
            return False, 'File not found'

        try:
            os.remove(filepath)
            logger.info(f'File deleted: {filename}')
            return True, 'File deleted successfully'
        except Exception as e:
            error_msg = f'Failed to delete file: {e!s}'
            logger.error(error_msg)
            return False, error_msg

    def list_files(self, page: int = 1, limit: int = 20, search: str | None = None) -> dict:
        """
        List all files with pagination.

        Args:
            page: Page number (1-indexed)
            limit: Number of items per page
            search: Optional search term to filter filenames

        Returns:
            Dictionary with files list and pagination info
        """
        try:
            all_files = []

            if os.path.exists(self.upload_folder):
                for filename in os.listdir(self.upload_folder):
                    filepath = os.path.join(self.upload_folder, filename)

                    # Skip directories and hidden files
                    if not os.path.isfile(filepath) or filename.startswith('.'):
                        continue

                    # Apply search filter
                    if search and search.lower() not in filename.lower():
                        continue

                    file_info = self.get_file_info(filename)
                    if file_info:
                        file_info['id'] = filename
                        all_files.append(file_info)

            # Sort by modified date (newest first)
            all_files.sort(key=lambda x: x['modified_at'], reverse=True)

            # Pagination
            total = len(all_files)
            start = (page - 1) * limit
            end = start + limit
            paginated_files = all_files[start:end]

            return {
                'files': paginated_files,
                'total': total,
                'page': page,
                'limit': limit,
                'total_pages': (total + limit - 1) // limit if total > 0 else 0,
            }

        except Exception as e:
            logger.error(f'Error listing files: {e!s}')
            return {'files': [], 'total': 0, 'page': page, 'limit': limit, 'total_pages': 0}

    def file_exists(self, filename: str) -> bool:
        """
        Check if file exists.

        Args:
            filename: Name of the file

        Returns:
            True if file exists, False otherwise
        """
        filepath = os.path.join(self.upload_folder, filename)
        return os.path.exists(filepath) and os.path.isfile(filepath)

    def get_filepath(self, filename: str) -> str | None:
        """
        Get full path to file.

        Args:
            filename: Name of the file

        Returns:
            Full filepath or None if file doesn't exist
        """
        filepath = os.path.join(self.upload_folder, filename)
        return filepath if self.file_exists(filename) else None

    def move_file(self, filename: str, new_folder: str) -> tuple[bool, str]:
        """
        Move file to a different folder.

        Args:
            filename: Name of the file
            new_folder: Destination folder

        Returns:
            Tuple of (success, message)
        """
        source = os.path.join(self.upload_folder, filename)

        if not os.path.exists(source):
            return False, 'File not found'

        try:
            # Create destination folder if needed
            if not os.path.exists(new_folder):
                os.makedirs(new_folder)

            destination = os.path.join(new_folder, filename)
            shutil.move(source, destination)

            logger.info(f'File moved: {filename} -> {new_folder}')
            return True, f'File moved to {new_folder}'
        except Exception as e:
            error_msg = f'Failed to move file: {e!s}'
            logger.error(error_msg)
            return False, error_msg

    def get_storage_info(self) -> dict:
        """
        Get storage information.

        Returns:
            Dictionary with storage statistics
        """
        try:
            total_size = 0
            file_count = 0

            if os.path.exists(self.upload_folder):
                for filename in os.listdir(self.upload_folder):
                    filepath = os.path.join(self.upload_folder, filename)
                    if os.path.isfile(filepath):
                        total_size += os.path.getsize(filepath)
                        file_count += 1

            return {
                'total_files': file_count,
                'total_size': total_size,
                'total_size_human': self._human_readable_size(total_size),
                'upload_folder': self.upload_folder,
            }
        except Exception as e:
            logger.error(f'Error getting storage info: {e!s}')
            return {'total_files': 0, 'total_size': 0, 'total_size_human': '0 B', 'upload_folder': self.upload_folder}


# Global file manager instance
file_manager = FileManager()
