#!/usr/bin/env python3
"""
Simple script to process local PDF files for UBRI data preprocessing.
"""
import os
import sys
import json
from pathlib import Path
from typing import List, Dict, Any
import logging

# Setup basic logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class SimplePaperProcessor:
    """Simple paper processor for local PDF files."""
    
    def __init__(self, pdf_directory: str = "data/raw"):
        self.pdf_directory = Path(pdf_directory)
        self.processed_data = []
        
    def find_pdf_files(self) -> List[Path]:
        """Find all PDF files in the specified directory."""
        if not self.pdf_directory.exists():
            logger.warning(f"PDF directory does not exist: {self.pdf_directory}")
            return []
        
        pdf_files = list(self.pdf_directory.glob("*.pdf"))
        logger.info(f"Found {len(pdf_files)} PDF files")
        return pdf_files
    
    def extract_basic_info(self, pdf_path: Path) -> Dict[str, Any]:
        """Extract basic information from PDF file."""
        try:
            # Get file info
            stat = pdf_path.stat()
            
            info = {
                'filename': pdf_path.name,
                'file_path': str(pdf_path),
                'file_size': stat.st_size,
                'created': stat.st_ctime,
                'modified': stat.st_mtime,
                'status': 'pending'
            }
            
            logger.info(f"Processed file info: {pdf_path.name}")
            return info
            
        except Exception as e:
            logger.error(f"Error processing {pdf_path.name}: {e}")
            return {
                'filename': pdf_path.name,
                'file_path': str(pdf_path),
                'status': 'error',
                'error': str(e)
            }
    
    def process_all_papers(self) -> List[Dict[str, Any]]:
        """Process all PDF files in the directory."""
        pdf_files = self.find_pdf_files()
        
        if not pdf_files:
            logger.warning("No PDF files found to process")
            return []
        
        logger.info(f"Starting to process {len(pdf_files)} papers")
        
        for pdf_file in pdf_files:
            try:
                paper_info = self.extract_basic_info(pdf_file)
                self.processed_data.append(paper_info)
                
            except Exception as e:
                logger.error(f"Failed to process {pdf_file.name}: {e}")
                self.processed_data.append({
                    'filename': pdf_file.name,
                    'status': 'failed',
                    'error': str(e)
                })
        
        logger.info(f"Completed processing {len(self.processed_data)} papers")
        return self.processed_data
    
    def save_results(self, output_file: str = "data/processed/papers_index.json"):
        """Save processing results to JSON file."""
        output_path = Path(output_file)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        
        try:
            with open(output_path, 'w', encoding='utf-8') as f:
                json.dump(self.processed_data, f, indent=2, ensure_ascii=False)
            
            logger.info(f"Results saved to: {output_path}")
            
        except Exception as e:
            logger.error(f"Failed to save results: {e}")
    
    def generate_summary(self) -> Dict[str, Any]:
        """Generate a summary of the processing results."""
        total_files = len(self.processed_data)
        successful = len([p for p in self.processed_data if p.get('status') == 'pending'])
        failed = len([p for p in self.processed_data if p.get('status') in ['error', 'failed']])
        
        total_size = sum(p.get('file_size', 0) for p in self.processed_data if p.get('file_size'))
        
        summary = {
            'total_files': total_files,
            'successful': successful,
            'failed': failed,
            'total_size_bytes': total_size,
            'total_size_mb': round(total_size / (1024 * 1024), 2)
        }
        
        logger.info(f"Processing Summary: {summary}")
        return summary


def main():
    """Main function to run the paper processing."""
    logger.info("Starting UBRI Paper Processing")
    
    # Initialize processor
    processor = SimplePaperProcessor()
    
    # Process all papers
    results = processor.process_all_papers()
    
    # Save results
    processor.save_results()
    
    # Generate summary
    summary = processor.generate_summary()
    
    logger.info("Paper processing completed!")
    logger.info(f"Summary: {summary}")


if __name__ == "__main__":
    main() 