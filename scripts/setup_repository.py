#!/usr/bin/env python3
"""
Repository Setup and Organization Script

This script:
1. Organizes the repository structure
2. Validates data integrity
3. Provides MongoDB setup instructions
4. Creates necessary symbolic links
5. Generates a comprehensive README
"""
import json
import os
import shutil
from pathlib import Path
from typing import Dict, List, Any
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class RepositorySetup:
    """Setup and organize the UBRI repository."""
    
    def __init__(self):
        self.root_dir = Path.cwd()
        self.data_dir = self.root_dir / "data"
        self.scripts_dir = self.root_dir / "scripts"
        self.processed_dir = self.data_dir / "processed"
        self.raw_dir = self.data_dir / "raw"
        
    def validate_structure(self) -> Dict[str, Any]:
        """Validate the current repository structure."""
        logger.info("Validating repository structure...")
        
        validation = {
            'structure_valid': True,
            'issues': [],
            'warnings': [],
            'data_summary': {}
        }
        
        # Check required directories
        required_dirs = [
            self.data_dir,
            self.processed_dir,
            self.raw_dir,
            self.scripts_dir
        ]
        
        for dir_path in required_dirs:
            if not dir_path.exists():
                validation['structure_valid'] = False
                validation['issues'].append(f"Missing directory: {dir_path}")
            else:
                logger.info(f"✓ Directory exists: {dir_path}")
        
        # Check processed data files
        processed_files = [
            self.processed_dir / "mongodb_papers_clean.json",
            self.processed_dir / "processing_summary.json"
        ]
        
        for file_path in processed_files:
            if not file_path.exists():
                validation['issues'].append(f"Missing processed file: {file_path}")
            else:
                file_size = file_path.stat().st_size
                logger.info(f"✓ Processed file: {file_path} ({file_size:,} bytes)")
                validation['data_summary'][file_path.name] = {
                    'size_bytes': file_size,
                    'exists': True
                }
        
        # Check raw data structure
        if self.raw_dir.exists():
            raw_subdirs = [d for d in self.raw_dir.iterdir() if d.is_dir()]
            validation['data_summary']['raw_subdirectories'] = len(raw_subdirs)
            logger.info(f"✓ Raw data subdirectories: {len(raw_subdirs)}")
        
        return validation
    
    def create_symbolic_links(self):
        """Create necessary symbolic links for compatibility."""
        logger.info("Creating symbolic links...")
        
        # Link the processed JSON file to the expected name
        source_file = self.processed_dir / "mongodb_papers_clean.json"
        target_file = self.processed_dir / "papers_with_content.json"
        
        if source_file.exists():
            # Remove existing symlink if it exists
            if target_file.exists() or target_file.is_symlink():
                try:
                    target_file.unlink()
                    logger.info(f"✓ Removed existing symlink: {target_file}")
                except Exception as e:
                    logger.warning(f"Could not remove existing symlink: {e}")
            
            try:
                os.symlink(source_file, target_file)
                logger.info(f"✓ Created symlink: {target_file} -> {source_file}")
            except Exception as e:
                logger.error(f"Failed to create symlink: {e}")
        else:
            logger.error(f"Source file does not exist: {source_file}")
    
    def analyze_data_content(self) -> Dict[str, Any]:
        """Analyze the content of processed data."""
        logger.info("Analyzing data content...")
        
        analysis = {}
        
        # Analyze processing summary
        summary_file = self.processed_dir / "processing_summary.json"
        if summary_file.exists():
            with open(summary_file, 'r') as f:
                summary = json.load(f)
            analysis['processing_summary'] = summary
            logger.info(f"✓ Processing summary loaded: {summary.get('total_papers', 0)} papers")
        
        # Analyze main data file
        data_file = self.processed_dir / "mongodb_papers_clean.json"
        if data_file.exists():
            try:
                with open(data_file, 'r') as f:
                    papers = json.load(f)
                
                analysis['data_file'] = {
                    'total_papers': len(papers),
                    'papers_with_content': sum(1 for p in papers if p.get('content_extracted', False)),
                    'papers_with_pdf_files': sum(1 for p in papers if p.get('file_found', False)),
                    'universities': len(set(p.get('university', '') for p in papers if p.get('university'))),
                    'years': sorted(set(p.get('year') for p in papers if p.get('year')))
                }
                
                logger.info(f"✓ Data file analyzed: {len(papers)} papers")
                
            except Exception as e:
                logger.error(f"Failed to analyze data file: {e}")
                analysis['data_file'] = {'error': str(e)}
        
        return analysis
    
    def generate_readme(self, validation: Dict[str, Any], analysis: Dict[str, Any]):
        """Generate a comprehensive README file."""
        logger.info("Generating README...")
        
        readme_content = """# UBRI Research Papers Repository

This repository contains processed research papers from the University of California Berkeley's Blockchain Research Initiative (UBRI).

## Repository Structure

```
UBRI/
├── data/
│   ├── raw/                    # Original PDF files organized by university
│   └── processed/              # Processed and cleaned data
│       ├── mongodb_papers_clean.json    # Main processed data
│       ├── processing_summary.json      # Processing statistics
│       └── papers_with_content.json     # Symlink to main data
├── scripts/                    # All processing and utility scripts
├── config/                     # Configuration files
├── logs/                       # Processing logs
└── src/                        # Source code modules
```

## Data Summary

### Processing Statistics
- **Total Papers**: {total_papers}
- **Papers with PDF Files**: {papers_with_pdf}
- **File Coverage**: {coverage}%

### Data File Analysis
- **Total Papers in Database**: {db_total}
- **Papers with Extracted Content**: {db_with_content}
- **Papers with PDF Files**: {db_with_pdf}
- **Universities Represented**: {universities}
- **Year Range**: {years}

## Setup Instructions

### 1. Install Dependencies
```bash
pip install -r requirements.txt
```

### 2. MongoDB Setup (Optional)
To enable full-text search and advanced querying:

1. **Install MongoDB**:
   - macOS: `brew install mongodb-community`
   - Ubuntu: `sudo apt-get install mongodb`
   - Windows: Download from [MongoDB website](https://www.mongodb.com/try/download/community)

2. **Start MongoDB**:
   ```bash
   mongod --dbpath /path/to/data/directory
   ```

3. **Import Data**:
   ```bash
   cd scripts
   python import_to_mongodb.py
   ```

### 3. Verify Setup
```bash
python scripts/setup_repository.py
```

## Scripts Overview

### Data Processing Scripts
- `process_excel_index.py` - Process Excel index files
- `extract_pdf_content.py` - Extract content from PDF files
- `extract_pdf_content_simple.py` - Simplified PDF extraction
- `process_papers.py` - Main paper processing pipeline
- `fix_json_serialization.py` - Fix JSON serialization issues

### Database Scripts
- `import_to_mongodb.py` - Import data to MongoDB
- `create_mongodb_json.py` - Create MongoDB-compatible JSON

### Utility Scripts
- `pdf_processor.py` - PDF processing utilities
- `run_full_pipeline.py` - Complete processing pipeline
- `setup_repository.py` - Repository setup and validation

## Data Access

### JSON Format
The main data is stored in `data/processed/mongodb_papers_clean.json` with the following structure:

```json
{{
  "_id": "paper_id",
  "title": "Paper Title",
  "authors": ["Author 1", "Author 2"],
  "year": 2023,
  "university": "University Name",
  "file_path": "relative/path/to/pdf",
  "file_found": true,
  "content_extracted": true,
  "pdf_content": {{
    "text_chunks": [
      {{
        "chunk_id": "chunk_1",
        "text": "Extracted text content...",
        "word_count": 150
      }}
    ]
  }}
}}
```

### MongoDB Collections
If MongoDB is set up, data is organized into two collections:
- `papers` - Main paper metadata and content
- `chunks` - Text chunks for full-text search

## Usage Examples

### Query Papers by University
```python
# Using JSON
import json
with open('data/processed/mongodb_papers_clean.json', 'r') as f:
    papers = json.load(f)
berkeley_papers = [p for p in papers if p.get('university') == 'Berkeley']

# Using MongoDB
from pymongo import MongoClient
client = MongoClient('mongodb://localhost:27017/')
db = client['ubri_papers']
berkeley_papers = list(db.papers.find({{'university': 'Berkeley'}}))
```

### Search Paper Content
```python
# Using MongoDB full-text search
results = db.papers.find({{'$text': {{'$search': 'blockchain'}}}})
```

## Validation Status

{validation_status} Repository structure is valid
{issues_status} No critical issues found

### Issues Found:
{issues_list}

### Warnings:
{warnings_list}

## Contributing

1. Ensure all scripts are placed in the `scripts/` directory
2. Update this README when adding new functionality
3. Test data processing pipeline before committing changes
4. Maintain data integrity and backup raw files

## License

This repository contains research papers and data from various universities. Please respect the original authors' rights and institutional policies when using this data.
""".format(
            total_papers=analysis.get('processing_summary', {}).get('total_papers', 'N/A'),
            papers_with_pdf=analysis.get('processing_summary', {}).get('papers_with_pdf_files', 'N/A'),
            coverage=analysis.get('processing_summary', {}).get('file_coverage_percentage', 'N/A'),
            db_total=analysis.get('data_file', {}).get('total_papers', 'N/A'),
            db_with_content=analysis.get('data_file', {}).get('papers_with_content', 'N/A'),
            db_with_pdf=analysis.get('data_file', {}).get('papers_with_pdf_files', 'N/A'),
            universities=analysis.get('data_file', {}).get('universities', 'N/A'),
            years=analysis.get('data_file', {}).get('years', []),
            validation_status='✓' if validation['structure_valid'] else '✗',
            issues_status='✓' if not validation['issues'] else '✗',
            issues_list='\n'.join(f"- {issue}" for issue in validation['issues']) if validation['issues'] else "None",
            warnings_list='\n'.join(f"- {warning}" for warning in validation['warnings']) if validation['warnings'] else "None"
        )
        
        readme_path = self.root_dir / "README.md"
        with open(readme_path, 'w') as f:
            f.write(readme_content)
        
        logger.info(f"✓ README generated: {readme_path}")
    
    def run_setup(self):
        """Run the complete setup process."""
        logger.info("Starting repository setup...")
        
        # Validate structure
        validation = self.validate_structure()
        
        # Create symbolic links
        self.create_symbolic_links()
        
        # Analyze data content
        analysis = self.analyze_data_content()
        
        # Generate README
        self.generate_readme(validation, analysis)
        
        # Print summary
        logger.info("\n" + "="*50)
        logger.info("SETUP COMPLETE")
        logger.info("="*50)
        
        if validation['structure_valid']:
            logger.info("✓ Repository structure is valid")
        else:
            logger.error("✗ Repository structure has issues")
            for issue in validation['issues']:
                logger.error(f"  - {issue}")
        
        logger.info(f"✓ Total papers: {analysis.get('data_file', {}).get('total_papers', 'N/A')}")
        logger.info(f"✓ Papers with content: {analysis.get('data_file', {}).get('papers_with_content', 'N/A')}")
        
        logger.info("\nNext steps:")
        logger.info("1. Install MongoDB if you want full-text search capabilities")
        logger.info("2. Run: cd scripts && python import_to_mongodb.py")
        logger.info("3. Check the generated README.md for detailed usage instructions")


def main():
    """Main function."""
    setup = RepositorySetup()
    setup.run_setup()


if __name__ == "__main__":
    main()