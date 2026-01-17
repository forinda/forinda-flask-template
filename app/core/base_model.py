"""
Base model with common database operations.
"""

from typing import Dict, Optional, List
from datetime import datetime
from bson import ObjectId
from app.database import get_db
from app.utils.logger import get_logger

logger = get_logger(__name__)


class BaseModel:
    """Base model with common CRUD operations for MongoDB collections."""
    
    collection_name = None
    
    @classmethod
    def get_collection(cls):
        """
        Get the MongoDB collection for this model.
        
        Returns:
            Collection: MongoDB collection instance
        """
        db = get_db()
        return db[cls.collection_name]
    
    @classmethod
    def find_one(cls, query: Dict, session=None) -> Optional[Dict]:
        """
        Find a single document.
        
        Args:
            query: MongoDB query filter
            session: Optional MongoDB session for transactions
            
        Returns:
            Document dictionary or None if not found
        """
        try:
            collection = cls.get_collection()
            doc = collection.find_one(query, session=session)
            if doc and '_id' in doc:
                doc['id'] = str(doc['_id'])
            return doc
        except Exception as e:
            logger.error(f'Error finding document in {cls.collection_name}: {str(e)}')
            return None
    
    @classmethod
    def find_many(cls, query: Dict = None, skip: int = 0, limit: int = 10, sort: List = None, session=None) -> List[Dict]:
        """
        Find multiple documents.
        
        Args:
            query: MongoDB query filter
            skip: Number of documents to skip
            limit: Maximum number of documents to return
            sort: Sort specification
            session: Optional MongoDB session for transactions
            
        Returns:
            List of document dictionaries
        """
        try:
            collection = cls.get_collection()
            query = query or {}
            cursor = collection.find(query, session=session).skip(skip).limit(limit)
            
            if sort:
                cursor = cursor.sort(sort)
            
            docs = []
            for doc in cursor:
                if '_id' in doc:
                    doc['id'] = str(doc['_id'])
                docs.append(doc)
            
            return docs
        except Exception as e:
            logger.error(f'Error finding documents in {cls.collection_name}: {str(e)}')
            return []
    
    @classmethod
    def count(cls, query: Dict = None, session=None) -> int:
        """
        Count documents matching the query.
        
        Args:
            query: MongoDB query filter
            session: Optional MongoDB session for transactions
            
        Returns:
            Number of matching documents
        """
        try:
            collection = cls.get_collection()
            return collection.count_documents(query or {}, session=session)
        except Exception as e:
            logger.error(f'Error counting documents in {cls.collection_name}: {str(e)}')
            return 0
    
    @classmethod
    def insert_one(cls, document: Dict, session=None) -> Optional[str]:
        """
        Insert a single document.
        
        Args:
            document: Document data to insert
            session: Optional MongoDB session for transactions
            
        Returns:
            Inserted document ID as string or None on error
        """
        try:
            collection = cls.get_collection()
            document['created_at'] = datetime.utcnow()
            document['updated_at'] = datetime.utcnow()
            result = collection.insert_one(document, session=session)
            return str(result.inserted_id)
        except Exception as e:
            logger.error(f'Error inserting document in {cls.collection_name}: {str(e)}')
            return None
    
    @classmethod
    def update_one(cls, query: Dict, update: Dict, session=None) -> bool:
        """
        Update a single document.
        
        Args:
            query: MongoDB query filter
            update: Update operations
            session: Optional MongoDB session for transactions
            
        Returns:
            True if document was modified, False otherwise
        """
        try:
            collection = cls.get_collection()
            update['$set'] = update.get('$set', {})
            update['$set']['updated_at'] = datetime.utcnow()
            result = collection.update_one(query, update, session=session)
            return result.modified_count > 0
        except Exception as e:
            logger.error(f'Error updating document in {cls.collection_name}: {str(e)}')
            return False
    
    @classmethod
    def delete_one(cls, query: Dict, session=None) -> bool:
        """
        Delete a single document.
        
        Args:
            query: MongoDB query filter
            session: Optional MongoDB session for transactions
            
        Returns:
            True if document was deleted, False otherwise
        """
        try:
            collection = cls.get_collection()
            result = collection.delete_one(query, session=session)
            return result.deleted_count > 0
        except Exception as e:
            logger.error(f'Error deleting document in {cls.collection_name}: {str(e)}')
            return False
    
    @classmethod
    def find_by_id(cls, doc_id: str, session=None) -> Optional[Dict]:
        """
        Find document by ID.
        
        Args:
            doc_id: Document ID as string
            session: Optional MongoDB session for transactions
            
        Returns:
            Document dictionary or None if not found
        """
        try:
            return cls.find_one({'_id': ObjectId(doc_id)}, session=session)
        except Exception as e:
            logger.error(f'Error finding document by ID in {cls.collection_name}: {str(e)}')
            return None
