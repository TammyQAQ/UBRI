#!/usr/bin/env python3
"""
Improved UBRI Paper Classification System

This script:
1. Reads Excel files directly using pandas
2. Assigns papers to 3 most relevant categories
3. Creates new categories for papers that don't fit existing ones
4. Reads abstracts for better understanding
5. Provides more granular categorization
"""

import os
import json
import pandas as pd
import openai
from datetime import datetime
import time
from typing import List, Dict, Any, Tuple
import logging

# Setup logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Initialize OpenAI client
client = openai.OpenAI(api_key=os.getenv('OPENAI_API_KEY'))

# Base categories - these will be expanded based on paper content
BASE_CATEGORIES = [
    "DeFi (Decentralized Finance)",
    "Cryptocurrency Economics & Market Analysis", 
    "Stablecoins & CBDCs",
    "RWA (Real World Assets)",
    "Smart Contract Security & Vulnerabilities",
    "Consensus Mechanisms & Protocols",
    "Zero-Knowledge Proofs & Privacy",
    "Scalability & Performance Optimization",
    "Cross-Chain & Interoperability",
    "Network Analysis & Graph Theory",
    "Game Theory & Mechanism Design",
    "Regulation & Legal Analysis",
    "Security & Cryptography",
    "Energy & Sustainability",
    "Healthcare & Digital Health",
    "Supply Chain & Logistics",
    "Governance & DAOs",
    "FinTech & Traditional Finance",
    "Machine Learning & AI Applications",
    "IoT & Edge Computing",
    "Metaverse & Virtual Reality",
    "Digital Identity & Authentication",
    "Tokenomics & Token Design",
    "Blockchain Infrastructure & Development",
    "Academic Research & Methodology"
]

def read_excel_data(excel_file_path: str) -> List[Dict[str, Any]]:
    """
    Read Excel file and extract paper information
    """
    try:
        logger.info(f"Reading Excel file: {excel_file_path}")
        df = pd.read_excel(excel_file_path)
        
        papers = []
        for index, row in df.iterrows():
            # Handle both 'Author' and 'Authors' column names
            author_col = 'Author' if 'Author' in row else 'Authors' if 'Authors' in row else None
            authors = str(row.get(author_col, '')).strip() if author_col else ''
            
            # Use the actual row number from Excel as paper ID
            paper_id = str(row.get('No', index + 1)) if pd.notna(row.get('No')) else str(index + 1)
            
            paper = {
                'paper_id': paper_id,
                'excel_row': index + 1,  # Keep track of Excel row for reference
                'title': str(row.get('Title', '')).strip(),
                'authors': authors,
                'university': str(row.get('University', '')).strip(),
                'year': row.get('Year', None),
                'abstract': str(row.get('Abstract', '')).strip(),
                'keywords': str(row.get('Keywords', '')).strip(),
                'doi': str(row.get('DOI', '')).strip(),
                'journal': str(row.get('Journal', '')).strip()
            }
            
            # Only include papers with titles
            if paper['title'] and paper['title'] != 'nan':
                papers.append(paper)
        
        logger.info(f"Successfully read {len(papers)} papers from Excel file")
        return papers
        
    except Exception as e:
        logger.error(f"Error reading Excel file: {e}")
        return []

