#!/usr/bin/env python3
"""
Generate CSV output with universities vs themes where each cell contains comma-separated paper numbers
"""

import json
import pandas as pd
import os
from collections import defaultdict
from typing import Dict, List, Any

def load_classification_data(file_path: str) -> Dict[str, Any]:
    """Load classification data from JSON file"""
    with open(file_path, 'r', encoding='utf-8') as f:
        return json.load(f)

def generate_university_theme_papers_csv(data: Dict[str, Any], output_file: str = "university_theme_papers.csv"):
    """
    Generate CSV with universities vs themes where each cell contains comma-separated paper numbers
    """
    papers = data['classified_papers']
    
    # Get all unique universities and categories
    universities = set()
    categories = set()
    
    # Collect all universities and categories
    for paper in papers:
        if paper.get('is_blockchain_related', False):
            uni = paper.get('university', 'Unknown')
            universities.add(uni)
            
            # Get all categories for this paper
            for cat in [paper.get('primary_category'), paper.get('secondary_category'), paper.get('tertiary_category')]:
                if cat and cat != 'Not Blockchain Related':
                    categories.add(cat)
    
    universities = sorted(list(universities))
    categories = sorted(list(categories))
    
    print(f"Found {len(universities)} universities and {len(categories)} categories")
    
    # Create a dictionary to store paper numbers for each university-category combination
    university_category_papers = defaultdict(lambda: defaultdict(list))
    
    # Collect paper numbers for each university-category combination
    for paper in papers:
        if paper.get('is_blockchain_related', False):
            paper_id = paper.get('paper_id', 'Unknown')
            university = paper.get('university', 'Unknown')
            
            # Get all categories for this paper
            paper_categories = []
            for cat in [paper.get('primary_category'), paper.get('secondary_category'), paper.get('tertiary_category')]:
                if cat and cat != 'Not Blockchain Related':
                    paper_categories.append(cat)
            
            # Add paper ID to each category for this university
            for cat in paper_categories:
                university_category_papers[university][cat].append(paper_id)
    
    # Create the matrix
    matrix_data = []
    for uni in universities:
        row = {'University': uni}
        for cat in categories:
            paper_numbers = university_category_papers[uni][cat]
            if paper_numbers:
                # Sort paper numbers and join with commas
                paper_numbers.sort(key=lambda x: int(x) if x.isdigit() else float('inf'))
                row[cat] = ', '.join(paper_numbers)
            else:
                row[cat] = ''
        matrix_data.append(row)
    
    # Create DataFrame
    df = pd.DataFrame(matrix_data)
    df.set_index('University', inplace=True)
    
    # Save to CSV
    df.to_csv(output_file, encoding='utf-8')
    print(f"CSV saved to {output_file}")
    
    # Also create a count version (number of papers instead of paper numbers)
    count_data = []
    for uni in universities:
        row = {'University': uni}
        for cat in categories:
            count = len(university_category_papers[uni][cat])
            row[cat] = count
        count_data.append(row)
    
    count_df = pd.DataFrame(count_data)
    count_df.set_index('University', inplace=True)
    
    count_file = output_file.replace('.csv', '_counts.csv')
    count_df.to_csv(count_file, encoding='utf-8')
    print(f"Count CSV saved to {count_file}")
    
    return df, count_df

def main():
    """Main function"""
    # Find the most recent classification file
    import glob
    classification_files = glob.glob("ubri_paper_classifications_*.json")
    
    if not classification_files:
        print("No classification files found!")
        return
    
    latest_file = max(classification_files, key=os.path.getctime)
    print(f"Using classification file: {latest_file}")
    
    # Load data
    data = load_classification_data(latest_file)
    
    # Generate CSV
    df, count_df = generate_university_theme_papers_csv(data)
    
    # Print some statistics
    print(f"\nMatrix shape: {df.shape}")
    print(f"Count matrix shape: {count_df.shape}")
    
    # Show top universities by total papers
    total_papers = count_df.sum(axis=1).sort_values(ascending=False)
    print(f"\nTop 10 universities by total papers:")
    for i, (uni, count) in enumerate(total_papers.head(10).items(), 1):
        print(f"{i:2d}. {uni}: {count} papers")
    
    # Show top categories by total papers
    total_categories = count_df.sum(axis=0).sort_values(ascending=False)
    print(f"\nTop 10 categories by total papers:")
    for i, (cat, count) in enumerate(total_categories.head(10).items(), 1):
        print(f"{i:2d}. {cat}: {count} papers")
    
    # Show sample of the matrix
    print(f"\nSample of the matrix (first 3 universities, first 5 categories):")
    sample_df = df.head(3).iloc[:, :5]
    print(sample_df)

if __name__ == "__main__":
    main() 