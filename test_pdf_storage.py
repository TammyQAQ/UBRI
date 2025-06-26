#!/usr/bin/env python3
"""
Test script to verify PDF storage and retrieval functionality.
"""
import json
import logging
from pathlib import Path
from datetime import datetime

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def test_dependencies():
    """Test if all required dependencies are available."""
    logger.info("Testing dependencies...")
    
    try:
        import pymongo
        logger.info("✅ pymongo imported successfully")
        
        from gridfs import GridFS
        logger.info("✅ gridfs imported successfully")
        
        from pymongo import MongoClient
        logger.info("✅ MongoClient imported successfully")
        
        return True
        
    except ImportError as e:
        logger.error(f"❌ Import error: {e}")
        logger.error("Please install dependencies: pip install -r requirements.txt")
        return False


def test_mongodb_connection():
    """Test MongoDB connection."""
    logger.info("Testing MongoDB connection...")
    
    try:
        from pymongo import MongoClient
        from gridfs import GridFS
        
        # Test connection
        mongodb_uri = "mongodb+srv://yitianw:2T9KEjQqvMBSZ68Y@cluster0.jvwt789.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0"
        client = MongoClient(mongodb_uri)
        
        # Test database access
        db = client["UBRI_Publication"]
        logger.info("✅ MongoDB connection successful")
        
        # Test GridFS initialization
        fs = GridFS(db, collection="pdf_files")
        logger.info("✅ GridFS initialized successfully")
        
        # Test basic operations - use count_documents instead of count
        file_count = db.pdf_files.files.count_documents({})
        logger.info(f"✅ GridFS file count: {file_count}")
        
        client.close()
        return True
        
    except Exception as e:
        logger.error(f"❌ MongoDB connection failed: {e}")
        return False


def test_data_files():
    """Test if required data files exist."""
    logger.info("Testing data files...")
    
    required_files = [
        "data/processed/mongodb_papers_clean.json",
        "data/raw/Publications"
    ]
    
    all_exist = True
    for file_path in required_files:
        path = Path(file_path)
        if path.exists():
            logger.info(f"✅ {file_path} exists")
        else:
            logger.error(f"❌ {file_path} not found")
            all_exist = False
    
    return all_exist


def test_pdf_files():
    """Test if PDF files are available."""
    logger.info("Testing PDF files...")
    
    publications_dir = Path("data/raw/Publications")
    if not publications_dir.exists():
        logger.error("❌ Publications directory not found")
        return False
    
    # Count PDF files
    pdf_files = list(publications_dir.rglob("*.pdf"))
    logger.info(f"✅ Found {len(pdf_files)} PDF files")
    
    if len(pdf_files) > 0:
        logger.info(f"✅ Sample PDF: {pdf_files[0].name}")
        return True
    else:
        logger.warning("⚠️ No PDF files found")
        return False


def test_json_data():
    """Test if JSON data is valid."""
    logger.info("Testing JSON data...")
    
    json_file = Path("data/processed/mongodb_papers_clean.json")
    if not json_file.exists():
        logger.error("❌ JSON file not found")
        return False
    
    try:
        with open(json_file, 'r', encoding='utf-8') as f:
            papers = json.load(f)
        
        logger.info(f"✅ Loaded {len(papers)} papers from JSON")
        
        # Check for papers with PDF files
        papers_with_pdfs = [p for p in papers if p.get('file_found')]
        logger.info(f"✅ {len(papers_with_pdfs)} papers have PDF files")
        
        if papers_with_pdfs:
            sample_paper = papers_with_pdfs[0]
            logger.info(f"✅ Sample paper: {sample_paper.get('title', 'Unknown')[:50]}...")
            logger.info(f"✅ PDF path: {sample_paper.get('file_path', 'N/A')}")
        
        return True
        
    except Exception as e:
        logger.error(f"❌ JSON loading failed: {e}")
        return False


def main():
    """Run all tests."""
    logger.info("=" * 50)
    logger.info("PDF Storage Test Suite")
    logger.info("=" * 50)
    
    tests = [
        ("Dependencies", test_dependencies),
        ("MongoDB Connection", test_mongodb_connection),
        ("Data Files", test_data_files),
        ("PDF Files", test_pdf_files),
        ("JSON Data", test_json_data),
    ]
    
    results = {}
    for test_name, test_func in tests:
        logger.info(f"\n--- Testing {test_name} ---")
        try:
            results[test_name] = test_func()
        except Exception as e:
            logger.error(f"❌ {test_name} test failed with exception: {e}")
            results[test_name] = False
    
    # Summary
    logger.info("\n" + "=" * 50)
    logger.info("TEST SUMMARY")
    logger.info("=" * 50)
    
    passed = sum(results.values())
    total = len(results)
    
    for test_name, result in results.items():
        status = "✅ PASS" if result else "❌ FAIL"
        logger.info(f"{test_name}: {status}")
    
    logger.info(f"\nOverall: {passed}/{total} tests passed")
    
    if passed == total:
        logger.info("🎉 All tests passed! Ready to store PDFs in MongoDB.")
        logger.info("\nNext steps:")
        logger.info("1. Run: python store_pdfs_in_mongodb.py")
        logger.info("2. Run: python retrieve_pdfs_from_mongodb.py")
    else:
        logger.error("⚠️ Some tests failed. Please fix issues before proceeding.")
    
    return passed == total


if __name__ == "__main__":
    main() 