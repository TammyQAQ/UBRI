import pandas as pd

# Load the Excel file
file_path = 'data/matrix.xlsx'
df = pd.read_excel(file_path)

# Function to extract paper numbers and filter those greater than 428
def extract_and_filter_papers(paper_str):
    if pd.isna(paper_str) or not isinstance(paper_str, str):
        return []
    papers = [int(p.strip()) for p in paper_str.split(',') if p.strip().isdigit()]
    return [p for p in papers if p > 428]

# Creating dictionaries to hold the results
theme_papers = {}
blockchain_papers = {}

# Iterate through each row in the dataframe
for index, row in df.iterrows():
    theme = row[0]  # First column is the theme
    for blockchain in df.columns[1:]:
        papers = extract_and_filter_papers(row[blockchain])
        if theme not in theme_papers:
            theme_papers[theme] = []
        theme_papers[theme].extend(papers)
        
        if blockchain not in blockchain_papers:
            blockchain_papers[blockchain] = []
        blockchain_papers[blockchain].extend(papers)

# Convert lists to sets to get unique paper numbers and then get counts
theme_paper_counts = {theme: len(set(papers)) for theme, papers in theme_papers.items()}
blockchain_paper_counts = {blockchain: len(set(papers)) for blockchain, papers in blockchain_papers.items()}

# Convert results to DataFrames for better readability
theme_counts_df = pd.DataFrame(list(theme_paper_counts.items()), columns=['Theme', 'Count'])
blockchain_counts_df = pd.DataFrame(list(blockchain_paper_counts.items()), columns=['Blockchain', 'Count'])

# Display the results
print("Theme Paper Counts:")
print(theme_counts_df)
print("\nBlockchain Paper Counts:")
print(blockchain_counts_df)
