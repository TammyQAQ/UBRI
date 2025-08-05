#!/usr/bin/env python3
"""
Script to view and analyze paper classification results
"""

import json
import sys
from collections import Counter

def load_classifications(filename="paper_classifications.json"):
    """Load classification results from JSON file."""
    try:
        with open(filename, 'r', encoding='utf-8') as f:
            return json.load(f)
    except FileNotFoundError:
        print(f"File {filename} not found. Please run the classification first.")
        return None
    except Exception as e:
        print(f"Error loading {filename}: {str(e)}")
        return None

def display_summary(results):
    """Display summary statistics."""
    summary = results['summary']
    
    print("=" * 60)
    print("UBRI PAPER CLASSIFICATION SUMMARY")
    print("=" * 60)
    print(f"Total Papers: {summary['total_papers_classified']}")
    print(f"Universities: {summary['universities_represented']}")
    print(f"Years: {summary['years_covered']}")
    print(f"Classification Date: {summary['classification_timestamp']}")
    
    print("\n" + "=" * 60)
    print("CATEGORY DISTRIBUTION")
    print("=" * 60)
    
    # Sort categories by count
    sorted_categories = sorted(
        summary['category_distribution'].items(), 
        key=lambda x: x[1], 
        reverse=True
    )
    
    for category, count in sorted_categories:
        if count > 0:
            percentage = (count / summary['total_papers_classified']) * 100
            print(f"{category:<40} {count:>4} papers ({percentage:>5.1f}%)")

def display_papers_by_category(results, category_name=None):
    """Display papers grouped by category."""
    papers = results['classified_papers']
    
    if category_name:
        # Show papers for specific category
        category_papers = [p for p in papers if p['category'] == category_name]
        if not category_papers:
            print(f"No papers found in category: {category_name}")
            return
        
        print(f"\n" + "=" * 60)
        print(f"PAPERS IN CATEGORY: {category_name}")
        print(f"Total: {len(category_papers)} papers")
        print("=" * 60)
        
        for i, paper in enumerate(category_papers, 1):
            print(f"\n{i}. {paper['title']}")
            print(f"   Authors: {', '.join(paper['authors'])}")
            print(f"   University: {paper['university']}")
            print(f"   Year: {paper['year']}")
    else:
        # Show papers for all categories
        for category in results['categories']:
            category_papers = [p for p in papers if p['category'] == category]
            if category_papers:
                print(f"\n" + "=" * 60)
                print(f"CATEGORY: {category}")
                print(f"Papers: {len(category_papers)}")
                print("=" * 60)
                
                for i, paper in enumerate(category_papers[:5], 1):  # Show first 5
                    print(f"\n{i}. {paper['title']}")
                    print(f"   Authors: {', '.join(paper['authors'])}")
                    print(f"   University: {paper['university']}")
                    print(f"   Year: {paper['year']}")
                
                if len(category_papers) > 5:
                    print(f"\n   ... and {len(category_papers) - 5} more papers")

def display_university_stats(results):
    """Display statistics by university."""
    papers = results['classified_papers']
    
    # Count papers by university
    university_counts = Counter()
    university_categories = {}
    
    for paper in papers:
        uni = paper['university']
        if uni:
            university_counts[uni] += 1
            if uni not in university_categories:
                university_categories[uni] = Counter()
            university_categories[uni][paper['category']] += 1
    
    print("\n" + "=" * 60)
    print("UNIVERSITY STATISTICS")
    print("=" * 60)
    
    # Show top universities
    print("\nTop 15 Universities by Paper Count:")
    print("-" * 40)
    for uni, count in university_counts.most_common(15):
        print(f"{uni:<35} {count:>4} papers")
    
    # Show category distribution for top universities
    print("\n" + "=" * 60)
    print("CATEGORY DISTRIBUTION BY TOP UNIVERSITIES")
    print("=" * 60)
    
    for uni, count in university_counts.most_common(10):
        print(f"\n{uni} ({count} papers):")
        categories = university_categories[uni]
        for category, cat_count in categories.most_common():
            percentage = (cat_count / count) * 100
            print(f"  {category}: {cat_count} papers ({percentage:.1f}%)")

def search_papers(results, search_term):
    """Search papers by title or author."""
    papers = results['classified_papers']
    search_term = search_term.lower()
    
    matching_papers = []
    for paper in papers:
        title_match = search_term in paper['title'].lower()
        author_match = any(search_term in author.lower() for author in paper['authors'])
        
        if title_match or author_match:
            matching_papers.append(paper)
    
    if not matching_papers:
        print(f"No papers found matching '{search_term}'")
        return
    
    print(f"\n" + "=" * 60)
    print(f"SEARCH RESULTS FOR: '{search_term}'")
    print(f"Found {len(matching_papers)} papers")
    print("=" * 60)
    
    for i, paper in enumerate(matching_papers, 1):
        print(f"\n{i}. {paper['title']}")
        print(f"   Authors: {', '.join(paper['authors'])}")
        print(f"   University: {paper['university']}")
        print(f"   Category: {paper['category']}")
        print(f"   Year: {paper['year']}")

def main():
    """Main function with interactive menu."""
    if len(sys.argv) > 1:
        filename = sys.argv[1]
    else:
        filename = "paper_classifications.json"
    
    results = load_classifications(filename)
    if not results:
        return
    
    while True:
        print("\n" + "=" * 60)
        print("UBRI PAPER CLASSIFICATION VIEWER")
        print("=" * 60)
        print("1. Show summary statistics")
        print("2. Show papers by category")
        print("3. Show university statistics")
        print("4. Search papers")
        print("5. Show papers for specific category")
        print("6. Exit")
        
        choice = input("\nEnter your choice (1-6): ").strip()
        
        if choice == '1':
            display_summary(results)
        elif choice == '2':
            display_papers_by_category(results)
        elif choice == '3':
            display_university_stats(results)
        elif choice == '4':
            search_term = input("Enter search term: ").strip()
            if search_term:
                search_papers(results, search_term)
        elif choice == '5':
            print("\nAvailable categories:")
            for i, category in enumerate(results['categories'], 1):
                count = results['summary']['category_distribution'][category]
                if count > 0:
                    print(f"{i}. {category} ({count} papers)")
            
            try:
                cat_choice = int(input("\nEnter category number: ")) - 1
                if 0 <= cat_choice < len(results['categories']):
                    category = results['categories'][cat_choice]
                    display_papers_by_category(results, category)
                else:
                    print("Invalid category number")
            except ValueError:
                print("Please enter a valid number")
        elif choice == '6':
            print("Goodbye!")
            break
        else:
            print("Invalid choice. Please enter 1-6.")

if __name__ == "__main__":
    main() 