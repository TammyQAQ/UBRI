#!/usr/bin/env python3
"""
Process Excel index file and convert to MongoDB format for UBRI publications.
"""
import pandas as pd
import json
import os
from pathlib import Path
from typing import List, Dict, Any, Optional
import logging
from datetime import datetime
import re

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class ExcelIndexProcessor:
    """Process Excel index file and convert to MongoDB format."""
    
    def __init__(self, excel_file: str = "data/raw/Publications/UBRI Publications_.xlsx"):
        self.excel_file = Path(excel_file)
        self.publications_dir = Path("data/raw/Publications")
        self.processed_data = []
        
    def read_excel_file(self) -> pd.DataFrame:
        """Read the Excel file and return as DataFrame."""
        try:
            logger.info(f"Reading Excel file: {self.excel_file}")
            
            # Read Excel file - try different sheet names if needed
            try:
                df = pd.read_excel(self.excel_file)
            except Exception as e:
                logger.warning(f"Failed to read with default settings: {e}")
                # Try reading with different parameters
                df = pd.read_excel(self.excel_file, sheet_name=0)
            
            logger.info(f"Successfully read Excel file with {len(df)} rows and {len(df.columns)} columns")
            logger.info(f"Columns: {list(df.columns)}")
            
            return df
            
        except Exception as e:
            logger.error(f"Failed to read Excel file: {e}")
            raise
    
    def clean_column_names(self, df: pd.DataFrame) -> pd.DataFrame:
        """Clean and standardize column names."""
        # Create a mapping of common column name variations
        column_mapping = {
            'Title': 'title',
            'Authors': 'authors',
            'Author': 'authors',
            'Year': 'year',
            'Publication Year': 'year',
            'Journal': 'journal',
            'Publication': 'journal',
            'Venue': 'journal',
            'DOI': 'doi',
            'Abstract': 'abstract',
            'Keywords': 'keywords',
            'University': 'university',
            'Institution': 'university',
            'Category': 'category',
            'Type': 'type',
            'Type of publication': 'type',
            'Status': 'status',
            'File Path': 'file_path',
            'Filename': 'filename',
            'Quality': 'quality',
            'Relevance': 'relevance',
            'Discipline': 'discipline',
            'Comment': 'comment',
            'Link': 'link',
            'Link.1': 'link_alt'
        }
        
        # Clean column names
        df.columns = df.columns.str.strip()
        
        # Apply mapping
        for old_name, new_name in column_mapping.items():
            if old_name in df.columns:
                df = df.rename(columns={old_name: new_name})
        
        return df
    
    def clean_data(self, df: pd.DataFrame) -> pd.DataFrame:
        """Clean and validate the data."""
        # Remove completely empty rows
        df = df.dropna(how='all')
        
        logger.info(f"DataFrame columns after cleaning: {list(df.columns)}")
        
        # Get all string columns that exist in the dataframe
        string_columns = []
        for col in ['title', 'authors', 'journal', 'doi', 'abstract', 'keywords', 'university', 'category', 'type', 'quality', 'relevance', 'discipline', 'comment', 'link', 'link_alt']:
            if col in df.columns:
                string_columns.append(col)
        
        logger.info(f"String columns found: {string_columns}")
        
        # Fill NaN values for each column individually to avoid issues
        for col in string_columns:
            if col in df.columns:
                df[col] = df[col].fillna('')
        
        if 'year' in df.columns:
            df['year'] = df['year'].fillna(pd.NA)
        
        if 'status' in df.columns:
            df['status'] = df['status'].fillna('pending')
        
        # Clean string columns
        for col in string_columns:
            if col in df.columns:
                df[col] = df[col].astype(str).str.strip()
        
        # Convert year to integer if possible
        if 'year' in df.columns:
            df['year'] = pd.to_numeric(df['year'], errors='coerce').astype('Int64')
        
        return df
    
    def find_pdf_file(self, title: str, university: str = "") -> Optional[str]:
        """
        Find the corresponding PDF file for a paper.
        
        Args:
            title: Paper title
            university: University name (optional)
            
        Returns:
            Path to PDF file if found, None otherwise
        """
        # Clean title for filename matching
        clean_title = re.sub(r'[^\w\s-]', '', title.lower())
        clean_title = re.sub(r'[-\s]+', '_', clean_title)
        
        # Search in university-specific directories first
        if university:
            university_dir = self.publications_dir / university
            if university_dir.exists():
                for pdf_file in university_dir.rglob("*.pdf"):
                    if self._title_matches_file(title, pdf_file.name):
                        return str(pdf_file)
        
        # Search in all subdirectories
        for pdf_file in self.publications_dir.rglob("*.pdf"):
            if self._title_matches_file(title, pdf_file.name):
                return str(pdf_file)
        
        return None
    
    def _title_matches_file(self, title: str, filename: str) -> bool:
        """Check if title matches filename."""
        # Remove file extension
        filename_no_ext = Path(filename).stem.lower()
        
        # Clean title
        clean_title = re.sub(r'[^\w\s]', '', title.lower())
        
        # Check for common words
        title_words = set(clean_title.split())
        filename_words = set(filename_no_ext.split('_'))
        
        # Check if there's significant overlap
        common_words = title_words.intersection(filename_words)
        if len(common_words) >= min(3, len(title_words) // 2):
            return True
        
        return False
    
    def convert_to_mongodb_format(self, df: pd.DataFrame) -> List[Dict[str, Any]]:
        """Convert DataFrame to MongoDB document format."""
        mongodb_docs = []
        
        for index, row in df.iterrows():
            try:
                # Find corresponding PDF file
                pdf_path = self.find_pdf_file(row.get('title', ''), row.get('university', ''))
                
                # Create MongoDB document
                doc = {
                    '_id': f"paper_{index + 1}",  # Generate unique ID
                    'title': row.get('title', ''),
                    'authors': self._parse_authors(row.get('authors', '')),
                    'year': int(row.get('year')) if pd.notna(row.get('year')) else None,
                    'journal': row.get('journal', ''),
                    'venue': row.get('journal', ''),  # Keep original venue field
                    'doi': row.get('doi', ''),
                    'abstract': row.get('abstract', ''),
                    'keywords': self._parse_keywords(row.get('keywords', '')),
                    'university': row.get('university', ''),
                    'category': row.get('category', ''),
                    'type': row.get('type', ''),
                    'quality': row.get('quality', ''),
                    'relevance': row.get('relevance', ''),
                    'discipline': row.get('discipline', ''),
                    'comment': row.get('comment', ''),
                    'link': row.get('link', ''),
                    'link_alt': row.get('link_alt', ''),
                    'file_path': pdf_path,
                    'file_found': pdf_path is not None,
                    'processing_status': 'pending',
                    'created_at': datetime.utcnow().isoformat(),
                    'updated_at': datetime.utcnow().isoformat(),
                    'metadata': {
                        'excel_row': index + 1,
                        'source_file': str(self.excel_file),
                        'original_data': row.to_dict()
                    }
                }
                
                mongodb_docs.append(doc)
                
            except Exception as e:
                logger.error(f"Error processing row {index + 1}: {e}")
                continue
        
        return mongodb_docs
    
    def _parse_authors(self, authors_str: str) -> List[str]:
        """Parse authors string into list of authors."""
        if not authors_str or authors_str == 'nan':
            return []
        
        # Common separators
        separators = [';', ',', ' and ', ' & ']
        
        for sep in separators:
            if sep in authors_str:
                authors = [author.strip() for author in authors_str.split(sep)]
                return [author for author in authors if author]
        
        # If no separator found, return as single author
        return [authors_str.strip()] if authors_str.strip() else []
    
    def _parse_keywords(self, keywords_str: str) -> List[str]:
        """Parse keywords string into list of keywords."""
        if not keywords_str or keywords_str == 'nan':
            return []
        
        # Common separators for keywords
        separators = [';', ',', '|']
        
        for sep in separators:
            if sep in keywords_str:
                keywords = [keyword.strip() for keyword in keywords_str.split(sep)]
                return [keyword for keyword in keywords if keyword]
        
        # If no separator found, return as single keyword
        return [keywords_str.strip()] if keywords_str.strip() else []
    
    def process_index(self) -> List[Dict[str, Any]]:
        """Main processing function."""
        logger.info("Starting Excel index processing")
        
        # Read Excel file
        df = self.read_excel_file()
        
        # Clean column names
        df = self.clean_column_names(df)
        
        # Clean data
        df = self.clean_data(df)
        
        # Convert to MongoDB format
        mongodb_docs = self.convert_to_mongodb_format(df)
        
        self.processed_data = mongodb_docs
        
        logger.info(f"Successfully processed {len(mongodb_docs)} papers")
        
        return mongodb_docs
    
    def save_to_json(self, output_file: str = "data/processed/mongodb_papers.json"):
        """Save processed data to JSON file."""
        output_path = Path(output_file)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        
        try:
            with open(output_path, 'w', encoding='utf-8') as f:
                json.dump(self.processed_data, f, indent=2, ensure_ascii=False)
            
            logger.info(f"Data saved to: {output_path}")
            
        except Exception as e:
            logger.error(f"Failed to save data: {e}")
    
    def generate_summary(self) -> Dict[str, Any]:
        """Generate processing summary."""
        total_papers = len(self.processed_data)
        papers_with_files = len([p for p in self.processed_data if p.get('file_found')])
        papers_without_files = total_papers - papers_with_files
        
        # Count by university
        universities = {}
        for paper in self.processed_data:
            university = paper.get('university', 'Unknown')
            universities[university] = universities.get(university, 0) + 1
        
        # Count by year
        years = {}
        for paper in self.processed_data:
            year = paper.get('year')
            if year:
                years[year] = years.get(year, 0) + 1
        
        summary = {
            'total_papers': total_papers,
            'papers_with_pdf_files': papers_with_files,
            'papers_without_pdf_files': papers_without_files,
            'file_coverage_percentage': round((papers_with_files / total_papers) * 100, 2) if total_papers > 0 else 0,
            'universities': universities,
            'years': dict(sorted(years.items())),
            'processing_timestamp': datetime.utcnow().isoformat()
        }
        
        logger.info(f"Processing Summary: {summary}")
        return summary


def main():
    """Main function to run the Excel index processing."""
    logger.info("Starting UBRI Excel Index Processing")
    
    # Initialize processor
    processor = ExcelIndexProcessor()
    
    # Process the index
    papers = processor.process_index()
    
    # Save results
    processor.save_to_json()
    
    # Generate summary
    summary = processor.generate_summary()
    
    # Save summary
    summary_path = Path("data/processed/processing_summary.json")
    summary_path.parent.mkdir(parents=True, exist_ok=True)
    with open(summary_path, 'w', encoding='utf-8') as f:
        json.dump(summary, f, indent=2, ensure_ascii=False)
    
    logger.info("Excel index processing completed!")
    logger.info(f"Summary: {summary}")


if __name__ == "__main__":
    main() 