#!/usr/bin/env python3
"""
Test script for paper classification - runs on a small sample first
"""

import json
import os
from classify_papers import PaperClassifier

def test_classification():
    """Test the classification with a small sample of papers."""
    # Check for OpenAI API key
    api_key = os.getenv('OPENAI_API_KEY')
    if not api_key:
        print("Please set OPENAI_API_KEY environment variable")
        return
    
    # Load papers data
    try:
        with open('../data/processed/mongodb_papers_clean.json', 'r', encoding='utf-8') as f:
            papers_data = json.load(f)
        print(f"Loaded {len(papers_data)} papers")
    except Exception as e:
        print(f"Error loading papers data: {str(e)}")
        return
    
    # Take a small sample for testing (first 5 papers)
    test_papers = papers_data[:5]
    print(f"Testing with {len(test_papers)} papers...")
    
    # Initialize classifier
    classifier = PaperClassifier(api_key)
    
    # Test classification on sample
    results = classifier.classify_all_papers(test_papers, batch_size=1)
    
    # Print results
    print("\n" + "="*60)
    print("TEST CLASSIFICATION RESULTS")
    print("="*60)
    
    for paper in results['classified_papers']:
        print(f"\nTitle: {paper['title']}")
        print(f"Authors: {', '.join(paper['authors'])}")
        print(f"University: {paper['university']}")
        print(f"Category: {paper['category']}")
        print("-" * 40)
    
    # Show category distribution
    print(f"\nCategory Distribution:")
    for category, count in results['summary']['category_distribution'].items():
        if count > 0:
            print(f"  {category}: {count} papers")
    
    print(f"\nTest completed successfully!")
    print(f"Results saved to: test_classifications.json")
    
    # Save test results
    classifier.save_results(results, "test_classifications.json")

if __name__ == "__main__":
    test_classification() 