#!/usr/bin/env python3
"""
Script to analyze papers classified as "Other"
"""

import json

def analyze_others():
    """Analyze papers classified as 'Other'."""
    try:
        with open('classification/paper_classifications.json', 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        # Get papers classified as "Other"
        other_papers = [p for p in data['classified_papers'] if p['category'] == 'Other']
        
        print(f"Papers classified as 'Other': {len(other_papers)}")
        print("=" * 60)
        
        # Show first 20 papers to understand patterns
        for i, paper in enumerate(other_papers[:20], 1):
            print(f"\n{i}. {paper['title']}")
            print(f"   Authors: {', '.join(paper['authors'])}")
            print(f"   University: {paper['university']}")
            print(f"   Year: {paper['year']}")
            print("-" * 40)
        
        if len(other_papers) > 20:
            print(f"\n... and {len(other_papers) - 20} more papers")
        
        # Analyze universities in "Other" category
        print(f"\n" + "=" * 60)
        print("UNIVERSITIES WITH MOST 'OTHER' PAPERS")
        print("=" * 60)
        
        uni_counts = {}
        for paper in other_papers:
            uni = paper['university']
            if uni:
                uni_counts[uni] = uni_counts.get(uni, 0) + 1
        
        for uni, count in sorted(uni_counts.items(), key=lambda x: x[1], reverse=True)[:10]:
            print(f"{uni}: {count} papers")
        
        # Analyze years in "Other" category
        print(f"\n" + "=" * 60)
        print("YEAR DISTRIBUTION OF 'OTHER' PAPERS")
        print("=" * 60)
        
        year_counts = {}
        for paper in other_papers:
            year = paper['year']
            if year:
                year_counts[year] = year_counts.get(year, 0) + 1
        
        for year in sorted(year_counts.keys()):
            print(f"{year}: {year_counts[year]} papers")
        
    except Exception as e:
        print(f"Error: {str(e)}")

if __name__ == "__main__":
    analyze_others() 