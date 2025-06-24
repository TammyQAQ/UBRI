# PDF Content Extraction and MongoDB Import Guide

This guide will help you extract comprehensive content from your PDF papers (including text, tables, and metadata) and import everything into MongoDB for your AI search tool.

## Overview

The process involves three main steps:
1. **Extract PDF content** - Get text, tables, and metadata from PDFs
2. **Process content** - Clean and chunk the text for vector processing
3. **Import to MongoDB** - Store everything in MongoDB for search

## Step 1: Install Dependencies

First, install the required packages for PDF processing:

```bash
# Install PDF processing dependencies
pip install pdfplumber PyMuPDF Pillow

# Install MongoDB driver
pip install pymongo

# Install other dependencies
pip install pandas numpy
```

## Step 2: Extract PDF Content

### Option A: Simple Content Extraction (Recommended)

Run the simplified content extraction script:

```bash
python extract_pdf_content_simple.py
```

This will:
- Extract text content from all PDFs
- Extract tables from PDFs
- Create text chunks for vector processing
- Generate page summaries
- Save everything to `data/processed/papers_with_content.json`

### Option B: Advanced Content Extraction (With Images)

If you want to extract figures and images as well:

```bash
python extract_pdf_content.py
```

**Note:** This requires additional dependencies and may be slower.

## Step 3: Import to MongoDB

### Prerequisites

1. **Install MongoDB** (if not already installed):
   ```bash
   # On macOS with Homebrew
   brew install mongodb-community
   
   # Start MongoDB
   brew services start mongodb-community
   ```

2. **Verify MongoDB is running**:
   ```bash
   mongosh
   # Should connect to MongoDB shell
   ```

### Import Data

Run the MongoDB import script:

```bash
python import_to_mongodb.py
```

This will:
- Connect to MongoDB
- Create necessary indexes
- Import all papers with content
- Import text chunks for vector search
- Generate import summary

## MongoDB Schema

### Papers Collection

Each paper document contains:

```json
{
  "_id": ObjectId("..."),
  "title": "Paper Title",
  "authors": ["Author 1", "Author 2"],
  "year": 2023,
  "journal": "Journal Name",
  "abstract": "Abstract text...",
  "keywords": ["keyword1", "keyword2"],
  "university": "University Name",
  "file_path": "path/to/paper.pdf",
  "file_found": true,
  "content_extracted": true,
  "pdf_content": {
    "text_content": {
      "full_text": "Complete paper text...",
      "pages_text": [...],
      "sections": {
        "abstract": "...",
        "introduction": "...",
        "methods": "...",
        "results": "...",
        "discussion": "..."
      },
      "page_summaries": [...]
    },
    "tables": [...],
    "text_chunks": [...],
    "summary": {
      "total_pages": 15,
      "total_tables": 3,
      "total_chunks": 25,
      "total_words": 8500
    }
  },
  "imported_at": ISODate("2025-06-24T...")
}
```

### Chunks Collection

Text chunks for vector search:

```json
{
  "_id": ObjectId("..."),
  "paper_id": ObjectId("..."),
  "paper_title": "Paper Title",
  "chunk_id": "chunk_1",
  "chunk_index": 1,
  "text": "Chunk text content...",
  "start_char": 0,
  "end_char": 1000,
  "word_count": 150,
  "created_at": ISODate("2025-06-24T...")
}
```

## MongoDB Queries

### Basic Queries

```javascript
// Find all papers
db.papers.find()

// Find papers with extracted content
db.papers.find({"content_extracted": true})

// Find papers by university
db.papers.find({"university": "UCL"})

// Find papers by year
db.papers.find({"year": 2023})

// Find papers with specific keywords
db.papers.find({"keywords": "blockchain"})
```

### Advanced Queries

```javascript
// Find papers with tables
db.papers.find({
  "pdf_content.summary.total_tables": {"$gt": 0}
})

// Find papers by word count
db.papers.find({
  "pdf_content.summary.total_words": {"$gt": 5000}
})

// Find papers with specific sections
db.papers.find({
  "pdf_content.text_content.sections.abstract": {"$exists": true}
})

// Search text chunks
db.chunks.find({
  "text": {"$regex": "blockchain", "$options": "i"}
})
```

### Aggregation Queries

```javascript
// Papers by university
db.papers.aggregate([
  {"$group": {"_id": "$university", "count": {"$sum": 1}}},
  {"$sort": {"count": -1}}
])

// Papers by year
db.papers.aggregate([
  {"$match": {"year": {"$ne": null}}},
  {"$group": {"_id": "$year", "count": {"$sum": 1}}},
  {"$sort": {"_id": 1}}
])

// Average word count by university
db.papers.aggregate([
  {"$match": {"content_extracted": true}},
  {"$group": {
    "_id": "$university", 
    "avg_words": {"$avg": "$pdf_content.summary.total_words"},
    "count": {"$sum": 1}
  }},
  {"$sort": {"avg_words": -1}}
])
```

## Performance Optimization

### Indexes

The import script creates these indexes automatically:

```javascript
// Papers collection indexes
db.papers.createIndex({"title": 1})
db.papers.createIndex({"authors": 1})
db.papers.createIndex({"year": 1})
db.papers.createIndex({"university": 1})
db.papers.createIndex({"content_extracted": 1})

// Chunks collection indexes
db.chunks.createIndex({"paper_id": 1})
db.chunks.createIndex({"chunk_index": 1})
db.chunks.createIndex({"word_count": 1})
```

### Additional Indexes for Search

```javascript
// Text search index
db.chunks.createIndex({"text": "text"})

// Compound indexes
db.papers.createIndex({"university": 1, "year": 1})
db.papers.createIndex({"content_extracted": 1, "university": 1})
```

## Next Steps: Vector Search

Once your data is in MongoDB, you can:

1. **Generate embeddings** for text chunks
2. **Store vectors** in MongoDB or a vector database
3. **Implement semantic search** using the embeddings
4. **Build your AI search interface**

### Example Vector Search Setup

```python
# Generate embeddings for chunks
from sentence_transformers import SentenceTransformer
import numpy as np

model = SentenceTransformer('all-MiniLM-L6-v2')

# Get chunks from MongoDB
chunks = db.chunks.find()
for chunk in chunks:
    embedding = model.encode(chunk['text'])
    # Store embedding in MongoDB or vector database
```

## Troubleshooting

### Common Issues

1. **PDF extraction fails**:
   - Check if PDF files are corrupted
   - Ensure PDFs are not password protected
   - Try different PDF processing libraries

2. **MongoDB connection fails**:
   - Verify MongoDB is running
   - Check connection string
   - Ensure network connectivity

3. **Memory issues**:
   - Process papers in smaller batches
   - Increase system memory
   - Use streaming for large files

### Performance Tips

1. **Batch processing**: Process papers in batches of 50-100
2. **Memory management**: Clear variables after processing large files
3. **Parallel processing**: Use multiple processes for PDF extraction
4. **Database optimization**: Use appropriate indexes and connection pooling

## File Structure

After processing, you'll have:

```
data/
├── processed/
│   ├── mongodb_papers_clean.json          # Basic paper metadata
│   ├── papers_with_content.json           # Papers with extracted content
│   └── processing_summary.json            # Processing statistics
├── raw/
│   └── Publications/                      # Original PDF files
└── vectors/                               # Future: vector embeddings
```

## Monitoring

Check processing logs for:
- Extraction success/failure rates
- Processing time per paper
- Memory usage
- Database import statistics

The scripts provide detailed logging to help you monitor the process and identify any issues. 