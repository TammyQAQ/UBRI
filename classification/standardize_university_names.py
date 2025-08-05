#!/usr/bin/env python3
"""
Standardize university names using the provided list and update CSV files
"""

import json
import pandas as pd
import os
import re
from typing import Dict, List, Any

# Standard university names mapping
UNIVERSITY_MAPPING = {
    # Full names as provided
    'Arizona State University': 'Arizona State University',
    'Australian National University': 'Australian National University',
    'Carnegie Mellon University': 'Carnegie Mellon University',
    'Columbia University': 'Columbia University',
    'Cornell University': 'Cornell University',
    'Duke University': 'Duke University',
    'EBS Universität für Wirtschaft und Recht': 'EBS Universität für Wirtschaft und Recht',
    'EPITA School of Engineering and Computer Science': 'EPITA School of Engineering and Computer Science',
    'ETH Zurich': 'ETH Zurich',
    'European University Institute': 'European University Institute',
    'Fundação Getulio Vargas': 'Fundação Getulio Vargas',
    'Georgetown University': 'Georgetown University',
    'IE Business School Madrid': 'IE Business School Madrid',
    'Instituto Tecnológico Autónomo de México': 'Instituto Tecnológico Autónomo de México',
    'International Institute of Information Technology Hyderabad': 'International Institute of Information Technology Hyderabad',
    'Istanbul Technical University': 'Istanbul Technical University',
    'Indian Institute of Technology Bombay': 'Indian Institute of Technology Bombay',
    'Korea University': 'Korea University',
    'Kyoto University': 'Kyoto University',
    'Massachusetts Institute of Technology (MIT)': 'Massachusetts Institute of Technology (MIT)',
    'Morgan State University': 'Morgan State University',
    'National Kaohsiung University of Science and Technology': 'National Kaohsiung University of Science and Technology',
    'National University of Singapore': 'National University of Singapore',
    'Nanyang Technological University': 'Nanyang Technological University',
    'Northeastern University': 'Northeastern University',
    'Northwestern University Kellogg School of Management': 'Northwestern University Kellogg School of Management',
    'Nova School of Business and Economics': 'Nova School of Business and Economics',
    'Portland State University': 'Portland State University',
    'Princeton University': 'Princeton University',
    'Reykjavik University': 'Reykjavik University',
    'Royal University of Bhutan': 'Royal University of Bhutan',
    'Rutgers University Law School': 'Rutgers University Law School',
    'Stanford University': 'Stanford University',
    'Toronto Metropolitan University': 'Toronto Metropolitan University',
    'Trinity College Dublin': 'Trinity College Dublin',
    'Tsinghua University': 'Tsinghua University',
    'TU Delft': 'TU Delft',
    'University College London': 'University College London',
    'University of Bern': 'University of Bern',
    'University of Cape Town': 'University of Cape Town',
    'University of Kansas': 'University of Kansas',
    'University of Luxembourg': 'University of Luxembourg',
    'University of Michigan': 'University of Michigan',
    'University of Nicosia': 'University of Nicosia',
    'University of North Carolina at Chapel Hill': 'University of North Carolina at Chapel Hill',
    'University of Oregon': 'University of Oregon',
    'University of Oxford': 'University of Oxford',
    'University of Pennsylvania': 'University of Pennsylvania',
    'University of São Paulo': 'University of São Paulo',
    'University of Texas at Austin': 'University of Texas at Austin',
    'University of Tokyo': 'University of Tokyo',
    'University of Toronto': 'University of Toronto',
    'University of Trento': 'University of Trento',
    'University of Waterloo': 'University of Waterloo',
    'University of Wyoming': 'University of Wyoming',
    'University of Zurich': 'University of Zurich',
    'Victoria University': 'Victoria University',
    'Yonsei University': 'Yonsei University',
    
    # Common variations and abbreviations
    'ASU': 'Arizona State University',
    'ANU': 'Australian National University',
    'CMU': 'Carnegie Mellon University',
    'Columbia': 'Columbia University',
    'Cornell': 'Cornell University',
    'Duke': 'Duke University',
    'EBS': 'EBS Universität für Wirtschaft und Recht',
    'EPITA': 'EPITA School of Engineering and Computer Science',
    'ETH': 'ETH Zurich',
    'EUI': 'European University Institute',
    'FGV': 'Fundação Getulio Vargas',
    'Georgetown': 'Georgetown University',
    'IE Madrid': 'IE Business School Madrid',
    'ITAM': 'Instituto Tecnológico Autónomo de México',
    'IIIT-H': 'International Institute of Information Technology Hyderabad',
    'IIIT Hyderabad': 'International Institute of Information Technology Hyderabad',
    'ITU': 'Istanbul Technical University',
    'IITB': 'Indian Institute of Technology Bombay',
    'IIT Bombay': 'Indian Institute of Technology Bombay',
    'Korea U': 'Korea University',
    'Kyoto': 'Kyoto University',
    'MIT': 'Massachusetts Institute of Technology (MIT)',
    'Morgan State': 'Morgan State University',
    'NKUST': 'National Kaohsiung University of Science and Technology',
    'NUS': 'National University of Singapore',
    'NTU': 'Nanyang Technological University',
    'Northeastern': 'Northeastern University',
    'Northwestern': 'Northwestern University Kellogg School of Management',
    'Kellogg': 'Northwestern University Kellogg School of Management',
    'Nova SBE': 'Nova School of Business and Economics',
    'Portland State': 'Portland State University',
    'Princeton': 'Princeton University',
    'Reykjavik': 'Reykjavik University',
    'RUB': 'Royal University of Bhutan',
    'Rutgers': 'Rutgers University Law School',
    'Rutgers Law': 'Rutgers University Law School',
    'Rutgers Law School': 'Rutgers University Law School',
    'Stanford': 'Stanford University',
    'TMU': 'Toronto Metropolitan University',
    'TCD': 'Trinity College Dublin',
    'Trinity College': 'Trinity College Dublin',
    'Tsinghua': 'Tsinghua University',
    'Delft': 'TU Delft',
    'Delft University of Technology': 'TU Delft',
    'UCL': 'University College London',
    'Bern': 'University of Bern',
    'University of Bern': 'University of Bern',
    'Cape Town': 'University of Cape Town',
    'UCT': 'University of Cape Town',
    'Kansas': 'University of Kansas',
    'KU': 'University of Kansas',
    'Luxembourg': 'University of Luxembourg',
    'Michigan': 'University of Michigan',
    'UMichigan': 'University of Michigan',
    'Nicosia': 'University of Nicosia',
    'UNC': 'University of North Carolina at Chapel Hill',
    'North Carolina': 'University of North Carolina at Chapel Hill',
    'Oregon': 'University of Oregon',
    'Oxford': 'University of Oxford',
    'Penn': 'University of Pennsylvania',
    'UPenn': 'University of Pennsylvania',
    'USP': 'University of São Paulo',
    'São Paulo': 'University of São Paulo',
    'Sao Paulo': 'University of São Paulo',
    'Texas': 'University of Texas at Austin',
    'UT Austin': 'University of Texas at Austin',
    'Tokyo': 'University of Tokyo',
    'Toronto': 'University of Toronto',
    'U of T': 'University of Toronto',
    'Trento': 'University of Trento',
    'Waterloo': 'University of Waterloo',
    'Wyoming': 'University of Wyoming',
    'Zurich': 'University of Zurich',
    'Victoria': 'Victoria University',
    'Yonsei': 'Yonsei University',
    
    # Additional variations found in the data
    'Berkeley': 'University of California, Berkeley',
    'U.C. Berkeley': 'University of California, Berkeley',
    'UC Berkeley': 'University of California, Berkeley',
    'Fundacao Getulio Vargas': 'Fundação Getulio Vargas',
    'UZH': 'University of Zurich',
    'UZH Zurich': 'University of Zurich',
    'MSU': 'Morgan State University',
    'U Michigan': 'University of Michigan',
    'U Penn': 'University of Pennsylvania',
    'Trento University': 'University of Trento',
    'University of Kyoto': 'Kyoto University',
    'University of North Carolina (UNC)': 'University of North Carolina at Chapel Hill',
    'UCL/UK CBT': 'University College London',
    'NUS Fintech Lab': 'National University of Singapore',
    'UK CBT & NTU': 'Nanyang Technological University',
    'NTU & UK CBT': 'Nanyang Technological University',
    'FGV & USP': 'Fundação Getulio Vargas'
}

