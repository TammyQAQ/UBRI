#!/usr/bin/env python3
"""
Extract PDF content (text, tables, basic metadata) for MongoDB storage.
Simplified version without heavy image processing dependencies.
"""
import json
import logging
import os
from pathlib import Path
from typing import List, Dict, Any, Optional
import pdfplumber
from datetime import datetime
import re

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class SimplePDFContentExtractor:
    """Extract text content and tables from PDF files."""
    
    def __init__(self, output_dir: str = "data/processed"):
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)
        
    def extract_pdf_content(self, pdf_path: str) -> Dict[str, Any]:
        """
        Extract content from a PDF file.
        
        Args:
            pdf_path: Path to the PDF file
            
        Returns:
            Dictionary containing extracted content
        """
        pdf_path = Path(pdf_path)
        if not pdf_path.exists():
            logger.error(f"PDF file not found: {pdf_path}")
            return None
        
        logger.info(f"Processing PDF: {pdf_path.name}")
        
        try:
            # Extract text content
            text_content = self._extract_text_content(pdf_path)
            
            # Extract tables
            tables_content = self._extract_tables(pdf_path)
            
            # Extract basic metadata
            metadata = self._extract_basic_metadata(pdf_path)
            
            # Process content into chunks
            text_chunks = self._create_text_chunks(text_content['full_text'])
            
            # Create comprehensive result
            result = {
                'file_path': str(pdf_path),
                'file_name': pdf_path.name,
                'file_size': pdf_path.stat().st_size,
                'extraction_timestamp': datetime.utcnow().isoformat(),
                'metadata': metadata,
                'text_content': text_content,
                'tables': tables_content,
                'text_chunks': text_chunks,
                'summary': {
                    'total_pages': metadata.get('num_pages', 0),
                    'total_tables': len(tables_content),
                    'total_chunks': len(text_chunks),
                    'total_words': len(text_content['full_text'].split()),
                    'extraction_success': True
                }
            }
            
            logger.info(f"Successfully extracted content from {pdf_path.name}")
            return result
            
        except Exception as e:
            logger.error(f"Failed to extract content from {pdf_path.name}: {e}")
            return {
                'file_path': str(pdf_path),
                'file_name': pdf_path.name,
                'extraction_timestamp': datetime.utcnow().isoformat(),
                'extraction_success': False,
                'error': str(e)
            }
    
    def _extract_text_content(self, pdf_path: Path) -> Dict[str, Any]:
        """Extract text content from PDF."""
        text_content = {
            'full_text': '',
            'pages_text': [],
            'sections': {},
            'page_summaries': []
        }
        
        try:
            with pdfplumber.open(pdf_path) as pdf:
                for page_num, page in enumerate(pdf.pages):
                    page_text = page.extract_text()
                    if page_text:
                        page_data = {
                            'page_number': page_num + 1,
                            'text': page_text.strip(),
                            'word_count': len(page_text.split()),
                            'char_count': len(page_text)
                        }
                        text_content['pages_text'].append(page_data)
                        text_content['full_text'] += page_text + '\n'
                        
                        # Create page summary
                        page_summary = {
                            'page_number': page_num + 1,
                            'word_count': len(page_text.split()),
                            'char_count': len(page_text),
                            'first_sentence': self._get_first_sentence(page_text),
                            'has_figures': 'figure' in page_text.lower() or 'fig.' in page_text.lower(),
                            'has_tables': 'table' in page_text.lower() or 'tab.' in page_text.lower()
                        }
                        text_content['page_summaries'].append(page_summary)
            
            # Extract sections
            text_content['sections'] = self._extract_sections(text_content['full_text'])
            
            # Clean text
            text_content['full_text'] = self._clean_text(text_content['full_text'])
            
        except Exception as e:
            logger.warning(f"Error extracting text from {pdf_path.name}: {e}")
        
        return text_content
    
    def _extract_tables(self, pdf_path: Path) -> List[Dict[str, Any]]:
        """Extract tables from PDF."""
        tables = []
        
        try:
            with pdfplumber.open(pdf_path) as pdf:
                for page_num, page in enumerate(pdf.pages):
                    page_tables = page.extract_tables()
                    
                    for table_index, table in enumerate(page_tables):
                        if table and any(any(cell for cell in row) for row in table):
                            # Clean table data
                            cleaned_table = []
                            for row in table:
                                cleaned_row = [str(cell).strip() if cell else '' for cell in row]
                                cleaned_table.append(cleaned_row)
                            
                            table_data = {
                                'table_id': f"table_{page_num + 1}_{table_index + 1}",
                                'page_number': page_num + 1,
                                'table_index': table_index + 1,
                                'data': cleaned_table,
                                'rows': len(cleaned_table),
                                'columns': len(cleaned_table[0]) if cleaned_table else 0,
                                'extraction_timestamp': datetime.utcnow().isoformat()
                            }
                            
                            tables.append(table_data)
            
        except Exception as e:
            logger.warning(f"Error extracting tables from {pdf_path.name}: {e}")
        
        return tables
    
    def _extract_basic_metadata(self, pdf_path: Path) -> Dict[str, Any]:
        """Extract basic metadata from PDF."""
        metadata = {
            'file_size': pdf_path.stat().st_size,
            'file_modified': datetime.fromtimestamp(pdf_path.stat().st_mtime).isoformat()
        }
        
        try:
            with pdfplumber.open(pdf_path) as pdf:
                metadata['num_pages'] = len(pdf.pages)
                
                # Try to get document info
                if hasattr(pdf, 'metadata') and pdf.metadata:
                    metadata.update({
                        'title': pdf.metadata.get('Title', ''),
                        'author': pdf.metadata.get('Author', ''),
                        'subject': pdf.metadata.get('Subject', ''),
                        'creator': pdf.metadata.get('Creator', ''),
                        'producer': pdf.metadata.get('Producer', '')
                    })
            
        except Exception as e:
            logger.warning(f"Error extracting metadata from {pdf_path.name}: {e}")
        
        return metadata
    
    def _extract_sections(self, text: str) -> Dict[str, str]:
        """Extract document sections."""
        sections = {}
        
        # Common section headers
        section_patterns = {
            'abstract': r'(?i)(abstract|summary)',
            'introduction': r'(?i)(introduction|intro)',
            'methods': r'(?i)(methods|methodology|materials and methods)',
            'results': r'(?i)(results|findings)',
            'discussion': r'(?i)(discussion|conclusion)',
            'references': r'(?i)(references|bibliography|citations)',
            'appendix': r'(?i)(appendix|appendices)'
        }
        
        lines = text.split('\n')
        current_section = 'unknown'
        current_content = []
        
        for line in lines:
            line_lower = line.lower().strip()
            
            # Check if line contains section header
            for section_name, pattern in section_patterns.items():
                if any(keyword in line_lower for keyword in pattern.split('|')):
                    if current_content:
                        sections[current_section] = '\n'.join(current_content).strip()
                    current_section = section_name
                    current_content = []
                    break
            else:
                current_content.append(line)
        
        # Add the last section
        if current_content:
            sections[current_section] = '\n'.join(current_content).strip()
        
        return sections
    
    def _clean_text(self, text: str) -> str:
        """Clean extracted text."""
        if not text:
            return ""
        
        # Remove excessive whitespace
        text = ' '.join(text.split())
        
        # Remove common PDF artifacts
        text = text.replace('\x00', '')  # Null characters
        text = text.replace('\x0c', ' ')  # Form feed
        text = text.replace('\x0b', ' ')  # Vertical tab
        
        # Normalize quotes and dashes
        text = text.replace('"', '"').replace('"', '"')
        text = text.replace('–', '-').replace('—', '-')
        
        return text.strip()
    
    def _get_first_sentence(self, text: str) -> str:
        """Get the first sentence from text."""
        if not text:
            return ""
        
        # Find first sentence ending
        for i, char in enumerate(text):
            if char in '.!?':
                return text[:i+1].strip()
        
        return text[:100].strip() + "..." if len(text) > 100 else text.strip()
    
    def _create_text_chunks(self, text: str, chunk_size: int = 1000, overlap: int = 200) -> List[Dict[str, Any]]:
        """Create text chunks for vector processing."""
        if not text or len(text) <= chunk_size:
            return [{
                'chunk_id': 'chunk_1',
                'text': text,
                'start_char': 0,
                'end_char': len(text),
                'word_count': len(text.split()),
                'chunk_index': 1
            }]
        
        chunks = []
        start = 0
        chunk_index = 1
        
        while start < len(text):
            end = start + chunk_size
            
            # Try to break at sentence boundary
            if end < len(text):
                for i in range(end, max(start + chunk_size - 100, start), -1):
                    if text[i] in '.!?':
                        end = i + 1
                        break
            
            chunk_text = text[start:end].strip()
            if chunk_text:
                chunk = {
                    'chunk_id': f'chunk_{chunk_index}',
                    'text': chunk_text,
                    'start_char': start,
                    'end_char': end,
                    'word_count': len(chunk_text.split()),
                    'chunk_index': chunk_index
                }
                chunks.append(chunk)
                chunk_index += 1
            
            # Move start position with overlap
            start = end - overlap
            if start >= len(text):
                break
        
        return chunks
    
    def process_papers_from_json(self, json_file: str = "data/processed/mongodb_papers_clean.json") -> None:
        """Process all papers from the JSON index."""
        logger.info(f"Processing papers from: {json_file}")
        
        # Load the papers index
        with open(json_file, 'r', encoding='utf-8') as f:
            papers = json.load(f)
        
        processed_papers = []
        successful_extractions = 0
        failed_extractions = 0
        
        for i, paper in enumerate(papers):
            if paper.get('file_found') and paper.get('file_path'):
                logger.info(f"Processing paper {i+1}/{len(papers)}: {paper['title'][:50]}...")
                
                # Extract content
                content = self.extract_pdf_content(paper['file_path'])
                
                if content and content.get('extraction_success', False):
                    # Merge paper metadata with extracted content
                    paper_with_content = {
                        **paper,
                        'pdf_content': content,
                        'content_extracted': True,
                        'content_extraction_timestamp': datetime.utcnow().isoformat()
                    }
                    successful_extractions += 1
                else:
                    paper_with_content = {
                        **paper,
                        'pdf_content': content,
                        'content_extracted': False,
                        'content_extraction_timestamp': datetime.utcnow().isoformat()
                    }
                    failed_extractions += 1
                
                processed_papers.append(paper_with_content)
            else:
                # Paper without PDF file
                paper_with_content = {
                    **paper,
                    'pdf_content': None,
                    'content_extracted': False,
                    'content_extraction_timestamp': datetime.utcnow().isoformat()
                }
                processed_papers.append(paper_with_content)
        
        # Save processed papers
        output_file = self.output_dir / "papers_with_content.json"
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(processed_papers, f, indent=2, ensure_ascii=False)
        
        logger.info(f"Processing completed!")
        logger.info(f"Total papers: {len(processed_papers)}")
        logger.info(f"Successful extractions: {successful_extractions}")
        logger.info(f"Failed extractions: {failed_extractions}")
        logger.info(f"Output saved to: {output_file}")


def main():
    """Main function to extract PDF content."""
    logger.info("Starting PDF content extraction")
    
    extractor = SimplePDFContentExtractor()
    extractor.process_papers_from_json()
    
    logger.info("PDF content extraction completed!")


if __name__ == "__main__":
    main() 