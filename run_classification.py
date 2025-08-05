#!/usr/bin/env python3
"""
Convenience script to run classification tools from the main directory
"""

import sys
import os
import subprocess

def main():
    """Main function to run classification tools."""
    if len(sys.argv) < 2:
        print("UBRI Paper Classification System")
        print("=" * 40)
        print("Usage:")
        print("  python run_classification.py test     - Run test classification")
        print("  python run_classification.py full     - Run full classification")
        print("  python run_classification.py view     - View results interactively")
        print("  python run_classification.py summary  - Show summary report")
        print("  python run_classification.py help     - Show this help")
        return
    
    command = sys.argv[1].lower()
    
    # Change to classification directory
    classification_dir = os.path.join(os.path.dirname(__file__), 'classification')
    
    if not os.path.exists(classification_dir):
        print(f"Error: Classification directory not found at {classification_dir}")
        return
    
    os.chdir(classification_dir)
    
    if command == 'test':
        print("Running test classification...")
        subprocess.run([sys.executable, 'test_classification.py'])
    
    elif command == 'full':
        print("Running full classification...")
        print("This will process all papers and may take 10-15 minutes.")
        confirm = input("Continue? (y/N): ").strip().lower()
        if confirm == 'y':
            subprocess.run([sys.executable, 'classify_papers.py'])
        else:
            print("Cancelled.")
    
    elif command == 'view':
        print("Starting interactive viewer...")
        subprocess.run([sys.executable, 'view_classifications.py'])
    
    elif command == 'summary':
        summary_file = 'classification_summary_report.txt'
        if os.path.exists(summary_file):
            with open(summary_file, 'r') as f:
                print(f.read())
        else:
            print(f"Summary file not found: {summary_file}")
            print("Run 'python run_classification.py full' first to generate results.")
    
    elif command == 'help':
        print("UBRI Paper Classification System")
        print("=" * 40)
        print("Available commands:")
        print("  test     - Run test classification on 5 papers")
        print("  full     - Run full classification on all papers")
        print("  view     - Interactive viewer for browsing results")
        print("  summary  - Display summary report")
        print("  help     - Show this help message")
        print("\nAll files are stored in the 'classification/' directory.")
    
    else:
        print(f"Unknown command: {command}")
        print("Use 'python run_classification.py help' for available commands.")

if __name__ == "__main__":
    main() 