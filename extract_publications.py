#!/usr/bin/env python3
"""
Extract UBRI Publications data from Excel file and output as formatted text.
"""

import pandas as pd
import re

def clean_text(text):
    """Clean and format text fields."""
    if pd.isna(text):
        return ""
    return str(text).strip()

def extract_publications():
    """Extract publications data and format as requested."""
    
    # Read the Excel file
    try:
        df = pd.read_excel('data/raw/Publications/UBRI Publications .xlsx')
        print(f"Successfully loaded {len(df)} publications")
    except Exception as e:
        print(f"Error reading Excel file: {e}")
        return
    
    # Define the columns we want to extract
    columns_mapping = {
        'Title': 'Title',
        'Author': 'Author', 
        'Keywords': 'Keywords',
        'University': 'University',
        'Link': 'Link',
        'Year': 'Year',
        'Venue': 'Venue',
        'Abstract': 'Abstract'
    }
    
    # Filter out rows that don't have meaningful data (like header rows)
    # Look for rows that have at least a title or author
    valid_rows = df[
        (df['Title'].notna() & (df['Title'] != 'Title')) |
        (df['Author'].notna() & (df['Author'] != 'Author'))
    ].copy()
    
    print(f"Found {len(valid_rows)} valid publication entries")
    
    # Create output text
    output_lines = []
    output_lines.append("UBRI PUBLICATIONS DATABASE")
    output_lines.append("=" * 50)
    output_lines.append("")
    
    for idx, row in valid_rows.iterrows():
        # Skip if this looks like a header row
        if pd.isna(row['Title']) or str(row['Title']).strip() == '':
            continue
            
        output_lines.append(f"PUBLICATION #{idx + 1}")
        output_lines.append("-" * 30)
        
        # Extract each field
        for col_key, display_name in columns_mapping.items():
            if col_key in df.columns:
                value = clean_text(row[col_key])
                if value and value != display_name:  # Skip if it's just the column header
                    output_lines.append(f"{display_name}: {value}")
        
        output_lines.append("")  # Empty line between publications
    
    # Write to file
    output_file = "ubri_publications_extracted.txt"
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write('\n'.join(output_lines))
    
    print(f"Extracted data written to: {output_file}")
    
    # Also show a sample of the extracted data
    print("\nSample of extracted data:")
    print("-" * 40)
    for i, line in enumerate(output_lines[:20]):
        print(line)

if __name__ == "__main__":
    extract_publications() 