def classify_paper_with_llm(paper: Dict[str, Any], existing_categories: List[str]) -> Dict[str, Any]:
    """
    Use LLM to classify a paper into 3 most relevant categories
    """
    
    # Prepare paper information for classification
    paper_info = f"""
Title: {paper['title']}
Authors: {paper['authors']}
University: {paper['university']}
Year: {paper['year']}
Abstract: {paper['abstract']}
Keywords: {paper['keywords']}
"""
    
    prompt = f"""
Classify this blockchain research paper into 3 categories:

EXISTING CATEGORIES:
{chr(10).join([f"{i+1}. {cat}" for i, cat in enumerate(existing_categories)])}

PAPER:
{paper_info}

Respond ONLY with valid JSON:
{{
    "is_blockchain_related": true/false,
    "primary_category": "category_name",
    "secondary_category": "category_name", 
    "tertiary_category": "category_name",
    "confidence_levels": {{
        "primary": "high/medium/low",
        "secondary": "high/medium/low",
        "tertiary": "high/medium/low"
    }},
    "new_categories_suggested": [],
    "reasoning": "brief explanation"
}}
"""

    try:
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.1,
            max_tokens=1000
        )
        
        content = response.choices[0].message.content.strip()
        if not content:
            raise ValueError("Empty response from LLM")
        
        # Clean up the response - remove markdown formatting if present
        if content.startswith('```json'):
            content = content[7:]
        if content.endswith('```'):
            content = content[:-3]
        content = content.strip()
        
        result = json.loads(content)
        
        # Add paper metadata to result
        result['paper_id'] = paper['paper_id']
        result['title'] = paper['title']
        result['authors'] = paper['authors']
        result['university'] = paper['university']
        result['year'] = paper['year']
        
        return result
        
    except Exception as e:
        logger.error(f"Error classifying paper {paper['paper_id']}: {e}")
        # Log the actual response for debugging
        try:
            content = response.choices[0].message.content if 'response' in locals() else "No response"
            logger.error(f"LLM response: {content}")
        except:
            pass
        return {
            'paper_id': paper['paper_id'],
            'title': paper['title'],
            'authors': paper['authors'],
            'university': paper['university'],
            'year': paper['year'],
            'is_blockchain_related': False,
            'primary_category': 'Classification Error',
            'secondary_category': 'Classification Error',
            'tertiary_category': 'Classification Error',
            'confidence_levels': {'primary': 'low', 'secondary': 'low', 'tertiary': 'low'},
            'new_categories_suggested': [],
            'reasoning': f'Error during classification: {str(e)}'
        }

