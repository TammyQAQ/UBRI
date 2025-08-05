#!/usr/bin/env python3
"""
Improved UBRI Paper Classification Viewer

This script provides an interactive interface to explore the improved classification results
with multi-category assignments and better analysis capabilities.
"""

import json
import os
import sys
from typing import Dict, List, Any
from collections import defaultdict, Counter
import pandas as pd

def load_classification_data(file_path: str) -> Dict[str, Any]:
    """Load classification data from JSON file"""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            return json.load(f)
    except Exception as e:
        print(f"Error loading file {file_path}: {e}")
        return None

def display_summary(data: Dict[str, Any]):
    """Display summary statistics"""
    summary = data['summary']
    
    print("\n" + "="*80)
    print("IMPROVED UBRI PAPER CLASSIFICATION SUMMARY")
    print("="*80)
    
    print(f"Total Papers Processed: {summary['total_papers_processed']}")
    print(f"Blockchain Related Papers: {summary['blockchain_related_papers']}")
    print(f"Not Blockchain Related: {summary['not_blockchain_papers']}")
    print(f"Classification Date: {summary['classification_timestamp']}")
    print(f"Categories Used: {len(summary['categories_used'])}")
    print(f"Years Covered: {summary['years_covered']}")
    
    # Category distribution
    print(f"\n{'CATEGORY DISTRIBUTION':^80}")
    print("-" * 80)
    
    sorted_categories = sorted(summary['category_distribution'].items(), 
                             key=lambda x: x[1], reverse=True)
    
    for i, (category, count) in enumerate(sorted_categories):
        percentage = (count / summary['blockchain_related_papers']) * 100 if summary['blockchain_related_papers'] > 0 else 0
        print(f"{i+1:2d}. {category:<50} {count:>3} papers ({percentage:>5.1f}%)")
    
    # University distribution
    print(f"\n{'TOP UNIVERSITIES':^80}")
    print("-" * 80)
    
    sorted_universities = sorted(summary['university_distribution'].items(), 
                               key=lambda x: x[1], reverse=True)
    
    for i, (university, count) in enumerate(sorted_universities[:15]):
        print(f"{i+1:2d}. {university:<60} {count:>3} papers")

def display_papers_by_category(data: Dict[str, Any], category: str = None):
    """Display papers grouped by category"""
    papers = data['classified_papers']
    
    if category:
        # Show papers for specific category
        category_papers = []
        for paper in papers:
            if paper.get('is_blockchain_related', False):
                if (paper.get('primary_category') == category or 
                    paper.get('secondary_category') == category or 
                    paper.get('tertiary_category') == category):
                    category_papers.append(paper)
        
        print(f"\n{'PAPERS IN CATEGORY: ' + category:^80}")
        print("-" * 80)
        
        for i, paper in enumerate(category_papers, 1):
            print(f"{i:2d}. {paper['title']}")
            print(f"    Authors: {paper['authors']}")
            print(f"    University: {paper['university']}")
            print(f"    Year: {paper['year']}")
            print(f"    Categories: {paper.get('primary_category', 'N/A')} | {paper.get('secondary_category', 'N/A')} | {paper.get('tertiary_category', 'N/A')}")
            print(f"    Confidence: {paper.get('confidence_levels', {}).get('primary', 'N/A')}")
            print()
    else:
        # Show category overview
        category_counts = defaultdict(int)
        for paper in papers:
            if paper.get('is_blockchain_related', False):
                for cat in [paper.get('primary_category'), paper.get('secondary_category'), paper.get('tertiary_category')]:
                    if cat and cat != 'Not Blockchain Related':
                        category_counts[cat] += 1
        
        print(f"\n{'CATEGORY OVERVIEW':^80}")
        print("-" * 80)
        
        sorted_categories = sorted(category_counts.items(), key=lambda x: x[1], reverse=True)
        for i, (cat, count) in enumerate(sorted_categories, 1):
            print(f"{i:2d}. {cat:<50} {count:>3} papers")

