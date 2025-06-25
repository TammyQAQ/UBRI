class MongoDBImporter:
    """Import papers with content into MongoDB."""
    
    def __init__(self, 
                 mongodb_uri: str = "mongodb+srv://yitianw:yitianw@cluster0.jvwt789.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0",
                 database_name: str = "ubri_papers",
                 papers_collection: str = "papers",
                 chunks_collection: str = "chunks"):
        # ... existing code ... 