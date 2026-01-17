"""
Article model for blog posts and content management.
"""

from typing import Optional, Dict, List
from app.lib.base_model import BaseModel


class Article(BaseModel):
    """
    Article model for managing blog posts and content.
    
    Collection: articles
    Indexes: slug (unique), category_id, author_id, published, created_at, text search on title and content
    """
    
    collection_name = 'articles'
    
    @classmethod
    def find_by_slug(cls, slug: str, session=None) -> Optional[Dict]:
        """
        Find article by slug.
        
        Args:
            slug: Article slug (URL-friendly identifier)
            session: Optional MongoDB session for transactions
            
        Returns:
            Article document or None if not found
        """
        return cls.find_one({'slug': slug}, session=session)
    
    @classmethod
    def find_by_category(cls, category_id: str, skip: int = 0, limit: int = 10, session=None) -> List[Dict]:
        """
        Find articles by category.
        
        Args:
            category_id: Category ID
            skip: Number of documents to skip (pagination)
            limit: Maximum number of documents to return
            session: Optional MongoDB session for transactions
            
        Returns:
            List of article documents
        """
        return cls.find_many(
            {'category_id': category_id},
            skip=skip,
            limit=limit,
            sort=[('created_at', -1)],
            session=session
        )
    
    @classmethod
    def search(cls, search_term: str, skip: int = 0, limit: int = 10, session=None) -> List[Dict]:
        """
        Search articles by title or content using MongoDB text search.
        
        Args:
            search_term: Search query string
            skip: Number of documents to skip (pagination)
            limit: Maximum number of documents to return
            session: Optional MongoDB session for transactions
            
        Returns:
            List of matching article documents
        """
        return cls.find_many(
            {'$text': {'$search': search_term}},
            skip=skip,
            limit=limit,
            sort=[('created_at', -1)],
            session=session
        )
