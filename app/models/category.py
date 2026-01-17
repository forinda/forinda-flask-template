"""
Category model for organizing articles and content.
"""

from typing import Optional, Dict
from app.lib.base_model import BaseModel


class Category(BaseModel):
    """
    Category model for organizing and classifying content.
    
    Collection: categories
    Indexes: slug (unique), name
    """
    
    collection_name = 'categories'
    
    @classmethod
    def find_by_slug(cls, slug: str, session=None) -> Optional[Dict]:
        """
        Find category by slug.
        
        Args:
            slug: Category slug (URL-friendly identifier)
            session: Optional MongoDB session for transactions
            
        Returns:
            Category document or None if not found
        """
        return cls.find_one({'slug': slug}, session=session)
