import json
import requests
from pymongo import MongoClient

# MongoDB connection
MONGO_URI = "mongodb+srv://yitianw:2T9KEjQqvMBSZ68Y@cluster0.jvwt789.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0"
DB_NAME = "UBRI_Publication"
COLLECTION_NAME = "Papers"

# Jina API details
JINA_API_KEY = "jina_ecf9e5b8a0b04908a6fd8ddb5e437509YzHhwJ9RGvbUIxxumQr1HDkF1Rqd"  # <-- Replace with your Jina API key
JINA_ENDPOINT = "https://r.jina.ai/"  # Or your specific endpoint

# 1. Fetch all documents from MongoDB
client = MongoClient(MONGO_URI)
db = client[DB_NAME]
collection = db[COLLECTION_NAME]

print("Fetching all documents from MongoDB...")
docs = list(collection.find())
print(f"Fetched {len(docs)} documents.")

# Remove MongoDB ObjectId for JSON serialization
for doc in docs:
    doc.pop('_id', None)

# 2. Send to Jina API
headers = {
    "Authorization": f"Bearer {JINA_API_KEY}",
    "Content-Type": "application/json"
}

print("Sending data to Jina API...")
response = requests.post(
    JINA_ENDPOINT,
    headers=headers,
    json=docs
)

print(f"Jina API response status: {response.status_code}")
try:
    print(response.json())
except Exception:
    print(response.text) 