def display_university_analysis(data: Dict[str, Any], university: str = None):
    """Display university-specific analysis"""
    papers = data['classified_papers']
    
    if university:
        # Show papers for specific university
        uni_papers = [p for p in papers if p.get('university', '').lower() == university.lower()]
        
        print(f"\n{'PAPERS FROM UNIVERSITY: ' + university.upper():^80}")
        print("-" * 80)
        
        # Group by category
        uni_categories = defaultdict(list)
        for paper in uni_papers:
            if paper.get('is_blockchain_related', False):
                primary_cat = paper.get('primary_category', 'Unknown')
                uni_categories[primary_cat].append(paper)
        
        for category, category_papers in sorted(uni_categories.items()):
            print(f"\n{category} ({len(category_papers)} papers):")
            for paper in category_papers[:5]:  # Show first 5 papers
                print(f"  - {paper['title']}")
                print(f"    Year: {paper['year']}, Authors: {paper['authors']}")
    else:
        # Show university overview
        uni_stats = defaultdict(lambda: {'total': 0, 'blockchain': 0, 'categories': Counter()})
        
        for paper in papers:
            uni = paper.get('university', 'Unknown')
            uni_stats[uni]['total'] += 1
            
            if paper.get('is_blockchain_related', False):
                uni_stats[uni]['blockchain'] += 1
                for cat in [paper.get('primary_category'), paper.get('secondary_category'), paper.get('tertiary_category')]:
                    if cat and cat != 'Not Blockchain Related':
                        uni_stats[uni]['categories'][cat] += 1
        
        print(f"\n{'UNIVERSITY ANALYSIS':^80}")
        print("-" * 80)
        
        sorted_unis = sorted(uni_stats.items(), key=lambda x: x[1]['blockchain'], reverse=True)
        for uni, stats in sorted_unis[:15]:
            blockchain_pct = (stats['blockchain'] / stats['total']) * 100 if stats['total'] > 0 else 0
            top_category = stats['categories'].most_common(1)[0] if stats['categories'] else ('None', 0)
            print(f"{uni:<40} {stats['blockchain']:>3}/{stats['total']:>3} blockchain ({blockchain_pct:>5.1f}%) | Top: {top_category[0]}")

def search_papers(data: Dict[str, Any], query: str):
    """Search papers by title, author, or university"""
    papers = data['classified_papers']
    query = query.lower()
    
    matching_papers = []
    for paper in papers:
        if (query in paper.get('title', '').lower() or 
            query in paper.get('authors', '').lower() or 
            query in paper.get('university', '').lower()):
            matching_papers.append(paper)
    
    print(f"\n{'SEARCH RESULTS FOR: ' + query.upper():^80}")
    print("-" * 80)
    
    if matching_papers:
        for i, paper in enumerate(matching_papers, 1):
            print(f"{i:2d}. {paper['title']}")
            print(f"    Authors: {paper['authors']}")
            print(f"    University: {paper['university']}")
            print(f"    Year: {paper['year']}")
            print(f"    Blockchain Related: {paper.get('is_blockchain_related', 'Unknown')}")
            if paper.get('is_blockchain_related', False):
                print(f"    Categories: {paper.get('primary_category', 'N/A')} | {paper.get('secondary_category', 'N/A')} | {paper.get('tertiary_category', 'N/A')}")
            print()
    else:
        print("No papers found matching your query.")

def display_multi_category_analysis(data: Dict[str, Any]):
    """Display analysis of papers with multiple category assignments"""
    papers = data['classified_papers']
    blockchain_papers = [p for p in papers if p.get('is_blockchain_related', False)]
    
    print(f"\n{'MULTI-CATEGORY ANALYSIS':^80}")
    print("-" * 80)
    
    # Analyze category combinations
    category_combinations = Counter()
    for paper in blockchain_papers:
        cats = [paper.get('primary_category'), paper.get('secondary_category'), paper.get('tertiary_category')]
        cats = [c for c in cats if c and c != 'Not Blockchain Related']
        if len(cats) >= 2:
            combination = ' + '.join(sorted(set(cats)))
            category_combinations[combination] += 1
    
    print("Most Common Category Combinations:")
    for combination, count in category_combinations.most_common(10):
        print(f"  {combination}: {count} papers")
    
    # Analyze papers that appear in multiple categories
    print(f"\nPapers appearing in multiple categories:")
    for paper in blockchain_papers:
        cats = [paper.get('primary_category'), paper.get('secondary_category'), paper.get('tertiary_category')]
        cats = [c for c in cats if c and c != 'Not Blockchain Related']
        if len(set(cats)) >= 2:
            print(f"  {paper['title']}")
            print(f"    Categories: {' | '.join(set(cats))}")

