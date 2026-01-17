"""
Collection model for organizing articles into user-created collections.
"""

from datetime import datetime

from bson import ObjectId

from app.core.base_model import BaseModel
from app.utils.logger import get_logger

logger = get_logger(__name__)


class Collection(BaseModel):
    """
    Collection model for user-created article collections.

    Collection: collections
    Indexes: user_id, is_public, created_at
    """

    collection_name = 'collections'

    @classmethod
    def find_by_user(cls, user_id: str, skip: int = 0, limit: int = 10, session=None) -> list[dict]:
        """
        Find collections by user.

        Args:
            user_id: User ID
            skip: Number of documents to skip (pagination)
            limit: Maximum number of documents to return
            session: Optional MongoDB session for transactions

        Returns:
            List of collection documents
        """
        return cls.find_many({'user_id': user_id}, skip=skip, limit=limit, sort=[('created_at', -1)], session=session)

    @classmethod
    def add_article(cls, collection_id: str, article_id: str, session=None) -> bool:
        """
        Add article to collection.

        Args:
            collection_id: Collection ID
            article_id: Article ID to add
            session: Optional MongoDB session for transactions

        Returns:
            True if article was added, False otherwise
        """
        try:
            collection = cls.get_collection()
            result = collection.update_one(
                {'_id': ObjectId(collection_id)},
                {'$addToSet': {'article_ids': article_id}, '$set': {'updated_at': datetime.utcnow()}},
                session=session,
            )
            return result.modified_count > 0
        except Exception as e:
            logger.error(f'Error adding article to collection: {e!s}')
            return False

    @classmethod
    def remove_article(cls, collection_id: str, article_id: str, session=None) -> bool:
        """
        Remove article from collection.

        Args:
            collection_id: Collection ID
            article_id: Article ID to remove
            session: Optional MongoDB session for transactions

        Returns:
            True if article was removed, False otherwise
        """
        try:
            collection = cls.get_collection()
            result = collection.update_one(
                {'_id': ObjectId(collection_id)},
                {'$pull': {'article_ids': article_id}, '$set': {'updated_at': datetime.utcnow()}},
                session=session,
            )
            return result.modified_count > 0
        except Exception as e:
            logger.error(f'Error removing article from collection: {e!s}')
            return False
