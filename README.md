# UBRI Research Papers Repository

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
- **Total Papers**: 644
- **Papers with PDF Files**: 373
- **File Coverage**: 57.92%

### Data File Analysis
- **Total Papers in Database**: 496
- **Papers with Extracted Content**: 0
- **Papers with PDF Files**: 294
- **Universities Represented**: 63
- **Year Range**: [2017.0, 2018.0, 2019.0, 2020.0, 2021.0, 2022.0, 2023.0, 2024.0, 2025.0]

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
{
  "_id": "paper_id",
  "title": "Paper Title",
  "authors": ["Author 1", "Author 2"],
  "year": 2023,
  "university": "University Name",
  "file_path": "relative/path/to/pdf",
  "file_found": true,
  "content_extracted": true,
  "pdf_content": {
    "text_chunks": [
      {
        "chunk_id": "chunk_1",
        "text": "Extracted text content...",
        "word_count": 150
      }
    ]
  }
}
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
berkeley_papers = list(db.papers.find({'university': 'Berkeley'}))
```

### Search Paper Content
```python
# Using MongoDB full-text search
results = db.papers.find({'$text': {'$search': 'blockchain'}})
```

## Validation Status

✓ Repository structure is valid
✓ No critical issues found

### Issues Found:
None

### Warnings:
None

## Contributing

1. Ensure all scripts are placed in the `scripts/` directory
2. Update this README when adding new functionality
3. Test data processing pipeline before committing changes
4. Maintain data integrity and backup raw files

## License

This repository contains research papers and data from various universities. Please respect the original authors' rights and institutional policies when using this data.
