print(">>> THIS IS THE CORRECT SCRIPT <<<")

from pymongo import MongoClient
import logging
import json
from pathlib import Path

logger = logging.getLogger(__name__)

class MongoDBImporter:
    """Import papers with content into MongoDB."""
    
    def __init__(self, 
                 mongodb_uri: str = "mongodb+srv://yitianw:2T9KEjQqvMBSZ68Y@cluster0.jvwt789.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0",
                 database_name: str = "UBRI_Publication",
                 papers_collection: str = "Papers",
                 chunks_collection: str = "chunks"):
        self.mongodb_uri = mongodb_uri
        self.database_name = database_name
        self.papers_collection = papers_collection
        self.chunks_collection = chunks_collection
        # Connect to MongoDB
        self.client = MongoClient(mongodb_uri)
        self.db = self.client[database_name]
        self.papers_coll = self.db[papers_collection]
        self.chunks_coll = self.db[chunks_collection]
        print(f"Connected to MongoDB: {mongodb_uri}")
        print(f"Database: {database_name}")

def main():
    print(">>> Starting import script...")
    importer = MongoDBImporter()
    data_path = Path("/Users/yitianw/UBRI/data/processed/mongodb_papers_clean.json")
    if not data_path.exists():
        print(f"Data file not found: {data_path}")
        return
    with open(data_path, "r", encoding="utf-8") as f:
        papers = json.load(f)
    print(f"Loaded {len(papers)} papers from JSON")
    inserted = 0
    for paper in papers:
        try:
            importer.papers_coll.insert_one(paper)
            inserted += 1
        except Exception as e:
            print(f"Failed to insert paper: {e}")
    print(f"Inserted {inserted} papers into MongoDB.")

if __name__ == "__main__":
    main() 