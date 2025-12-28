"""MongoDB client utility."""

from pymongo import MongoClient
from pymongo.database import Database
from typing import Optional
import logging
import sys
from pathlib import Path

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from literature_review.config import config

logger = logging.getLogger(__name__)

class MongoDBClient:
    """MongoDB client wrapper."""
    
    _instance: Optional['MongoDBClient'] = None
    _client: Optional[MongoClient] = None
    _db: Optional[Database] = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance
    
    def connect(self):
        """Connect to MongoDB."""
        if self._client is None:
            logger.info(f"Connecting to MongoDB: {config.MONGODB_URI}")
            self._client = MongoClient(config.MONGODB_URI, serverSelectionTimeoutMS=5000)
            self._db = self._client[config.MONGODB_DATABASE]
            # Test connection
            self._client.server_info()
            logger.info(f"Connected to database: {config.MONGODB_DATABASE}")
    
    @property
    def db(self) -> Database:
        """Get database instance."""
        if self._db is None:
            self.connect()
        assert self._db is not None
        return self._db
    
    @property
    def documents(self):
        """Get documents collection."""
        return self.db[config.MONGODB_COLLECTIONS["documents"]]
    
    @property
    def chunks(self):
        """Get chunks collection."""
        return self.db[config.MONGODB_COLLECTIONS["chunks"]]
    
    @property
    def facts(self):
        """Get facts collection."""
        return self.db[config.MONGODB_COLLECTIONS["facts"]]
    
    @property
    def assessments(self):
        """Get assessments collection."""
        return self.db[config.MONGODB_COLLECTIONS["assessments"]]
    
    @property
    def checkpoints(self):
        """Get checkpoints collection."""
        return self.db[config.MONGODB_COLLECTIONS["checkpoints"]]
    
    def close(self):
        """Close MongoDB connection."""
        if self._client:
            self._client.close()
            logger.info("MongoDB connection closed")
    
    def setup_indexes(self):
        """Create necessary indexes."""
        logger.info("Setting up indexes...")
        
        # Document indexes
        self.documents.create_index("doc_id", unique=True)
        self.documents.create_index("filename")
        
        # Chunk indexes
        self.chunks.create_index([("doc_id", 1), ("chunk_id", 1)])
        
        # Fact indexes
        self.facts.create_index("fact_number", unique=True)
        
        # Assessment indexes
        self.assessments.create_index("fact_number", unique=True)
        
        logger.info("Indexes created successfully")

# Global instance
mongodb = MongoDBClient()
