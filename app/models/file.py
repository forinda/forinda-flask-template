"""
File model for managing uploaded files and file metadata.
"""

from app.core.base_model import BaseModel


class File(BaseModel):
    """
    File model for managing file uploads and metadata.

    Collection: files
    Indexes: filename (unique), created_at
    """

    collection_name = 'files'

    @classmethod
    def find_by_filename(cls, filename: str, session=None) -> dict | None:
        """
        Find file by filename.

        Args:
            filename: Name of the file
            session: Optional MongoDB session for transactions

        Returns:
            File document or None if not found
        """
        return cls.find_one({'filename': filename}, session=session)
