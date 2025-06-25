#!/usr/bin/env python3
"""
Create MongoDB-ready JSON from Excel index.
"""
import pandas as pd
import json
from pathlib import Path
import logging
from datetime import datetime
import re

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def clean_value(value):
    """Clean a value for JSON serialization."""
    if pd.isna(value) or value == '' or value == 'nan':
        return None
    if isinstance(value, (int, float)):
        return value
    return str(value).strip()


def parse_authors(authors_str):
    """Parse authors string into list."""
    if not authors_str or authors_str == 'nan':
        return []
    
    # Common separators
    separators = [';', ',', ' and ', ' & ']
    
    for sep in separators:
        if sep in authors_str:
            authors = [author.strip() for author in authors_str.split(sep)]
            return [author for author in authors if author and author != 'nan']
    
    return [authors_str.strip()] if authors_str.strip() and authors_str != 'nan' else []


def parse_keywords(keywords_str):
    """Parse keywords string into list."""
    if not keywords_str or keywords_str == 'nan':
        return []
    
    separators = [';', ',', '|']
    
    for sep in separators:
        if sep in keywords_str:
            keywords = [keyword.strip() for keyword in keywords_str.split(sep)]
            return [keyword for keyword in keywords if keyword and keyword != 'nan']
    
    return [keywords_str.strip()] if keywords_str.strip() and keywords_str != 'nan' else []


def find_pdf_file(title, university, publications_dir):
    """Find corresponding PDF file."""
    publications_path = Path(publications_dir)
    
    # Search in university-specific directories first
    if university:
        university_dir = publications_path / university
        if university_dir.exists():
            for pdf_file in university_dir.rglob("*.pdf"):
                if title_matches_file(title, pdf_file.name):
                    return str(pdf_file)
    
    # Search in all subdirectories
    for pdf_file in publications_path.rglob("*.pdf"):
        if title_matches_file(title, pdf_file.name):
            return str(pdf_file)
    
    return None


def title_matches_file(title, filename):
    """Check if title matches filename."""
    if not title or title == 'nan':
        return False
    
    filename_no_ext = Path(filename).stem.lower()
    clean_title = re.sub(r'[^\w\s]', '', title.lower())
    
    title_words = set(clean_title.split())
    filename_words = set(filename_no_ext.split('_'))
    
    common_words = title_words.intersection(filename_words)
    return len(common_words) >= min(3, len(title_words) // 2)


def main():
    """Main processing function."""
    logger.info("Creating MongoDB-ready JSON from Excel index")
    
    # Read Excel file
    excel_file = "data/raw/Publications/UBRI Publications_.xlsx"
    df = pd.read_excel(excel_file)
    
    logger.info(f"Read {len(df)} rows from Excel file")
    
    # Clean column names
    column_mapping = {
        'Title': 'title',
        'Author': 'authors',
        'Year': 'year',
        'Venue': 'journal',
        'Abstract': 'abstract',
        'Keywords': 'keywords',
        'University': 'university',
        'Type of publication': 'type',
        'Quality': 'quality',
        'Relevance': 'relevance',
        'Discipline': 'discipline',
        'Comment': 'comment',
        'Link': 'link',
        'Link.1': 'link_alt'
    }
    
    df.columns = df.columns.str.strip()
    for old_name, new_name in column_mapping.items():
        if old_name in df.columns:
            df = df.rename(columns={old_name: new_name})
    
    # Process each row
    mongodb_docs = []
    
    for index, row in df.iterrows():
        try:
            # Skip completely empty rows
            if row.isna().all():
                continue
            
            # Find PDF file
            title = clean_value(row.get('title', ''))
            university = clean_value(row.get('university', ''))
            pdf_path = find_pdf_file(title, university, "data/raw/Publications")
            
            # Create MongoDB document
            doc = {
                '_id': f"paper_{index + 1}",
                'title': clean_value(row.get('title', '')),
                'authors': parse_authors(row.get('authors', '')),
                'year': clean_value(row.get('year', '')),
                'journal': clean_value(row.get('journal', '')),
                'venue': clean_value(row.get('journal', '')),
                'abstract': clean_value(row.get('abstract', '')),
                'keywords': parse_keywords(row.get('keywords', '')),
                'university': clean_value(row.get('university', '')),
                'type': clean_value(row.get('type', '')),
                'quality': clean_value(row.get('quality', '')),
                'relevance': clean_value(row.get('relevance', '')),
                'discipline': clean_value(row.get('discipline', '')),
                'comment': clean_value(row.get('comment', '')),
                'link': clean_value(row.get('link', '')),
                'link_alt': clean_value(row.get('link_alt', '')),
                'file_path': pdf_path,
                'file_found': pdf_path is not None,
                'processing_status': 'pending',
                'created_at': datetime.utcnow().isoformat(),
                'updated_at': datetime.utcnow().isoformat()
            }
            
            mongodb_docs.append(doc)
            
        except Exception as e:
            logger.error(f"Error processing row {index + 1}: {e}")
            continue
    
    # Save to JSON file
    output_file = "data/processed/mongodb_papers_clean.json"
    Path(output_file).parent.mkdir(parents=True, exist_ok=True)
    
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(mongodb_docs, f, indent=2, ensure_ascii=False)
    
    logger.info(f"Successfully created MongoDB JSON with {len(mongodb_docs)} papers")
    logger.info(f"Saved to: {output_file}")
    
    # Generate summary
    papers_with_files = len([d for d in mongodb_docs if d['file_found']])
    logger.info(f"Papers with PDF files: {papers_with_files}/{len(mongodb_docs)} ({papers_with_files/len(mongodb_docs)*100:.1f}%)")
    
    # Show sample document
    if mongodb_docs:
        logger.info("Sample document:")
        sample = mongodb_docs[0]
        for key, value in sample.items():
            if key not in ['created_at', 'updated_at']:
                logger.info(f"  {key}: {value}")


if __name__ == "__main__":
    main() 