#!/usr/bin/env python3
"""
Paper Classification Script using OpenAI API
Classifies all papers in the UBRI dataset into major topic/theme categories.
"""

import json
import os
import openai
from typing import List, Dict, Any
import time
from datetime import datetime
import logging

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class PaperClassifier:
    def __init__(self, api_key: str):
        """Initialize the classifier with OpenAI API key."""
        self.client = openai.OpenAI(api_key=api_key)
        self.classification_categories = [
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
            "Other"
        ]
    
    def classify_paper(self, paper: Dict[str, Any]) -> Dict[str, Any]:
        """Classify a single paper using OpenAI API."""
        try:
            # Prepare the paper information for classification
            title = paper.get('title', '')
            abstract = paper.get('abstract', '')
            keywords = paper.get('keywords', [])
            discipline = paper.get('discipline', '')
            
            # Create a comprehensive description for classification
            paper_info = f"Title: {title}\n"
            if abstract:
                paper_info += f"Abstract: {abstract}\n"
            if keywords:
                paper_info += f"Keywords: {', '.join(keywords)}\n"
            if discipline:
                paper_info += f"Discipline: {discipline}\n"
            
            # Create the classification prompt
            prompt = f"""
You are an expert in blockchain, cryptocurrency, and distributed systems research. 
Your task is to classify the following academic paper into ONE of the provided categories.

Available categories:
{chr(10).join([f"{i+1}. {cat}" for i, cat in enumerate(self.classification_categories)])}

Paper information:
{paper_info}

Please respond with ONLY the category number (1-20) that best fits this paper. 
If none of the categories fit well, use category 20 (Other).

Consider the main focus and contribution of the paper when making your classification.
"""

            # Make API call
            response = self.client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[
                    {"role": "system", "content": "You are a research paper classifier specializing in blockchain and cryptocurrency research."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.1,
                max_tokens=10
            )
            
            # Extract the classification
            classification_text = response.choices[0].message.content.strip()
            
            # Parse the category number
            try:
                category_num = int(classification_text)
                if 1 <= category_num <= len(self.classification_categories):
                    category = self.classification_categories[category_num - 1]
                else:
                    category = "Other"
            except ValueError:
                category = "Other"
            
            return {
                "paper_id": paper.get('_id', ''),
                "title": title,
                "authors": paper.get('authors', []),
                "university": paper.get('university', ''),
                "year": paper.get('year', ''),
                "category": category,
                "category_number": category_num if 'category_num' in locals() else 20,
                "classification_confidence": "high" if category != "Other" else "low"
            }
            
        except Exception as e:
            logger.error(f"Error classifying paper {paper.get('_id', 'unknown')}: {str(e)}")
            return {
                "paper_id": paper.get('_id', ''),
                "title": paper.get('title', ''),
                "authors": paper.get('authors', []),
                "university": paper.get('university', ''),
                "year": paper.get('year', ''),
                "category": "Error in classification",
                "category_number": 20,
                "classification_confidence": "error"
            }
    
    def classify_all_papers(self, papers_data: List[Dict[str, Any]], batch_size: int = 10) -> Dict[str, Any]:
        """Classify all papers in batches to avoid rate limits."""
        logger.info(f"Starting classification of {len(papers_data)} papers...")
        
        classified_papers = []
        category_counts = {cat: 0 for cat in self.classification_categories}
        
        for i in range(0, len(papers_data), batch_size):
            batch = papers_data[i:i + batch_size]
            logger.info(f"Processing batch {i//batch_size + 1}/{(len(papers_data) + batch_size - 1)//batch_size}")
            
            for paper in batch:
                classified_paper = self.classify_paper(paper)
                classified_papers.append(classified_paper)
                
                # Update category counts
                category = classified_paper['category']
                if category in category_counts:
                    category_counts[category] += 1
                
                # Add small delay to avoid rate limits
                time.sleep(0.5)
        
        # Create summary statistics
        summary = {
            "total_papers_classified": len(classified_papers),
            "classification_timestamp": datetime.now().isoformat(),
            "category_distribution": category_counts,
            "universities_represented": len(set(p['university'] for p in classified_papers if p['university'])),
            "years_covered": sorted(list(set(p['year'] for p in classified_papers if p['year'])))
        }
        
        return {
            "summary": summary,
            "classified_papers": classified_papers,
            "categories": self.classification_categories
        }
    
    def save_results(self, results: Dict[str, Any], output_file: str = "paper_classifications.json"):
        """Save classification results to JSON file."""
        try:
            with open(output_file, 'w', encoding='utf-8') as f:
                json.dump(results, f, indent=2, ensure_ascii=False)
            logger.info(f"Results saved to {output_file}")
        except Exception as e:
            logger.error(f"Error saving results: {str(e)}")
    
    def generate_summary_report(self, results: Dict[str, Any], report_file: str = "classification_summary_report.txt"):
        """Generate a human-readable summary report."""
        try:
            with open(report_file, 'w', encoding='utf-8') as f:
                f.write("UBRI Paper Classification Summary Report\n")
                f.write("=" * 50 + "\n\n")
                
                summary = results['summary']
                f.write(f"Total Papers Classified: {summary['total_papers_classified']}\n")
                f.write(f"Classification Date: {summary['classification_timestamp']}\n")
                f.write(f"Universities Represented: {summary['universities_represented']}\n")
                f.write(f"Years Covered: {summary['years_covered']}\n\n")
                
                f.write("Category Distribution:\n")
                f.write("-" * 30 + "\n")
                for category, count in sorted(summary['category_distribution'].items(), key=lambda x: x[1], reverse=True):
                    percentage = (count / summary['total_papers_classified']) * 100
                    f.write(f"{category}: {count} papers ({percentage:.1f}%)\n")
                
                f.write("\nTop Universities by Paper Count:\n")
                f.write("-" * 35 + "\n")
                university_counts = {}
                for paper in results['classified_papers']:
                    uni = paper['university']
                    if uni:
                        university_counts[uni] = university_counts.get(uni, 0) + 1
                
                for uni, count in sorted(university_counts.items(), key=lambda x: x[1], reverse=True)[:10]:
                    f.write(f"{uni}: {count} papers\n")
                
                f.write("\nSample Papers by Category:\n")
                f.write("-" * 30 + "\n")
                for category in results['categories']:
                    category_papers = [p for p in results['classified_papers'] if p['category'] == category]
                    if category_papers:
                        f.write(f"\n{category}:\n")
                        for paper in category_papers[:3]:  # Show first 3 papers
                            f.write(f"  - {paper['title']} ({paper['university']})\n")
            
            logger.info(f"Summary report saved to {report_file}")
        except Exception as e:
            logger.error(f"Error generating summary report: {str(e)}")

def main():
    """Main function to run the paper classification."""
    # Check for OpenAI API key
    api_key = os.getenv('OPENAI_API_KEY')
    if not api_key:
        logger.error("Please set OPENAI_API_KEY environment variable")
        return
    
    # Load papers data
    try:
        with open('../data/processed/mongodb_papers_clean.json', 'r', encoding='utf-8') as f:
            papers_data = json.load(f)
        logger.info(f"Loaded {len(papers_data)} papers for classification")
    except Exception as e:
        logger.error(f"Error loading papers data: {str(e)}")
        return
    
    # Initialize classifier
    classifier = PaperClassifier(api_key)
    
    # Classify all papers
    results = classifier.classify_all_papers(papers_data)
    
    # Save results
    classifier.save_results(results, "paper_classifications.json")
    classifier.generate_summary_report(results, "classification_summary_report.txt")
    
    # Print quick summary
    print("\n" + "="*50)
    print("CLASSIFICATION COMPLETE")
    print("="*50)
    print(f"Total papers classified: {results['summary']['total_papers_classified']}")
    print(f"Results saved to: paper_classifications.json")
    print(f"Summary report saved to: classification_summary_report.txt")
    
    # Show top categories
    print("\nTop 5 Categories:")
    category_dist = results['summary']['category_distribution']
    for category, count in sorted(category_dist.items(), key=lambda x: x[1], reverse=True)[:5]:
        percentage = (count / results['summary']['total_papers_classified']) * 100
        print(f"  {category}: {count} papers ({percentage:.1f}%)")

if __name__ == "__main__":
    main() 