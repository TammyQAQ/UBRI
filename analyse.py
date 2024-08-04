import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

# Load the Excel file
file_path = 'data/matrix.xlsx'
df = pd.read_excel(file_path)

# Function to extract paper numbers and filter those greater than 429
def extract_and_filter_papers(paper_str):
    if pd.isna(paper_str) or not isinstance(paper_str, str):
        return []
    papers = [int(p.strip()) for p in paper_str.split(',') if p.strip().isdigit()]
    return [p for p in papers if p > 429]

# Function to get paper counts for themes and blockchains
def get_paper_counts(df):
    theme_papers = {}
    blockchain_papers = {}

    for index, row in df.iterrows():
        theme = row[0]
        for blockchain in df.columns[1:]:
            papers = extract_and_filter_papers(row[blockchain])
            if theme not in theme_papers:
                theme_papers[theme] = []
            theme_papers[theme].extend(papers)
            
            if blockchain not in blockchain_papers:
                blockchain_papers[blockchain] = []
            blockchain_papers[blockchain].extend(papers)
    
    theme_paper_counts = {theme: len(set(papers)) for theme, papers in theme_papers.items()}
    blockchain_paper_counts = {blockchain: len(set(papers)) for blockchain, papers in blockchain_papers.items()}
    
    return theme_paper_counts, blockchain_paper_counts

# Function to plot top 5 counts
def plot_top_5_counts(counts, title, xlabel, ylabel, color):
    top_5 = pd.DataFrame(list(counts.items()), columns=[xlabel, ylabel]).nlargest(5, ylabel)
    plt.bar(top_5[xlabel], top_5[ylabel], color=color)
    plt.xlabel(xlabel)
    plt.ylabel(ylabel)
    plt.title(title)
    plt.xticks(rotation=45)
    plt.tight_layout()

def main():
    file_path = 'data/matrix.xlsx'
    df = pd.read_excel(file_path)
    
    theme_paper_counts, blockchain_paper_counts = get_paper_counts(df)
    
    plt.figure(figsize=(12, 6))

    plt.subplot(1, 2, 1)
    plot_top_5_counts(theme_paper_counts, 'Top 5 Themes by Paper Count', 'Theme', 'Count', 'blue')

    plt.subplot(1, 2, 2)
    plot_top_5_counts(blockchain_paper_counts, 'Top 5 Blockchains by Paper Count', 'Blockchain', 'Count', 'green')

    plt.show()

if __name__ == "__main__":
    main()
