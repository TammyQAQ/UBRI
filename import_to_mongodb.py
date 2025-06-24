#!/usr/bin/env python3
"""
Import processed papers with content into MongoDB.
"""
import json
import logging
from pathlib import Path
from typing import List, Dict, Any
from datetime import datetime
import pymongo
from pymongo import MongoClient

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class MongoDBImporter:
    """Import papers with content into MongoDB."""
    
    def __init__(self, 
                 mongodb_uri: str = "mongodb://localhost:27017/",
                 database_name: str = "ubri_papers",
                 papers_collection: str = "papers",
                 chunks_collection: str = "chunks"):
        
        self.mongodb_uri = mongodb_uri
        self.database_name = database_name
        self.papers_collection = papers_collection
        self.chunks_collection = chunks_collection
        
        # Connect to MongoDB
        self.client = MongoClient(mongodb_uri)
        self.db = self.client[database_name]
        self.papers_coll = self.db[papers_collection]
        self.chunks_coll = self.db[chunks_collection]
        
        logger.info(f"Connected to MongoDB: {mongodb_uri}")
        logger.info(f"Database: {database_name}")
    
    def create_indexes(self):
        """Create necessary indexes for optimal performance."""
        try:
            # Papers collection indexes
            self.papers_coll.create_index("title")
            self.papers_coll.create_index("authors")
            self.papers_coll.create_index("year")
            self.papers_coll.create_index("university")
            self.papers_coll.create_index("content_extracted")
            self.papers_coll.create_index("file_found")
            
            # Chunks collection indexes
            self.chunks_coll.create_index("paper_id")
            self.chunks_coll.create_index("chunk_index")
            self.chunks_coll.create_index("word_count")
            
            logger.info("Successfully created MongoDB indexes")
            
        except Exception as e:
            logger.error(f"Failed to create indexes: {e}")
            raise
    
    def import_papers(self, json_file: str = "data/processed/papers_with_content.json"):
        """Import papers from JSON file into MongoDB."""
        json_path = Path(json_file)
        
        if not json_path.exists():
            logger.error(f"JSON file not found: {json_file}")
            return
        
        logger.info(f"Importing papers from: {json_file}")
        
        # Load papers
        with open(json_path, 'r', encoding='utf-8') as f:
            papers = json.load(f)
        
        logger.info(f"Loaded {len(papers)} papers from JSON")
        
        # Import papers
        imported_papers = 0
        imported_chunks = 0
        failed_imports = 0
        
        for paper in papers:
            try:
                # Prepare paper document for MongoDB
                paper_doc = self._prepare_paper_document(paper)
                
                # Insert paper
                result = self.papers_coll.insert_one(paper_doc)
                paper_id = result.inserted_id
                imported_papers += 1
                
                # Import text chunks if available
                if paper.get('pdf_content') and paper.get('content_extracted'):
                    chunks = self._prepare_chunk_documents(paper, paper_id)
                    if chunks:
                        self.chunks_coll.insert_many(chunks)
                        imported_chunks += len(chunks)
                
                logger.info(f"Imported paper: {paper.get('title', 'Unknown')[:50]}...")
                
            except Exception as e:
                logger.error(f"Failed to import paper {paper.get('title', 'Unknown')}: {e}")
                failed_imports += 1
                continue
        
        logger.info(f"Import completed!")
        logger.info(f"Papers imported: {imported_papers}")
        logger.info(f"Chunks imported: {imported_chunks}")
        logger.info(f"Failed imports: {failed_imports}")
    
    def _prepare_paper_document(self, paper: Dict[str, Any]) -> Dict[str, Any]:
        """Prepare paper document for MongoDB insertion."""
        # Remove MongoDB-specific fields that might conflict
        paper_doc = paper.copy()
        
        # Ensure _id is not present (MongoDB will generate it)
        if '_id' in paper_doc:
            del paper_doc['_id']
        
        # Add import timestamp
        paper_doc['imported_at'] = datetime.utcnow()
        
        # Clean up any None values that might cause issues
        paper_doc = self._clean_document(paper_doc)
        
        return paper_doc
    
    def _prepare_chunk_documents(self, paper: Dict[str, Any], paper_id) -> List[Dict[str, Any]]:
        """Prepare chunk documents for MongoDB insertion."""
        chunks = []
        
        if not paper.get('pdf_content') or not paper.get('pdf_content').get('text_chunks'):
            return chunks
        
        for chunk in paper['pdf_content']['text_chunks']:
            chunk_doc = {
                'paper_id': paper_id,
                'paper_title': paper.get('title', ''),
                'chunk_id': chunk.get('chunk_id', ''),
                'chunk_index': chunk.get('chunk_index', 0),
                'text': chunk.get('text', ''),
                'start_char': chunk.get('start_char', 0),
                'end_char': chunk.get('end_char', 0),
                'word_count': chunk.get('word_count', 0),
                'created_at': datetime.utcnow()
            }
            
            chunks.append(chunk_doc)
        
        return chunks
    
    def _clean_document(self, doc: Dict[str, Any]) -> Dict[str, Any]:
        """Clean document by removing None values and handling special cases."""
        cleaned = {}
        
        for key, value in doc.items():
            if value is None:
                continue
            elif isinstance(value, dict):
                cleaned[key] = self._clean_document(value)
            elif isinstance(value, list):
                cleaned[key] = [item for item in value if item is not None]
            else:
                cleaned[key] = value
        
        return cleaned
    
    def get_import_summary(self) -> Dict[str, Any]:
        """Get summary of imported data."""
        try:
            total_papers = self.papers_coll.count_documents({})
            papers_with_content = self.papers_coll.count_documents({"content_extracted": True})
            total_chunks = self.chunks_coll.count_documents({})
            
            # Get university distribution
            pipeline = [
                {"$group": {"_id": "$university", "count": {"$sum": 1}}},
                {"$sort": {"count": -1}}
            ]
            universities = list(self.papers_coll.aggregate(pipeline))
            
            # Get year distribution
            pipeline = [
                {"$match": {"year": {"$ne": None}}},
                {"$group": {"_id": "$year", "count": {"$sum": 1}}},
                {"$sort": {"_id": 1}}
            ]
            years = list(self.papers_coll.aggregate(pipeline))
            
            summary = {
                'total_papers': total_papers,
                'papers_with_content': papers_with_content,
                'total_chunks': total_chunks,
                'universities': universities[:10],  # Top 10
                'years': years,
                'import_timestamp': datetime.utcnow().isoformat()
            }
            
            return summary
            
        except Exception as e:
            logger.error(f"Error getting import summary: {e}")
            return {}
    
    def close(self):
        """Close MongoDB connection."""
        if self.client:
            self.client.close()
            logger.info("MongoDB connection closed")


def main():
    """Main function to import papers into MongoDB."""
    logger.info("Starting MongoDB import")
    
    # Initialize importer
    importer = MongoDBImporter()
    
    try:
        # Create indexes
        importer.create_indexes()
        
        # Import papers
        importer.import_papers()
        
        # Get summary
        summary = importer.get_import_summary()
        logger.info(f"Import Summary: {summary}")
        
    except Exception as e:
        logger.error(f"Import failed: {e}")
    finally:
        importer.close()
    
    logger.info("MongoDB import completed!")


if __name__ == "__main__":
    main() 