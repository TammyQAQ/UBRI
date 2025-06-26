#!/usr/bin/env python3
"""
Store actual PDF files in MongoDB using GridFS for traceability.
"""
import json
import logging
from pathlib import Path
from typing import Dict, Any, Optional
from datetime import datetime
from pymongo import MongoClient
from gridfs import GridFS
import hashlib

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class PDFGridFSStorage:
    """Store PDF files in MongoDB using GridFS."""
    
    def __init__(self, 
                 mongodb_uri: str = "mongodb+srv://yitianw:2T9KEjQqvMBSZ68Y@cluster0.jvwt789.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0",
                 database_name: str = "UBRI_Publication"):
        
        self.mongodb_uri = mongodb_uri
        self.database_name = database_name
        
        # Connect to MongoDB
        self.client = MongoClient(mongodb_uri)
        self.db = self.client[database_name]
        
        # Initialize GridFS
        self.fs = GridFS(self.db, collection="pdf_files")
        
        logger.info(f"Connected to MongoDB: {mongodb_uri}")
        logger.info(f"Database: {database_name}")
        logger.info("GridFS initialized for PDF storage")
    
    def store_pdf_file(self, pdf_path: str, metadata: Dict[str, Any]) -> Optional[str]:
        """
        Store a PDF file in GridFS with metadata.
        
        Args:
            pdf_path: Path to the PDF file
            metadata: Additional metadata to store with the file
            
        Returns:
            GridFS file ID if successful, None otherwise
        """
        pdf_path = Path(pdf_path)
        
        if not pdf_path.exists():
            logger.error(f"PDF file not found: {pdf_path}")
            return None
        
        try:
            # Calculate file hash for deduplication
            file_hash = self._calculate_file_hash(pdf_path)
            
            # Check if file already exists
            existing_file = self.fs.find_one({"metadata.file_hash": file_hash})
            if existing_file:
                logger.info(f"File already exists in GridFS: {pdf_path.name}")
                return str(existing_file._id)
            
            # Prepare metadata
            file_metadata = {
                "original_filename": pdf_path.name,
                "file_path": str(pdf_path),
                "file_size": pdf_path.stat().st_size,
                "file_hash": file_hash,
                "upload_timestamp": datetime.utcnow(),
                "content_type": "application/pdf",
                **metadata
            }
            
            # Store file in GridFS
            with open(pdf_path, 'rb') as pdf_file:
                file_id = self.fs.put(
                    pdf_file,
                    filename=pdf_path.name,
                    metadata=file_metadata
                )
            
            logger.info(f"Successfully stored PDF: {pdf_path.name} (ID: {file_id})")
            return str(file_id)
            
        except Exception as e:
            logger.error(f"Failed to store PDF {pdf_path.name}: {e}")
            return None
    
    def _calculate_file_hash(self, file_path: Path) -> str:
        """Calculate SHA-256 hash of file for deduplication."""
        hash_sha256 = hashlib.sha256()
        with open(file_path, "rb") as f:
            for chunk in iter(lambda: f.read(4096), b""):
                hash_sha256.update(chunk)
        return hash_sha256.hexdigest()
    
    def retrieve_pdf_file(self, file_id: str, output_path: Optional[str] = None) -> Optional[bytes]:
        """
        Retrieve a PDF file from GridFS.
        
        Args:
            file_id: GridFS file ID
            output_path: Optional path to save the file
            
        Returns:
            File content as bytes if successful, None otherwise
        """
        try:
            # Get file from GridFS
            grid_out = self.fs.get(file_id)
            
            # Read file content
            file_content = grid_out.read()
            
            # Save to file if output path provided
            if output_path:
                output_path = Path(output_path)
                output_path.parent.mkdir(parents=True, exist_ok=True)
                with open(output_path, 'wb') as f:
                    f.write(file_content)
                logger.info(f"File saved to: {output_path}")
            
            return file_content
            
        except Exception as e:
            logger.error(f"Failed to retrieve file {file_id}: {e}")
            return None
    
    def get_file_metadata(self, file_id: str) -> Optional[Dict[str, Any]]:
        """Get metadata for a stored file."""
        try:
            grid_out = self.fs.get(file_id)
            return grid_out.metadata
        except Exception as e:
            logger.error(f"Failed to get metadata for file {file_id}: {e}")
            return None
    
    def list_stored_files(self) -> list:
        """List all stored PDF files with their metadata."""
        files = []
        for grid_out in self.fs.find():
            files.append({
                "file_id": str(grid_out._id),
                "filename": grid_out.filename,
                "length": grid_out.length,
                "upload_date": grid_out.upload_date,
                "metadata": grid_out.metadata
            })
        return files
    
    def store_papers_with_pdfs(self, json_file: str = "data/processed/mongodb_papers_clean.json"):
        """Store PDF files for all papers that have them."""
        json_path = Path(json_file)
        
        if not json_path.exists():
            logger.error(f"JSON file not found: {json_file}")
            return
        
        logger.info(f"Processing papers from: {json_file}")
        
        # Load papers
        with open(json_path, 'r', encoding='utf-8') as f:
            papers = json.load(f)
        
        stored_files = 0
        failed_stores = 0
        updated_papers = []
        
        for paper in papers:
            if paper.get('file_found') and paper.get('file_path'):
                pdf_path = paper['file_path']
                
                # Prepare metadata for GridFS
                metadata = {
                    "paper_title": paper.get('title', ''),
                    "authors": paper.get('authors', []),
                    "year": paper.get('year'),
                    "university": paper.get('university', ''),
                    "journal": paper.get('journal', ''),
                    "doi": paper.get('doi', ''),
                    "paper_id": paper.get('_id', ''),
                    "quality": paper.get('quality', ''),
                    "relevance": paper.get('relevance', ''),
                    "discipline": paper.get('discipline', '')
                }
                
                # Store PDF in GridFS
                file_id = self.store_pdf_file(pdf_path, metadata)
                
                if file_id:
                    # Update paper document with GridFS file ID
                    paper['gridfs_file_id'] = file_id
                    paper['pdf_stored_in_gridfs'] = True
                    paper['pdf_storage_timestamp'] = datetime.utcnow().isoformat()
                    stored_files += 1
                else:
                    paper['pdf_stored_in_gridfs'] = False
                    paper['pdf_storage_error'] = "Failed to store in GridFS"
                    failed_stores += 1
                
                updated_papers.append(paper)
            else:
                # Paper without PDF file
                paper['pdf_stored_in_gridfs'] = False
                paper['gridfs_file_id'] = None
                updated_papers.append(paper)
        
        # Save updated papers with GridFS references
        output_file = Path("data/processed/papers_with_gridfs_references.json")
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(updated_papers, f, indent=2, ensure_ascii=False)
        
        logger.info(f"PDF storage completed!")
        logger.info(f"Files stored in GridFS: {stored_files}")
        logger.info(f"Failed stores: {failed_stores}")
        logger.info(f"Updated papers saved to: {output_file}")
        
        return updated_papers
    
    def get_storage_summary(self) -> Dict[str, Any]:
        """Get summary of stored files."""
        try:
            total_files = self.db.pdf_files.files.count_documents({})
            total_size = sum(grid_out.length for grid_out in self.fs.find())
            
            # Get file count by university
            pipeline = [
                {"$group": {"_id": "$metadata.university", "count": {"$sum": 1}}},
                {"$sort": {"count": -1}}
            ]
            universities = list(self.db.pdf_files.files.aggregate(pipeline))
            
            summary = {
                'total_files': total_files,
                'total_size_bytes': total_size,
                'total_size_mb': round(total_size / (1024 * 1024), 2),
                'universities': universities,
                'storage_timestamp': datetime.utcnow().isoformat()
            }
            
            return summary
            
        except Exception as e:
            logger.error(f"Error getting storage summary: {e}")
            return {}
    
    def close(self):
        """Close MongoDB connection."""
        if self.client:
            self.client.close()
            logger.info("MongoDB connection closed")


def main():
    """Main function to store PDFs in MongoDB."""
    logger.info("Starting PDF storage in MongoDB GridFS")
    
    # Initialize storage
    storage = PDFGridFSStorage()
    
    try:
        # Store PDFs for all papers
        updated_papers = storage.store_papers_with_pdfs()
        
        # Get storage summary
        summary = storage.get_storage_summary()
        logger.info(f"Storage Summary: {summary}")
        
        # Show some example files
        logger.info("\nExample stored files:")
        files = storage.list_stored_files()
        for file_info in files[:5]:  # Show first 5 files
            logger.info(f"  📄 {file_info['filename']} ({file_info['length']} bytes)")
        
    except Exception as e:
        logger.error(f"Storage failed: {e}")
    finally:
        storage.close()
    
    logger.info("PDF storage in MongoDB completed!")


if __name__ == "__main__":
    main() 