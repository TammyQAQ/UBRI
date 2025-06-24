"""
Data models for UBRI paper processing.
"""
from datetime import datetime
from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field


class PaperMetadata(BaseModel):
    """Metadata for a research paper."""
    title: str
    authors: List[str]
    year: Optional[int] = None
    doi: Optional[str] = None
    journal: Optional[str] = None
    abstract: Optional[str] = None
    keywords: Optional[List[str]] = None
    file_path: Optional[str] = None
    file_size: Optional[int] = None
    
    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }


class TextChunk(BaseModel):
    """A chunk of text from a paper."""
    paper_id: str
    chunk_index: int
    text: str
    section: Optional[str] = None
    page_number: Optional[int] = None
    start_char: Optional[int] = None
    end_char: Optional[int] = None
    
    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }


class VectorChunk(TextChunk):
    """A text chunk with its vector embedding."""
    embedding: List[float]
    embedding_model: str
    embedding_timestamp: datetime = Field(default_factory=datetime.utcnow)
    
    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }


class ProcessingStatus(BaseModel):
    """Status tracking for paper processing."""
    paper_id: str
    status: str  # pending, processing, completed, failed
    current_step: Optional[str] = None
    progress: float = 0.0  # 0.0 to 1.0
    error_message: Optional[str] = None
    started_at: datetime = Field(default_factory=datetime.utcnow)
    completed_at: Optional[datetime] = None
    metadata: Optional[Dict[str, Any]] = None
    
    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }


class ProcessingConfig(BaseModel):
    """Configuration for processing parameters."""
    chunk_size: int = 1000
    chunk_overlap: int = 200
    max_concurrent: int = 3
    embedding_model: str = "text-embedding-ada-002"
    batch_size: int = 32
    
    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat()
        } 