#!/usr/bin/env python3
"""
Main entry point for UBRI data preprocessing pipeline.
"""
import sys
from pathlib import Path

# Add src to Python path
sys.path.insert(0, str(Path(__file__).parent / "src"))

from src.utils.logger import setup_logging, get_logger


def main():
    """Main function to run the data preprocessing pipeline."""
    # Setup logging
    setup_logging(log_level="INFO", log_file="logs/processing.log")
    logger = get_logger(__name__)
    
    logger.info("Starting UBRI data preprocessing pipeline")
    
    try:
        # TODO: Implement the main processing pipeline
        # 1. Read paper index from local files
        # 2. Process PDF files
        # 3. Extract text and metadata
        # 4. Generate vector embeddings
        # 5. Store in MongoDB
        
        logger.info("Pipeline completed successfully")
        
    except Exception as e:
        logger.error(f"Pipeline failed: {e}", exc_info=True)
        sys.exit(1)


if __name__ == "__main__":
    main() 