def export_to_excel(data: Dict[str, Any], filename: str = "classification_analysis.xlsx"):
    """Export classification data to Excel for further analysis"""
    papers = data['classified_papers']
    
    # Prepare data for Excel
    excel_data = []
    for paper in papers:
        row = {
            'Paper ID': paper.get('paper_id', ''),
            'Title': paper.get('title', ''),
            'Authors': paper.get('authors', ''),
            'University': paper.get('university', ''),
            'Year': paper.get('year', ''),
            'Is Blockchain Related': paper.get('is_blockchain_related', False),
            'Primary Category': paper.get('primary_category', ''),
            'Secondary Category': paper.get('secondary_category', ''),
            'Tertiary Category': paper.get('tertiary_category', ''),
            'Primary Confidence': paper.get('confidence_levels', {}).get('primary', ''),
            'Secondary Confidence': paper.get('confidence_levels', {}).get('secondary', ''),
            'Tertiary Confidence': paper.get('confidence_levels', {}).get('tertiary', ''),
            'New Categories Suggested': ', '.join(paper.get('new_categories_suggested', [])),
            'Reasoning': paper.get('reasoning', '')
        }
        excel_data.append(row)
    
    df = pd.DataFrame(excel_data)
    df.to_excel(filename, index=False)
    print(f"Data exported to {filename}")

def interactive_menu(data: Dict[str, Any]):
    """Interactive menu for exploring classification data"""
    while True:
        print("\n" + "="*80)
        print("IMPROVED UBRI CLASSIFICATION VIEWER")
        print("="*80)
        print("1. Display Summary Statistics")
        print("2. Browse Papers by Category")
        print("3. University Analysis")
        print("4. Search Papers")
        print("5. Multi-Category Analysis")
        print("6. Export to Excel")
        print("7. Exit")
        print("-" * 80)
        
        choice = input("Enter your choice (1-7): ").strip()
        
        if choice == '1':
            display_summary(data)
        
        elif choice == '2':
            print("\nEnter category name (or press Enter to see all categories):")
            category = input().strip()
            display_papers_by_category(data, category if category else None)
        
        elif choice == '3':
            print("\nEnter university name (or press Enter to see all universities):")
            university = input().strip()
            display_university_analysis(data, university if university else None)
        
        elif choice == '4':
            print("\nEnter search term (title, author, or university):")
            query = input().strip()
            if query:
                search_papers(data, query)
            else:
                print("Please enter a search term.")
        
        elif choice == '5':
            display_multi_category_analysis(data)
        
        elif choice == '6':
            filename = input("Enter Excel filename (default: classification_analysis.xlsx): ").strip()
            if not filename:
                filename = "classification_analysis.xlsx"
            export_to_excel(data, filename)
        
        elif choice == '7':
            print("Goodbye!")
            break
        
        else:
            print("Invalid choice. Please enter a number between 1 and 7.")

def main():
    """Main function"""
    # Check for classification files
    classification_files = [
        "improved_paper_classifications_*.json",
        "paper_classifications.json"
    ]
    
    # Find the most recent classification file
    latest_file = None
    for pattern in classification_files:
        import glob
        files = glob.glob(os.path.join('classification', pattern))
        if files:
            latest_file = max(files, key=os.path.getctime)
            break
    
    if not latest_file:
        print("No classification files found. Please run the classification script first.")
        return
    
    print(f"Loading classification data from: {latest_file}")
    data = load_classification_data(latest_file)
    
    if not data:
        print("Failed to load classification data.")
        return
    
    # Start interactive menu
    interactive_menu(data)

if __name__ == "__main__":
    main() 