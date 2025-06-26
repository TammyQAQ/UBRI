#!/usr/bin/env python3
"""
Retrieve PDF files from MongoDB GridFS for traceability and verification.
"""
import json
import logging
from pathlib import Path
from typing import Dict, Any, Optional, List
from datetime import datetime
from pymongo import MongoClient
from gridfs import GridFS
import hashlib

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class PDFRetriever:
    """Retrieve PDF files from MongoDB GridFS."""
    
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
    
    def retrieve_pdf_by_id(self, file_id: str, output_dir: str = "retrieved_pdfs") -> Optional[str]:
        """
        Retrieve a PDF file by its GridFS ID.
        
        Args:
            file_id: GridFS file ID
            output_dir: Directory to save the retrieved file
            
        Returns:
            Path to the retrieved file if successful, None otherwise
        """
        try:
            # Get file from GridFS
            grid_out = self.fs.get(file_id)
            
            # Create output directory
            output_path = Path(output_dir)
            output_path.mkdir(parents=True, exist_ok=True)
            
            # Generate filename
            filename = grid_out.filename or f"retrieved_{file_id}.pdf"
            file_path = output_path / filename
            
            # Save file
            with open(file_path, 'wb') as f:
                f.write(grid_out.read())
            
            logger.info(f"Retrieved PDF: {file_path}")
            return str(file_path)
            
        except Exception as e:
            logger.error(f"Failed to retrieve file {file_id}: {e}")
            return None
    
    def retrieve_pdf_by_title(self, title: str, output_dir: str = "retrieved_pdfs") -> Optional[str]:
        """
        Retrieve a PDF file by paper title.
        
        Args:
            title: Paper title to search for
            output_dir: Directory to save the retrieved file
            
        Returns:
            Path to the retrieved file if successful, None otherwise
        """
        try:
            # Find file by title in metadata
            grid_out = self.fs.find_one({"metadata.paper_title": {"$regex": title, "$options": "i"}})
            
            if not grid_out:
                logger.error(f"No PDF found for title: {title}")
                return None
            
            return self.retrieve_pdf_by_id(str(grid_out._id), output_dir)
            
        except Exception as e:
            logger.error(f"Failed to retrieve PDF by title '{title}': {e}")
            return None
    
    def retrieve_pdfs_by_university(self, university: str, output_dir: str = "retrieved_pdfs") -> List[str]:
        """
        Retrieve all PDFs from a specific university.
        
        Args:
            university: University name to search for
            output_dir: Directory to save the retrieved files
            
        Returns:
            List of paths to retrieved files
        """
        retrieved_files = []
        
        try:
            # Find all files from the university
            cursor = self.fs.find({"metadata.university": {"$regex": university, "$options": "i"}})
            
            for grid_out in cursor:
                file_path = self.retrieve_pdf_by_id(str(grid_out._id), output_dir)
                if file_path:
                    retrieved_files.append(file_path)
            
            logger.info(f"Retrieved {len(retrieved_files)} PDFs from {university}")
            return retrieved_files
            
        except Exception as e:
            logger.error(f"Failed to retrieve PDFs for university '{university}': {e}")
            return []
    
    def verify_file_integrity(self, file_id: str, original_path: Optional[str] = None) -> Dict[str, Any]:
        """
        Verify the integrity of a stored PDF file.
        
        Args:
            file_id: GridFS file ID
            original_path: Optional path to original file for comparison
            
        Returns:
            Verification results
        """
        try:
            # Get file from GridFS
            grid_out = self.fs.get(file_id)
            
            # Calculate hash of stored file
            stored_hash = grid_out.metadata.get('file_hash')
            
            # Read file content
            file_content = grid_out.read()
            
            # Calculate current hash
            current_hash = hashlib.sha256(file_content).hexdigest()
            
            # Compare with original file if provided
            original_hash = None
            original_size = None
            if original_path and Path(original_path).exists():
                original_hash = self._calculate_file_hash(Path(original_path))
                original_size = Path(original_path).stat().st_size
            
            verification = {
                'file_id': file_id,
                'filename': grid_out.filename,
                'stored_size': grid_out.length,
                'stored_hash': stored_hash,
                'current_hash': current_hash,
                'hash_match': stored_hash == current_hash if stored_hash else None,
                'original_size': original_size,
                'original_hash': original_hash,
                'size_match': original_size == grid_out.length if original_size else None,
                'original_hash_match': original_hash == current_hash if original_hash else None,
                'verification_timestamp': datetime.utcnow().isoformat()
            }
            
            return verification
            
        except Exception as e:
            logger.error(f"Failed to verify file {file_id}: {e}")
            return {'error': str(e)}
    
    def _calculate_file_hash(self, file_path: Path) -> str:
        """Calculate SHA-256 hash of file."""
        hash_sha256 = hashlib.sha256()
        with open(file_path, "rb") as f:
            for chunk in iter(lambda: f.read(4096), b""):
                hash_sha256.update(chunk)
        return hash_sha256.hexdigest()
    
    def list_all_stored_files(self) -> List[Dict[str, Any]]:
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
    
    def search_files(self, search_term: str, field: str = "paper_title") -> List[Dict[str, Any]]:
        """
        Search for files by metadata field.
        
        Args:
            search_term: Term to search for
            field: Metadata field to search in
            
        Returns:
            List of matching files
        """
        try:
            query = {f"metadata.{field}": {"$regex": search_term, "$options": "i"}}
            cursor = self.fs.find(query)
            
            results = []
            for grid_out in cursor:
                results.append({
                    "file_id": str(grid_out._id),
                    "filename": grid_out.filename,
                    "length": grid_out.length,
                    "upload_date": grid_out.upload_date,
                    "metadata": grid_out.metadata
                })
            
            return results
            
        except Exception as e:
            logger.error(f"Failed to search files: {e}")
            return []
    
    def get_storage_stats(self) -> Dict[str, Any]:
        """Get statistics about stored files."""
        try:
            total_files = self.db.pdf_files.files.count_documents({})
            total_size = sum(grid_out.length for grid_out in self.fs.find())
            
            # Get file count by university
            pipeline = [
                {"$group": {"_id": "$metadata.university", "count": {"$sum": 1}}},
                {"$sort": {"count": -1}}
            ]
            universities = list(self.db.pdf_files.files.aggregate(pipeline))
            
            # Get file count by year
            pipeline = [
                {"$group": {"_id": "$metadata.year", "count": {"$sum": 1}}},
                {"$sort": {"_id": 1}}
            ]
            years = list(self.db.pdf_files.files.aggregate(pipeline))
            
            stats = {
                'total_files': total_files,
                'total_size_bytes': total_size,
                'total_size_mb': round(total_size / (1024 * 1024), 2),
                'total_size_gb': round(total_size / (1024 * 1024 * 1024), 2),
                'universities': universities,
                'years': years,
                'stats_timestamp': datetime.utcnow().isoformat()
            }
            
            return stats
            
        except Exception as e:
            logger.error(f"Error getting storage stats: {e}")
            return {}
    
    def close(self):
        """Close MongoDB connection."""
        if self.client:
            self.client.close()
            logger.info("MongoDB connection closed")