def standardize_university_name(name: str) -> str:
    """Standardize university name using the mapping"""
    if not name or pd.isna(name):
        return 'Unknown'
    
    name = str(name).strip()
    
    # Direct match
    if name in UNIVERSITY_MAPPING:
        return UNIVERSITY_MAPPING[name]
    
    # Try partial matches
    for key, value in UNIVERSITY_MAPPING.items():
        if name.lower() in key.lower() or key.lower() in name.lower():
            return value
    
    # If no match found, return original name
    print(f"Warning: No mapping found for university: '{name}'")
    return name

def update_classification_data(data: Dict[str, Any]) -> Dict[str, Any]:
    """Update classification data with standardized university names"""
    updated_data = data.copy()
    
    # Update papers
    for paper in updated_data['classified_papers']:
        old_name = paper.get('university', 'Unknown')
        new_name = standardize_university_name(old_name)
        paper['university'] = new_name
        if old_name != new_name:
            print(f"Updated: '{old_name}' -> '{new_name}'")
    
    # Update summary statistics
    if 'summary' in updated_data:
        # Recalculate university distribution
        university_counts = {}
        for paper in updated_data['classified_papers']:
            uni = paper.get('university', 'Unknown')
            university_counts[uni] = university_counts.get(uni, 0) + 1
        
        updated_data['summary']['university_distribution'] = university_counts
    
    return updated_data

def update_csv_files():
    """Update CSV files with standardized university names"""
    # Find the most recent classification file
    import glob
    classification_files = glob.glob("ubri_paper_classifications_*.json")
    
    if not classification_files:
        print("No classification files found!")
        return
    
    latest_file = max(classification_files, key=os.path.getctime)
    print(f"Using classification file: {latest_file}")
    
    # Load and update data
    with open(latest_file, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    print("Standardizing university names...")
    updated_data = update_classification_data(data)
    
    # Save updated JSON
    updated_file = latest_file.replace('.json', '_standardized.json')
    with open(updated_file, 'w', encoding='utf-8') as f:
        json.dump(updated_data, f, indent=2, ensure_ascii=False)
    print(f"Updated JSON saved to {updated_file}")
    
    # Regenerate CSV files
    print("Regenerating CSV files...")
    from generate_university_theme_papers_csv import generate_university_theme_papers_csv
    df, count_df = generate_university_theme_papers_csv(updated_data, "university_theme_papers_standardized.csv")
    
    print("Standardization completed!")
    return updated_data

def main():
    """Main function"""
    update_csv_files()

if __name__ == "__main__":
    main() 