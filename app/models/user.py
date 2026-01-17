"""
User model for authentication and user management.
"""

from app.core.base_model import BaseModel


class User(BaseModel):
    """
    User model for managing user accounts.

    Collection: users
    Indexes: email (unique), created_at
    """

    collection_name = 'users'

    @classmethod
    def find_by_email(cls, email: str, session=None) -> dict | None:
        """
        Find user by email address.

        Args:
            email: User's email address
            session: Optional MongoDB session for transactions

        Returns:
            User document or None if not found
        """
        return cls.find_one({'email': email}, session=session)
