#!/usr/bin/env python3
"""
Master script to run the complete UBRI data processing pipeline.
"""
import logging
import sys
from pathlib import Path
from datetime import datetime

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(f'logs/pipeline_{datetime.now().strftime("%Y%m%d_%H%M%S")}.log'),
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger(__name__)


def run_pipeline():
    """Run the complete data processing pipeline."""
    logger.info("=" * 60)
    logger.info("STARTING UBRI DATA PROCESSING PIPELINE")
    logger.info("=" * 60)
    
    # Create logs directory
    Path("logs").mkdir(exist_ok=True)
    
    try:
        # Step 1: Process Excel index
        logger.info("\n" + "=" * 40)
        logger.info("STEP 1: Processing Excel Index")
        logger.info("=" * 40)
        
        try:
            from create_mongodb_json import main as process_excel
            process_excel()
            logger.info("✅ Excel index processing completed successfully")
        except Exception as e:
            logger.error(f"❌ Excel index processing failed: {e}")
            return False
        
        # Step 2: Extract PDF content
        logger.info("\n" + "=" * 40)
        logger.info("STEP 2: Extracting PDF Content")
        logger.info("=" * 40)
        
        try:
            from extract_pdf_content_simple import main as extract_content
            extract_content()
            logger.info("✅ PDF content extraction completed successfully")
        except Exception as e:
            logger.error(f"❌ PDF content extraction failed: {e}")
            logger.info("Continuing with basic metadata only...")
        
        # Step 3: Import to MongoDB (optional)
        logger.info("\n" + "=" * 40)
        logger.info("STEP 3: MongoDB Import (Optional)")
        logger.info("=" * 40)
        
        # Check if MongoDB import is requested
        import_mongo = input("\nDo you want to import to MongoDB now? (y/n): ").lower().strip()
        
        if import_mongo == 'y':
            try:
                from import_to_mongodb import main as import_mongo
                import_mongo()
                logger.info("✅ MongoDB import completed successfully")
            except Exception as e:
                logger.error(f"❌ MongoDB import failed: {e}")
                logger.info("You can run the import manually later using: python import_to_mongodb.py")
        else:
            logger.info("⏭️  Skipping MongoDB import")
            logger.info("You can run it later using: python import_to_mongodb.py")
        
        # Final summary
        logger.info("\n" + "=" * 60)
        logger.info("PIPELINE COMPLETED SUCCESSFULLY!")
        logger.info("=" * 60)
        
        # Show generated files
        logger.info("\nGenerated files:")
        processed_dir = Path("data/processed")
        if processed_dir.exists():
            for file in processed_dir.glob("*.json"):
                size_mb = file.stat().st_size / (1024 * 1024)
                logger.info(f"  📄 {file.name} ({size_mb:.1f} MB)")
        
        logger.info("\nNext steps:")
        logger.info("1. Review the generated JSON files in data/processed/")
        logger.info("2. Install MongoDB if you haven't already")
        logger.info("3. Run: python import_to_mongodb.py")
        logger.info("4. Start building your AI search tool!")
        
        return True
        
    except KeyboardInterrupt:
        logger.info("\n⚠️  Pipeline interrupted by user")
        return False
    except Exception as e:
        logger.error(f"\n❌ Pipeline failed with error: {e}")
        return False


def check_dependencies():
    """Check if required dependencies are installed."""
    logger.info("Checking dependencies...")
    
    missing_deps = []
    
    try:
        import pandas
        logger.info("✅ pandas")
    except ImportError:
        missing_deps.append("pandas")
        logger.error("❌ pandas")
    
    try:
        import pdfplumber
        logger.info("✅ pdfplumber")
    except ImportError:
        missing_deps.append("pdfplumber")
        logger.error("❌ pdfplumber")
    
    try:
        import pymongo
        logger.info("✅ pymongo")
    except ImportError:
        missing_deps.append("pymongo")
        logger.error("❌ pymongo")
    
    if missing_deps:
        logger.error(f"\nMissing dependencies: {', '.join(missing_deps)}")
        logger.info("Install them using:")
        logger.info(f"pip install {' '.join(missing_deps)}")
        return False
    
    logger.info("✅ All dependencies are installed")
    return True


def main():
    """Main function."""
    logger.info("UBRI Data Processing Pipeline")
    logger.info(f"Started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    # Check dependencies
    if not check_dependencies():
        logger.error("Please install missing dependencies and try again")
        return
    
    # Run pipeline
    success = run_pipeline()
    
    if success:
        logger.info("\n🎉 Pipeline completed successfully!")
        logger.info("Check the logs for detailed information")
    else:
        logger.error("\n💥 Pipeline failed!")
        logger.info("Check the logs for error details")


if __name__ == "__main__":
    main() 