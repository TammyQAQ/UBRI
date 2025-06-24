"""
Main configuration settings for UBRI data preprocessing project.
"""
import os
from pathlib import Path
from typing import Optional
from pydantic import BaseSettings, Field


class Settings(BaseSettings):
    """Application settings with environment variable support."""
    
    # Project paths
    BASE_DIR: Path = Path(__file__).parent.parent
    DATA_DIR: Path = BASE_DIR / "data"
    RAW_PDF_DIR: Path = DATA_DIR / "raw"
    PROCESSED_DIR: Path = DATA_DIR / "processed"
    VECTORS_DIR: Path = DATA_DIR / "vectors"
    LOGS_DIR: Path = BASE_DIR / "logs"
    
    # Google API Configuration
    GOOGLE_APPLICATION_CREDENTIALS: Optional[str] = None
    GOOGLE_SHEETS_ID: Optional[str] = None
    GOOGLE_DRIVE_FOLDER_ID: Optional[str] = None
    
    # MongoDB Configuration
    MONGODB_URI: str = "mongodb://localhost:27017/"
    MONGODB_DATABASE: str = "ubri_papers"
    MONGODB_PAPERS_COLLECTION: str = "papers"
    MONGODB_CHUNKS_COLLECTION: str = "chunks"
    MONGODB_STATUS_COLLECTION: str = "processing_status"
    
    # OpenAI Configuration (for embeddings)
    OPENAI_API_KEY: Optional[str] = None
    OPENAI_MODEL: str = "text-embedding-ada-002"
    
    # Processing Configuration
    MAX_CONCURRENT_DOWNLOADS: int = 5
    MAX_CONCURRENT_PROCESSING: int = 3
    CHUNK_SIZE: int = 1000
    CHUNK_OVERLAP: int = 200
    BATCH_SIZE: int = 32
    
    # Logging Configuration
    LOG_LEVEL: str = "INFO"
    LOG_FILE: str = "logs/processing.log"
    
    # Performance Configuration
    MEMORY_LIMIT_GB: int = 8
    TIMEOUT_SECONDS: int = 300
    RETRY_ATTEMPTS: int = 3
    RETRY_DELAY_SECONDS: int = 5
    
    # Development Configuration
    DEBUG: bool = False
    ENVIRONMENT: str = "development"
    
    class Config:
        env_file = ".env"
        case_sensitive = False
    
    def __post_init__(self):
        """Create necessary directories after initialization."""
        for directory in [self.DATA_DIR, self.RAW_PDF_DIR, self.PROCESSED_DIR, 
                         self.VECTORS_DIR, self.LOGS_DIR]:
            directory.mkdir(parents=True, exist_ok=True)


# Global settings instance
settings = Settings() 