# MongoDB PDF Storage Guide

This guide explains how to store actual PDF files in MongoDB using GridFS for complete traceability and retrieval.

## Why Store PDFs in MongoDB?

Based on the [MongoDB community discussion](https://www.mongodb.com/community/forums/t/what-is-the-best-way-to-store-an-actual-document-file/111714/6), MongoDB stores data in its original size using the Wired Tiger Storage Engine with compression. This makes it ideal for storing PDF files with:

- **Complete traceability**: Original files are preserved exactly as uploaded
- **Metadata storage**: Rich metadata alongside the files
- **Deduplication**: File hashing prevents duplicate storage
- **Scalability**: GridFS handles files larger than 16MB efficiently
- **Retrieval**: Easy access to original files when needed

## Architecture Overview

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Paper Data    │    │   PDF Content   │    │   PDF Files     │
│   (JSON)        │    │   (Text/Chunks) │    │   (GridFS)      │
└─────────────────┘    └─────────────────┘    └─────────────────┘
         │                       │                       │
         └───────────────────────┼───────────────────────┘
                                 │
                    ┌─────────────────┐
                    │   MongoDB       │
                    │   Collections   │
                    └─────────────────┘
```

## Installation

The required dependencies are already in `requirements.txt`:

```bash
pip install -r requirements.txt
```

Key dependencies:
- `pymongo==4.6.0` - MongoDB driver (includes GridFS)
- `gridfs` - Part of pymongo package

## Usage

### 1. Store PDFs in MongoDB

Run the PDF storage script to upload all PDF files to GridFS:

```bash
python store_pdfs_in_mongodb.py
```

This script will:
- Read the processed papers JSON
- Upload each PDF to GridFS with rich metadata
- Calculate file hashes for deduplication
- Update paper documents with GridFS file IDs
- Save updated papers with GridFS references

### 2. Retrieve PDFs from MongoDB

Use the retrieval script to access stored PDFs:

```bash
python retrieve_pdfs_from_mongodb.py
```

## Key Features

### File Storage (`store_pdfs_in_mongodb.py`)

```python
from store_pdfs_in_mongodb import PDFGridFSStorage

# Initialize storage
storage = PDFGridFSStorage()

# Store a single PDF
file_id = storage.store_pdf_file(
    pdf_path="path/to/paper.pdf",
    metadata={
        "paper_title": "Blockchain Research Paper",
        "authors": ["Author 1", "Author 2"],
        "university": "Stanford",
        "year": 2023
    }
)

# Store all papers with PDFs
updated_papers = storage.store_papers_with_pdfs()
```

### File Retrieval (`retrieve_pdfs_from_mongodb.py`)

```python
from retrieve_pdfs_from_mongodb import PDFRetriever

# Initialize retriever
retriever = PDFRetriever()

# Retrieve by GridFS ID
pdf_path = retriever.retrieve_pdf_by_id("gridfs_file_id")

# Retrieve by paper title
pdf_path = retriever.retrieve_pdf_by_title("Blockchain Research Paper")

# Retrieve all PDFs from a university
pdf_paths = retriever.retrieve_pdfs_by_university("Stanford")

# Verify file integrity
verification = retriever.verify_file_integrity("gridfs_file_id", "original_path.pdf")
```

## MongoDB Schema

### GridFS Collections

MongoDB creates two collections for GridFS:

1. **`pdf_files.files`** - File metadata
2. **`pdf_files.chunks`** - File content chunks

### File Metadata Structure

```json
{
  "_id": "ObjectId",
  "filename": "paper.pdf",
  "length": 1234567,
  "uploadDate": "2024-01-01T00:00:00Z",
  "metadata": {
    "paper_title": "Blockchain Research Paper",
    "authors": ["Author 1", "Author 2"],
    "university": "Stanford",
    "year": 2023,
    "journal": "Journal Name",
    "doi": "10.1234/paper",
    "file_hash": "sha256_hash",
    "file_size": 1234567,
    "original_filename": "paper.pdf",
    "file_path": "/path/to/original/file.pdf",
    "upload_timestamp": "2024-01-01T00:00:00Z",
    "content_type": "application/pdf"
  }
}
```

### Updated Paper Document Structure

```json
{
  "_id": "paper_id",
  "title": "Blockchain Research Paper",
  "authors": ["Author 1", "Author 2"],
  "university": "Stanford",
  "year": 2023,
  "file_found": true,
  "file_path": "/path/to/original/file.pdf",
  "gridfs_file_id": "gridfs_file_id",
  "pdf_stored_in_gridfs": true,
  "pdf_storage_timestamp": "2024-01-01T00:00:00Z",
  "pdf_content": {
    "text_chunks": [...],
    "tables": [...],
    "metadata": {...}
  }
}
```

## Advanced Usage

### File Integrity Verification

```python
# Verify a stored file matches the original
verification = retriever.verify_file_integrity(
    file_id="gridfs_file_id",
    original_path="original_file.pdf"
)

print(f"Hash match: {verification['hash_match']}")
print(f"Size match: {verification['size_match']}")
```

### Search and Filter

```python
# Search files by title
results = retriever.search_files("blockchain", "paper_title")

# Search files by university
results = retriever.search_files("Stanford", "university")

# Get storage statistics
stats = retriever.get_storage_stats()
print(f"Total files: {stats['total_files']}")
print(f"Total size: {stats['total_size_gb']} GB")
```

### Batch Operations

```python
# Retrieve all PDFs from multiple universities
universities = ["Stanford", "MIT", "Berkeley"]
for university in universities:
    pdf_paths = retriever.retrieve_pdfs_by_university(university)
    print(f"Retrieved {len(pdf_paths)} PDFs from {university}")
```

## Performance Considerations

### Storage Optimization

- **Deduplication**: Files are automatically deduplicated using SHA-256 hashes
- **Compression**: MongoDB's Wired Tiger engine compresses data automatically
- **Chunking**: Large files are split into 255KB chunks for efficient storage

### Retrieval Performance

- **Indexing**: Create indexes on frequently searched metadata fields
- **Streaming**: Large files can be streamed without loading entirely into memory
- **Caching**: Consider caching frequently accessed files

### Monitoring

```python
# Get storage statistics
stats = retriever.get_storage_stats()
print(f"Storage usage: {stats['total_size_gb']} GB")
print(f"File count: {stats['total_files']}")

# Monitor by university
for uni in stats['universities']:
    print(f"{uni['_id']}: {uni['count']} files")
```

## Security Considerations

### Access Control

- Use MongoDB authentication and authorization
- Implement role-based access to GridFS collections
- Consider encrypting sensitive PDF content

### Data Integrity

- File hashes ensure data integrity
- Regular integrity checks can be automated
- Backup strategies for GridFS collections

## Troubleshooting

### Common Issues

1. **Connection Errors**: Check MongoDB connection string and network access
2. **File Not Found**: Verify file paths and permissions
3. **Memory Issues**: Use streaming for large files
4. **Duplicate Files**: Check file hash deduplication logic

### Debug Commands

```python
# List all stored files
files = retriever.list_all_stored_files()
for file_info in files:
    print(f"ID: {file_info['file_id']}")
    print(f"Name: {file_info['filename']}")
    print(f"Size: {file_info['length']} bytes")

# Check specific file metadata
metadata = retriever.get_file_metadata("gridfs_file_id")
print(json.dumps(metadata, indent=2))
```

## Next Steps

1. **Run the storage script** to upload all PDFs to MongoDB
2. **Test retrieval** with a few sample files
3. **Verify integrity** of stored files
4. **Monitor storage usage** and performance
5. **Integrate with vector search** for AI-powered paper discovery

## Benefits of This Approach

- ✅ **Complete traceability**: Original PDFs are preserved exactly
- ✅ **Rich metadata**: All paper information stored with files
- ✅ **Easy retrieval**: Multiple ways to find and access files
- ✅ **Data integrity**: Hash verification ensures file authenticity
- ✅ **Scalability**: GridFS handles large files efficiently
- ✅ **Deduplication**: Prevents storage of duplicate files
- ✅ **Search capability**: Full-text and metadata search
- ✅ **Backup friendly**: MongoDB backup includes all files

This approach ensures you have complete control and traceability over your research paper PDFs while maintaining efficient storage and retrieval capabilities. 