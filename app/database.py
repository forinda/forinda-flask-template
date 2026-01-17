"""
MongoDB database configuration and connection management.
"""

from contextlib import contextmanager

from pymongo import MongoClient
from pymongo.errors import ConnectionFailure, ServerSelectionTimeoutError

from app.settings import settings
from app.utils.logger import get_logger

logger = get_logger(__name__)


class MongoDB:
    """MongoDB connection manager."""

    _client = None
    _db = None

    @classmethod
    def connect(cls):
        """
        Establish connection to MongoDB.

        Returns:
            Database instance
        """
        if cls._client is None:
            try:
                logger.info(f'Connecting to MongoDB: {settings.MONGODB_URI}')
                cls._client = MongoClient(settings.MONGODB_URI, serverSelectionTimeoutMS=settings.MONGODB_TIMEOUT)

                # Test connection
                cls._client.admin.command('ping')
                cls._db = cls._client[settings.MONGODB_DB_NAME]

                logger.info('Successfully connected to MongoDB')

            except (ConnectionFailure, ServerSelectionTimeoutError) as e:
                logger.error(f'Failed to connect to MongoDB: {e!s}')
                raise

        return cls._db

    @classmethod
    def get_db(cls):
        """
        Get database instance.

        Returns:
            Database instance
        """
        if cls._db is None:
            return cls.connect()
        return cls._db

    @classmethod
    def close(cls):
        """Close MongoDB connection."""
        if cls._client:
            cls._client.close()
            cls._client = None
            cls._db = None
            logger.info('MongoDB connection closed')

    @classmethod
    def get_collection(cls, collection_name: str):
        """
        Get a collection from the database.

        Args:
            collection_name: Name of the collection

        Returns:
            Collection instance
        """
        db = cls.get_db()
        return db[collection_name]

    @classmethod
    def get_client(cls):
        """
        Get MongoDB client instance.

        Returns:
            MongoClient instance
        """
        if cls._client is None:
            cls.connect()
        return cls._client

    @classmethod
    @contextmanager
    def transaction(cls):
        """
        Context manager for MongoDB transactions.

        Usage:
            with MongoDB.transaction() as session:
                collection.insert_one({'name': 'test'}, session=session)
                collection.update_one({'_id': id}, {'$set': {'status': 'active'}}, session=session)

        Yields:
            ClientSession: MongoDB session object

        Note:
            Transactions require MongoDB 4.0+ with replica set or MongoDB 4.2+ with sharded cluster.
            For standalone MongoDB, transactions are not supported.
        """
        client = cls.get_client()
        session = None

        try:
            session = client.start_session()
            session.start_transaction()

            logger.debug('Transaction started')

            yield session

            # Commit transaction if no exception occurred
            session.commit_transaction()
            logger.debug('Transaction committed successfully')

        except Exception as e:
            # Rollback transaction on error
            if session and session.in_transaction:
                session.abort_transaction()
                logger.error(f'Transaction aborted due to error: {e!s}')
            raise

        finally:
            if session:
                session.end_session()
                logger.debug('Transaction session ended')

    @classmethod
    def start_session(cls):
        """
        Start a new MongoDB session (for manual transaction management).

        Returns:
            ClientSession: MongoDB session object

        Usage:
            session = MongoDB.start_session()
            session.start_transaction()
            try:
                collection.insert_one({'name': 'test'}, session=session)
                session.commit_transaction()
            except Exception:
                session.abort_transaction()
            finally:
                session.end_session()
        """
        client = cls.get_client()
        return client.start_session()


# Convenience function
def get_db():
    """Get database instance."""
    return MongoDB.get_db()


def init_db():
    """Initialize database and create indexes."""
    try:
        db = MongoDB.get_db()

        # Create indexes for better performance
        logger.info('Creating database indexes...')

        # Users collection
        db.users.create_index('email', unique=True)
        db.users.create_index('created_at')

        # Articles collection
        db.articles.create_index('slug', unique=True)
        db.articles.create_index('category_id')
        db.articles.create_index('author_id')
        db.articles.create_index('published')
        db.articles.create_index('created_at')
        db.articles.create_index([('title', 'text'), ('content', 'text')])

        # Categories collection
        db.categories.create_index('slug', unique=True)
        db.categories.create_index('name')

        # Collections
        db.collections.create_index('user_id')
        db.collections.create_index('is_public')
        db.collections.create_index('created_at')

        # Files collection
        db.files.create_index('filename', unique=True)
        db.files.create_index('created_at')

        logger.info('Database indexes created successfully')

    except Exception as e:
        logger.error(f'Error initializing database: {e!s}')
        raise
