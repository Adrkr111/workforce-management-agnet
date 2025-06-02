import chromadb
import vertexai
import os
from pathlib import Path

vertexai.init(
    project=os.environ["GOOGLE_CLOUD_PROJECT"],
    location="us-central1"
)

def get_chroma_client():
    # Use the exact path from Jupyter notebook
    db_path = "/Users/aindrilkar/notebooks/workforce_management/chromadb_vector"
    print(f"\nUsing ChromaDB path: {db_path}")
    print(f"Path exists: {os.path.exists(db_path)}")
    
    client = chromadb.PersistentClient(path=db_path)
    
    # Ensure the collection exists and print stats
    collection = client.get_or_create_collection(
        name="forecast_data",
        metadata={"hnsw:space": "cosine"}
    )
    
    # Print collection info
    try:
        count = collection.count()
        print(f"\nCollection 'forecast_data' contains {count} documents")
    except Exception as e:
        print(f"Error getting collection count: {e}")
    
    return client
