#!/usr/bin/env python3
"""
Fix JSON serialization issues and create proper MongoDB-ready JSON.
"""
import json
import pandas as pd
from pathlib import Path
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def fix_na_values(obj):
    """Recursively replace pandas NA values with None for JSON serialization."""
    if pd.isna(obj):
        return None
    elif isinstance(obj, dict):
        return {key: fix_na_values(value) for key, value in obj.items()}
    elif isinstance(obj, list):
        return [fix_na_values(item) for item in obj]
    else:
        return obj


def main():
    """Fix the JSON serialization and create proper MongoDB documents."""
    # Read the Excel file again and process it properly
    from process_excel_index import ExcelIndexProcessor
    
    processor = ExcelIndexProcessor()
    papers = processor.process_index()
    
    # Fix NA values
    fixed_papers = fix_na_values(papers)
    
    # Save to new file
    output_file = "data/processed/mongodb_papers_fixed.json"
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(fixed_papers, f, indent=2, ensure_ascii=False)
    
    logger.info(f"Fixed JSON saved to: {output_file}")
    logger.info(f"Total papers processed: {len(fixed_papers)}")
    
    # Create a sample document for verification
    if fixed_papers:
        sample = fixed_papers[0]
        logger.info("Sample document structure:")
        for key, value in sample.items():
            if key != 'metadata':  # Skip metadata for brevity
                logger.info(f"  {key}: {type(value).__name__} = {str(value)[:100]}...")


if __name__ == "__main__":
    main() 