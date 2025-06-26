# UBRI Research Papers Repository

A comprehensive data processing pipeline for 600+ research papers from the University of California Berkeley's Blockchain Research Initiative (UBRI), with MongoDB storage and PDF traceability.

## 🚀 Features

- **Complete PDF Traceability**: Store original PDF files in MongoDB GridFS
- **Rich Metadata**: Paper information, authors, universities, years, quality scores
- **Content Extraction**: Text, tables, and metadata from PDFs
- **Vector Search Ready**: Prepared for AI-powered paper discovery
- **Deduplication**: Automatic file hash-based deduplication
- **Integrity Verification**: SHA-256 hash verification for all stored files

## 📊 Data Summary

### Processing Statistics
- **Total Papers**: 496
- **Papers with PDF Files**: 294 (59.3% coverage)
- **Universities Represented**: 63+
- **Year Range**: 2017-2025
- **Total Storage**: 127.34 MB in MongoDB GridFS

### Top Universities by Paper Count
- UCL: 15 papers
- University of Oregon: 4 papers
- Delft University of Technology: 4 papers
- CMU: 4 papers
- University of Waterloo: 3 papers

## 🏗️ Repository Structure

```
UBRI/
├── data/
│   ├── raw/Publications/        # Original PDF files by university
│   └── processed/               # Processed data
│       ├── mongodb_papers_clean.json           # Main processed data
│       ├── papers_with_gridfs_references.json  # Papers with MongoDB references
│       └── processing_summary.json             # Processing statistics
├── scripts/                     # Processing scripts
├── config/                      # Configuration files
├── logs/                        # Processing logs
├── src/                         # Source code modules
└── tests/                       # Test files
```

## 🛠️ Installation & Setup

### 1. Install Dependencies
```bash
pip install -r requirements.txt
```

### 2. Test Your Setup
```bash
python test_pdf_storage.py
```

### 3. Store PDFs in MongoDB (Optional)
```bash
python store_pdfs_in_mongodb.py
```

### 4. Test PDF Retrieval
```bash
python retrieve_pdfs_from_mongodb.py
```

## 📁 Core Scripts

### PDF Storage & Retrieval
- **`store_pdfs_in_mongodb.py`** - Upload PDFs to MongoDB GridFS with metadata
- **`retrieve_pdfs_from_mongodb.py`** - Retrieve and verify PDFs from MongoDB
- **`test_pdf_storage.py`** - Test all components and connections

### Data Processing
- **`import_to_mongodb.py`** - Import processed papers to MongoDB
- **`process_excel_index.py`** - Process Excel index files
- **`extract_pdf_content.py`** - Extract text, tables, and metadata from PDFs

## 🗄️ MongoDB Integration

### Connection Details
- **Database**: `UBRI_Publication`
- **Collections**: 
  - `Papers` - Paper metadata and content
  - `pdf_files.files` - PDF file metadata (GridFS)
  - `pdf_files.chunks` - PDF file content chunks (GridFS)

### Schema Examples

#### Paper Document
```json
{
  "_id": "paper_id",
  "title": "Blockchain Research Paper",
  "authors": ["Author 1", "Author 2"],
  "university": "Stanford",
  "year": 2023,
  "file_found": true,
  "file_path": "data/raw/Publications/Stanford/paper.pdf",
  "gridfs_file_id": "685d2da7f6a25c263d7772c0",
  "pdf_stored_in_gridfs": true,
  "pdf_storage_timestamp": "2024-01-01T00:00:00Z",
  "pdf_content": {
    "text_chunks": [...],
    "tables": [...],
    "metadata": {...}
  }
}
```

#### GridFS File Metadata
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
    "file_hash": "sha256_hash",
    "file_size": 1234567,
    "original_filename": "paper.pdf",
    "file_path": "/path/to/original/file.pdf",
    "upload_timestamp": "2024-01-01T00:00:00Z",
    "content_type": "application/pdf"
  }
}
```

## 🔍 Usage Examples

### Store PDFs in MongoDB
```python
from store_pdfs_in_mongodb import PDFGridFSStorage

# Initialize storage
storage = PDFGridFSStorage()

# Store all papers with PDFs
updated_papers = storage.store_papers_with_pdfs()

# Get storage summary
summary = storage.get_storage_summary()
print(f"Stored {summary['total_files']} files ({summary['total_size_mb']} MB)")
```

### Retrieve PDFs from MongoDB
```python
from retrieve_pdfs_from_mongodb import PDFRetriever

# Initialize retriever
retriever = PDFRetriever()

# Retrieve by GridFS ID
pdf_path = retriever.retrieve_pdf_by_id("685d2da7f6a25c263d7772c0")

# Retrieve by paper title
pdf_path = retriever.retrieve_pdf_by_title("Blockchain Research Paper")

# Retrieve all PDFs from a university
pdf_paths = retriever.retrieve_pdfs_by_university("Stanford")

# Verify file integrity
verification = retriever.verify_file_integrity("file_id", "original_path.pdf")
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

## 🔧 Advanced Features

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

### Batch Operations
```python
# Retrieve all PDFs from multiple universities
universities = ["Stanford", "MIT", "Berkeley"]
for university in universities:
    pdf_paths = retriever.retrieve_pdfs_by_university(university)
    print(f"Retrieved {len(pdf_paths)} PDFs from {university}")
```

### Storage Monitoring
```python
# Get storage statistics
stats = retriever.get_storage_stats()
print(f"Storage usage: {stats['total_size_gb']} GB")
print(f"File count: {stats['total_files']}")

# Monitor by university
for uni in stats['universities']:
    print(f"{uni['_id']}: {uni['count']} files")
```

## 🚨 Troubleshooting

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

## 📈 Performance Considerations

### Storage Optimization
- **Deduplication**: Files automatically deduplicated using SHA-256 hashes
- **Compression**: MongoDB's Wired Tiger engine compresses data automatically
- **Chunking**: Large files split into 255KB chunks for efficient storage

### Retrieval Performance
- **Indexing**: Create indexes on frequently searched metadata fields
- **Streaming**: Large files can be streamed without loading entirely into memory
- **Caching**: Consider caching frequently accessed files

## 🔒 Security Considerations

### Access Control
- Use MongoDB authentication and authorization
- Implement role-based access to GridFS collections
- Consider encrypting sensitive PDF content

### Data Integrity
- File hashes ensure data integrity
- Regular integrity checks can be automated
- Backup strategies for GridFS collections

## 🎯 Next Steps

1. **Vector Embeddings**: Add vector embeddings for AI-powered search
2. **Web Interface**: Build a web interface for paper discovery
3. **API Development**: Create REST API for programmatic access
4. **Advanced Analytics**: Implement citation analysis and research trends
5. **Integration**: Connect with external research databases

## 📝 Contributing

1. Ensure all scripts are placed in the appropriate directories
2. Update this README when adding new functionality
3. Test data processing pipeline before committing changes
4. Maintain data integrity and backup raw files
5. Follow the project structure and coding standards

## 📄 License

This repository contains research papers and data from various universities. Please respect the original authors' rights and institutional policies when using this data.

## 🤝 Support

For questions or issues:
1. Check the troubleshooting section above
2. Review the test scripts for examples
3. Examine the logs in the `logs/` directory
4. Verify your MongoDB connection and permissions

---

**Built with ❤️ for the UBRI research community**
