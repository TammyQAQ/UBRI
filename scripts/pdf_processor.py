"""
PDF processing utilities for extracting text from research papers.
"""
import logging
from pathlib import Path
from typing import List, Dict, Optional, Tuple
import PyPDF2
import pdfplumber
from pymongo import MongoClient


logger = logging.getLogger(__name__)


class PDFProcessor:
    """Handles PDF text extraction and processing."""
    
    def __init__(self):
        self.supported_extensions = {'.pdf'}
    
    def extract_text_from_pdf(self, pdf_path: Path) -> Dict[str, any]:
        """
        Extract text and metadata from a PDF file.
        
        Args:
            pdf_path: Path to the PDF file
            
        Returns:
            Dictionary containing extracted text and metadata
        """
        if not pdf_path.exists():
            raise FileNotFoundError(f"PDF file not found: {pdf_path}")
        
        if pdf_path.suffix.lower() not in self.supported_extensions:
            raise ValueError(f"Unsupported file type: {pdf_path.suffix}")
        
        logger.info(f"Processing PDF: {pdf_path.name}")
        
        try:
            # Extract text using pdfplumber (better for complex layouts)
            text_content = self._extract_with_pdfplumber(pdf_path)
            
            # Extract metadata using PyPDF2
            metadata = self._extract_metadata(pdf_path)
            
            # Combine results
            result = {
                'text': text_content,
                'metadata': metadata,
                'file_path': str(pdf_path),
                'file_size': pdf_path.stat().st_size,
                'pages': len(text_content) if isinstance(text_content, list) else 1
            }
            
            logger.info(f"Successfully processed {pdf_path.name}: {result['pages']} pages")
            return result
            
        except Exception as e:
            logger.error(f"Failed to process {pdf_path.name}: {e}")
            raise
    
    def _extract_with_pdfplumber(self, pdf_path: Path) -> List[str]:
        """Extract text from PDF using pdfplumber."""
        pages_text = []
        
        with pdfplumber.open(pdf_path) as pdf:
            for page_num, page in enumerate(pdf.pages):
                try:
                    # Extract text from the page
                    text = page.extract_text()
                    if text:
                        pages_text.append(text.strip())
                    else:
                        logger.warning(f"No text extracted from page {page_num + 1}")
                        pages_text.append("")
                        
                except Exception as e:
                    logger.warning(f"Error extracting text from page {page_num + 1}: {e}")
                    pages_text.append("")
        
        return pages_text
    
    def _extract_metadata(self, pdf_path: Path) -> Dict[str, any]:
        """Extract metadata from PDF using PyPDF2."""
        metadata = {}
        
        try:
            with open(pdf_path, 'rb') as file:
                pdf_reader = PyPDF2.PdfReader(file)
                
                # Get document info
                if pdf_reader.metadata:
                    info = pdf_reader.metadata
                    metadata.update({
                        'title': info.get('/Title', ''),
                        'author': info.get('/Author', ''),
                        'subject': info.get('/Subject', ''),
                        'creator': info.get('/Creator', ''),
                        'producer': info.get('/Producer', ''),
                        'creation_date': info.get('/CreationDate', ''),
                        'modification_date': info.get('/ModDate', '')
                    })
                
                # Get number of pages
                metadata['num_pages'] = len(pdf_reader.pages)
                
        except Exception as e:
            logger.warning(f"Failed to extract metadata: {e}")
        
        return metadata
    
    def clean_text(self, text: str) -> str:
        """
        Clean extracted text by removing artifacts and normalizing.
        
        Args:
            text: Raw extracted text
            
        Returns:
            Cleaned text
        """
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
    
    def split_into_chunks(self, text: str, chunk_size: int = 1000, overlap: int = 200) -> List[str]:
        """
        Split text into overlapping chunks.
        
        Args:
            text: Text to split
            chunk_size: Maximum size of each chunk
            overlap: Number of characters to overlap between chunks
            
        Returns:
            List of text chunks
        """
        if len(text) <= chunk_size:
            return [text]
        
        chunks = []
        start = 0
        
        while start < len(text):
            end = start + chunk_size
            
            # Try to break at sentence boundary
            if end < len(text):
                # Look for sentence endings
                for i in range(end, max(start + chunk_size - 100, start), -1):
                    if text[i] in '.!?':
                        end = i + 1
                        break
            
            chunk = text[start:end].strip()
            if chunk:
                chunks.append(chunk)
            
            # Move start position with overlap
            start = end - overlap
            if start >= len(text):
                break
        
        return chunks
    
    def extract_sections(self, pages_text: List[str]) -> Dict[str, str]:
        """
        Attempt to identify and extract common paper sections.
        
        Args:
            pages_text: List of text from each page
            
        Returns:
            Dictionary mapping section names to text content
        """
        full_text = '\n'.join(pages_text)
        sections = {}
        
        # Common section headers
        section_patterns = {
            'abstract': r'(?i)(abstract|summary)',
            'introduction': r'(?i)(introduction|intro)',
            'methods': r'(?i)(methods|methodology|materials and methods)',
            'results': r'(?i)(results|findings)',
            'discussion': r'(?i)(discussion|conclusion)',
            'references': r'(?i)(references|bibliography|citations)'
        }
        
        # Simple section extraction (can be enhanced with regex)
        lines = full_text.split('\n')
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


# Global processor instance
pdf_processor = PDFProcessor() 

client = MongoClient("mongodb+srv://yitianw:2T9KEjQqvMBSZ68Y@cluster0.jvwt789.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0")
db = client["UBRI_Publication"]
collection = db["Papers"]
result = collection.insert_one({"test": "hello"})
print("Inserted:", result.inserted_id)
print(list(collection.find())) 