def main():
    """Main function to demonstrate PDF retrieval."""
    logger.info("Starting PDF retrieval from MongoDB GridFS")
    
    # Initialize retriever
    retriever = PDFRetriever()
    
    try:
        # Get storage statistics
        stats = retriever.get_storage_stats()
        logger.info(f"Storage Statistics: {stats}")
        
        # List all stored files
        logger.info("\nAll stored files:")
        files = retriever.list_all_stored_files()
        for file_info in files[:10]:  # Show first 10 files
            logger.info(f"  📄 {file_info['filename']} ({file_info['length']} bytes)")
            logger.info(f"     ID: {file_info['file_id']}")
            logger.info(f"     Title: {file_info['metadata'].get('paper_title', 'N/A')}")
            logger.info(f"     University: {file_info['metadata'].get('university', 'N/A')}")
            logger.info("")
        
        # Example: Retrieve a specific file (uncomment and modify as needed)
        # if files:
        #     first_file_id = files[0]['file_id']
        #     retrieved_path = retriever.retrieve_pdf_by_id(first_file_id)
        #     if retrieved_path:
        #         logger.info(f"Successfully retrieved: {retrieved_path}")
        
        # Example: Search for files
        # search_results = retriever.search_files("blockchain", "paper_title")
        # logger.info(f"Found {len(search_results)} files matching 'blockchain'")
        
    except Exception as e:
        logger.error(f"Retrieval failed: {e}")
    finally:
        retriever.close()
    
    logger.info("PDF retrieval demonstration completed!")


if __name__ == "__main__":
    main() 