def process_papers_batch(papers: List[Dict[str, Any]], batch_size: int = 10) -> List[Dict[str, Any]]:
    """
    Process papers in batches to avoid rate limits
    """
    all_results = []
    categories = BASE_CATEGORIES.copy()
    new_categories = set()
    
    for i in range(0, len(papers), batch_size):
        batch = papers[i:i + batch_size]
        logger.info(f"Processing batch {i//batch_size + 1}/{(len(papers) + batch_size - 1)//batch_size}")
        
        batch_results = []
        for paper in batch:
            result = classify_paper_with_llm(paper, categories)
            batch_results.append(result)
            
            # Add new categories if suggested
            for new_cat in result.get('new_categories_suggested', []):
                if new_cat not in categories:
                    new_categories.add(new_cat)
                    categories.append(new_cat)
            
            # Rate limiting
            time.sleep(1)
        
        all_results.extend(batch_results)
        
        # Log progress
        logger.info(f"Completed batch {i//batch_size + 1}/{(len(papers) + batch_size - 1)//batch_size} - {len(all_results)} papers processed")
        
        # Save backup every 10 batches (optional - for safety)
        if (i//batch_size + 1) % 10 == 0:
            backup_dir = "backup"
            os.makedirs(backup_dir, exist_ok=True)
            backup_file = os.path.join(backup_dir, f"backup_batch_{i//batch_size + 1}.json")
            save_results(all_results, categories, backup_file)
            logger.info(f"Backup saved to {backup_file}")
        
        # Longer pause between batches
        time.sleep(5)
    
    return all_results, list(new_categories)

def save_results(results: List[Dict[str, Any]], categories: List[str], filename: str = None):
    """
    Save classification results to JSON file
    """
    if filename is None:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"ubri_paper_classifications_{timestamp}.json"
    
    # Calculate statistics
    blockchain_related = [r for r in results if r.get('is_blockchain_related', False)]
    not_blockchain = [r for r in results if not r.get('is_blockchain_related', False)]
    
    # Category distribution
    category_counts = {}
    for result in blockchain_related:
        for cat in [result.get('primary_category'), result.get('secondary_category'), result.get('tertiary_category')]:
            if cat and cat != 'Not Blockchain Related':
                category_counts[cat] = category_counts.get(cat, 0) + 1
    
    # University distribution
    university_counts = {}
    for result in results:
        uni = result.get('university', 'Unknown')
        university_counts[uni] = university_counts.get(uni, 0) + 1
    
    output = {
        "summary": {
            "total_papers_processed": len(results),
            "blockchain_related_papers": len(blockchain_related),
            "not_blockchain_papers": len(not_blockchain),
            "classification_timestamp": datetime.now().isoformat(),
            "categories_used": categories,
            "category_distribution": category_counts,
            "university_distribution": university_counts,
            "years_covered": sorted(list(set([r.get('year') for r in results if r.get('year')])))
        },
        "classified_papers": results
    }
    
    filepath = filename
    with open(filepath, 'w', encoding='utf-8') as f:
        json.dump(output, f, indent=2, ensure_ascii=False)
    
    logger.info(f"Results saved to {filepath}")
    return filepath

def generate_summary_report(results_file: str):
    """
    Generate a human-readable summary report
    """
    with open(results_file, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    summary = data['summary']
    papers = data['classified_papers']
    
    report = f"""IMPROVED UBRI Paper Classification Summary Report
{'='*60}

Total Papers Processed: {summary['total_papers_processed']}
Blockchain Related Papers: {summary['blockchain_related_papers']}
Not Blockchain Related: {summary['not_blockchain_papers']}
Classification Date: {summary['classification_timestamp']}
Categories Used: {len(summary['categories_used'])}
Years Covered: {summary['years_covered']}

CATEGORY DISTRIBUTION (Top 15):
{'-'*40}
"""
    
    # Sort categories by count
    sorted_categories = sorted(summary['category_distribution'].items(), 
                             key=lambda x: x[1], reverse=True)
    
    for i, (category, count) in enumerate(sorted_categories[:15]):
        percentage = (count / summary['blockchain_related_papers']) * 100
        report += f"{i+1:2d}. {category}: {count} papers ({percentage:.1f}%)\n"
    
    report += f"""
TOP UNIVERSITIES (Top 10):
{'-'*30}
"""
    
    sorted_universities = sorted(summary['university_distribution'].items(), 
                               key=lambda x: x[1], reverse=True)
    
    for i, (university, count) in enumerate(sorted_universities[:10]):
        report += f"{i+1:2d}. {university}: {count} papers\n"
    
    report += f"""
SAMPLE PAPERS BY CATEGORY:
{'-'*30}
"""
    
    # Group papers by primary category
    papers_by_category = {}
    for paper in papers:
        if paper.get('is_blockchain_related', False):
            primary_cat = paper.get('primary_category', 'Unknown')
            if primary_cat not in papers_by_category:
                papers_by_category[primary_cat] = []
            papers_by_category[primary_cat].append(paper)
    
    # Show sample papers for top categories
    for category, count in sorted_categories[:10]:
        report += f"\n{category}:\n"
        category_papers = papers_by_category.get(category, [])
        for i, paper in enumerate(category_papers[:3]):  # Show first 3 papers
            report += f"  - {paper['title']} ({paper['university']})\n"
    
    # Save report
    report_file = results_file.replace('.json', '_summary.txt')
    with open(report_file, 'w', encoding='utf-8') as f:
        f.write(report)
    
    logger.info(f"Summary report saved to {report_file}")
    return report_file

def main():
    """
    Main function to run the improved classification
    """
    # Check for Excel files
    excel_files = [
        "../data/raw/Publications/UBRI Publications .xlsx",
        "../data/raw/Publications/UBRI Publication Highlights - External Share.xlsx",
        "../data/raw/Publications/Related paper for the Optimizing Liquidity Incentives for Performance on the XRP Ledger DEX_2025.xlsx"
    ]
    
    excel_file = None
    for file_path in excel_files:
        if os.path.exists(file_path):
            excel_file = file_path
            break
    
    if not excel_file:
        logger.error("No Excel file found. Please place your updated Excel file in data/raw/Publications/")
        return
    
    logger.info(f"Using Excel file: {excel_file}")
    
    # Read papers from Excel
    papers = read_excel_data(excel_file)
    
    if not papers:
        logger.error("No papers found in Excel file")
        return
    
    logger.info(f"Found {len(papers)} papers to classify")
    
    # Process papers in batches
    results, new_categories = process_papers_batch(papers, batch_size=5)
    
    # Save final results
    results_file = save_results(results, BASE_CATEGORIES + new_categories)
    
    # Generate summary report
    summary_file = generate_summary_report(results_file)
    
    logger.info("Classification completed successfully!")
    logger.info(f"Results saved to: {results_file}")
    logger.info(f"Summary saved to: {summary_file}")
    logger.info(f"New categories created: {new_categories}")

if __name__ == "__main__":
    main() 