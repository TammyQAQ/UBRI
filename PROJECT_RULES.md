# UBRI Data Preprocessing Project Rules

## Project Overview
This project processes 600+ research papers stored in Google Drive, extracts text content, creates vector embeddings, and stores them in MongoDB for AI search functionality.

## Project Structure
```
UBRI/
├── config/                 # Configuration files
│   ├── settings.py        # Main configuration
│   └── mongodb_config.py  # MongoDB connection settings
├── src/                   # Source code
│   ├── __init__.py
│   ├── data_extraction/   # PDF processing and text extraction
│   ├── vectorization/     # Embedding generation
│   ├── database/          # MongoDB operations
│   └── utils/             # Utility functions
├── data/                  # Data storage
│   ├── raw/              # Raw PDF files (if downloaded)
│   ├── processed/        # Extracted text and metadata
│   └── vectors/          # Vector embeddings
├── tests/                # Unit tests
├── logs/                 # Processing logs
├── requirements.txt      # Python dependencies
├── .env.example         # Environment variables template
└── README.md           # Project documentation
```

## Coding Standards

### 1. Code Style
- Follow PEP 8 style guidelines
- Use type hints for all function parameters and return values
- Maximum line length: 88 characters (Black formatter)
- Use meaningful variable and function names
- Add docstrings for all functions and classes

### 2. Error Handling
- Implement comprehensive error handling for all external API calls
- Log all errors with appropriate context
- Use custom exceptions for domain-specific errors
- Implement retry mechanisms for network operations

### 3. Logging
- Use structured logging with appropriate log levels
- Include timestamps, process IDs, and context in log messages
- Log progress for long-running operations
- Separate logs by processing stage

### 4. Configuration Management
- Use environment variables for sensitive data (API keys, credentials)
- Centralize configuration in config/settings.py
- Validate configuration on startup
- Use .env files for local development

## Data Processing Pipeline

### Phase 1: Data Extraction
1. **Google Sheets Integration**
   - Read paper index from Google Sheets
   - Validate paper metadata (title, authors, year, etc.)
   - Track processing status for each paper

2. **Google Drive Integration**
   - Download PDF files from Google Drive
   - Implement rate limiting to respect API quotas
   - Handle different file formats and sizes
   - Verify file integrity after download

3. **PDF Processing**
   - Extract text content using PyPDF2 or pdfplumber
   - Handle multi-column layouts and tables
   - Extract figures and captions
   - Preserve document structure (sections, subsections)

### Phase 2: Text Preprocessing
1. **Text Cleaning**
   - Remove headers, footers, page numbers
   - Clean up formatting artifacts
   - Normalize whitespace and special characters
   - Handle mathematical expressions and formulas

2. **Content Segmentation**
   - Split into logical sections (abstract, introduction, methods, etc.)
   - Identify and extract references
   - Separate main content from appendices

3. **Metadata Extraction**
   - Extract title, authors, abstract, keywords
   - Identify publication venue and year
   - Extract DOI and other identifiers

### Phase 3: Vectorization
1. **Text Chunking**
   - Split documents into appropriate chunk sizes
   - Maintain semantic coherence within chunks
   - Handle overlapping chunks for better context

2. **Embedding Generation**
   - Use sentence-transformers or OpenAI embeddings
   - Implement batch processing for efficiency
   - Cache embeddings to avoid reprocessing
   - Handle API rate limits and quotas

### Phase 4: Database Storage
1. **MongoDB Schema Design**
   - Papers collection: metadata and basic info
   - Chunks collection: text chunks with embeddings
   - Processing status tracking
   - Index optimization for vector search

2. **Data Validation**
   - Validate data integrity before storage
   - Implement duplicate detection
   - Ensure proper indexing for performance

## Performance Requirements

### Processing Speed
- Target: Process 100+ papers per hour
- Implement parallel processing where possible
- Use async/await for I/O operations
- Implement progress tracking and resumability

### Resource Management
- Monitor memory usage during processing
- Implement garbage collection for large files
- Use streaming for large PDF files
- Implement connection pooling for database operations

### Error Recovery
- Implement checkpointing for long-running processes
- Allow resuming from last successful state
- Maintain processing logs for debugging
- Implement dead letter queues for failed items

## Security and Privacy

### Data Protection
- Never commit API keys or credentials to version control
- Use environment variables for sensitive data
- Implement proper access controls for Google Drive
- Encrypt sensitive data in transit and at rest

### API Usage
- Respect rate limits for all external APIs
- Implement exponential backoff for retries
- Monitor API usage and costs
- Cache responses when appropriate

## Testing Strategy

### Unit Tests
- Test all utility functions
- Mock external API calls
- Test error handling scenarios
- Achieve 80%+ code coverage

### Integration Tests
- Test end-to-end processing pipeline
- Test database operations
- Test Google Drive and Sheets integration
- Test vector search functionality

### Performance Tests
- Test processing speed with sample data
- Test memory usage with large files
- Test database query performance
- Load testing for concurrent operations

## Monitoring and Maintenance

### Health Checks
- Monitor processing pipeline status
- Track success/failure rates
- Monitor API usage and costs
- Database performance monitoring

### Maintenance Tasks
- Regular cleanup of temporary files
- Database optimization and indexing
- Log rotation and archival
- Dependency updates and security patches

## Documentation Requirements

### Code Documentation
- Comprehensive docstrings for all functions
- README files for each module
- API documentation for external interfaces
- Architecture diagrams and flowcharts

### User Documentation
- Setup and installation instructions
- Configuration guide
- Troubleshooting guide
- Performance tuning recommendations

## Version Control

### Git Workflow
- Use feature branches for development
- Require code review before merging
- Use conventional commit messages
- Tag releases with semantic versioning

### Branch Naming
- `feature/paper-processing` - New features
- `bugfix/pdf-extraction` - Bug fixes
- `hotfix/critical-error` - Critical fixes
- `docs/readme-update` - Documentation updates

## Deployment and Environment

### Environment Setup
- Use virtual environments for Python
- Docker containerization for consistency
- Environment-specific configurations
- Automated deployment scripts

### Dependencies
- Pin all dependency versions
- Regular security updates
- Minimal dependency footprint
- Clear dependency documentation

## Success Metrics

### Processing Metrics
- Papers processed per hour
- Success rate percentage
- Average processing time per paper
- Error rate and types

### Quality Metrics
- Text extraction accuracy
- Vector embedding quality
- Search result relevance
- Data completeness

### Performance Metrics
- Memory usage patterns
- CPU utilization
- Database query performance
- API response times 