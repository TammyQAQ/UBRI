"""
MongoDB configuration and connection utilities.
"""
from typing import Optional
from pymongo import MongoClient
from pymongo.database import Database
from pymongo.collection import Collection
import logging

from .settings import settings

logger = logging.getLogger(__name__)


class MongoDBManager:
    """Manages MongoDB connections and provides database access."""
    
    def __init__(self):
        self.client: Optional[MongoClient] = None
        self.database: Optional[Database] = None
        self._connect()
    
    def _connect(self) -> None:
        """Establish connection to MongoDB."""
        try:
            self.client = MongoClient(
                settings.MONGODB_URI,
                serverSelectionTimeoutMS=5000,
                maxPoolSize=10,
                minPoolSize=1
            )
            
            # Test connection
            self.client.admin.command('ping')
            self.database = self.client[settings.MONGODB_DATABASE]
            
            logger.info(f"Successfully connected to MongoDB: {settings.MONGODB_URI}")
            
        except Exception as e:
            logger.error(f"Failed to connect to MongoDB: {e}")
            raise
    
    def get_collection(self, collection_name: str) -> Collection:
        """Get a MongoDB collection by name."""
        if not self.database:
            raise RuntimeError("Database not connected")
        return self.database[collection_name]
    
    def get_papers_collection(self) -> Collection:
        """Get the papers collection."""
        return self.get_collection(settings.MONGODB_PAPERS_COLLECTION)
    
    def get_chunks_collection(self) -> Collection:
        """Get the chunks collection."""
        return self.get_collection(settings.MONGODB_CHUNKS_COLLECTION)
    
    def get_status_collection(self) -> Collection:
        """Get the processing status collection."""
        return self.get_collection(settings.MONGODB_STATUS_COLLECTION)
    
    def create_indexes(self) -> None:
        """Create necessary indexes for optimal performance."""
        try:
            # Papers collection indexes
            papers_collection = self.get_papers_collection()
            papers_collection.create_index("title")
            papers_collection.create_index("authors")
            papers_collection.create_index("year")
            papers_collection.create_index("doi")
            
            # Chunks collection indexes
            chunks_collection = self.get_chunks_collection()
            chunks_collection.create_index("paper_id")
            chunks_collection.create_index("chunk_index")
            chunks_collection.create_index("section")
            
            # Status collection indexes
            status_collection = self.get_status_collection()
            status_collection.create_index("paper_id", unique=True)
            status_collection.create_index("status")
            status_collection.create_index("last_updated")
            
            logger.info("Successfully created MongoDB indexes")
            
        except Exception as e:
            logger.error(f"Failed to create indexes: {e}")
            raise
    
    def close(self) -> None:
        """Close the MongoDB connection."""
        if self.client:
            self.client.close()
            logger.info("MongoDB connection closed")


# Global MongoDB manager instance
mongodb_manager = MongoDBManager() 