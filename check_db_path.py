import os
from vector_database.chroma import get_chroma_client

def check_db_location():
    # Get the ChromaDB client
    client = get_chroma_client()
    
    # Get the absolute path of the database
    db_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), "data", "chromadb")
    db_path = os.path.abspath(db_path)
    
    print(f"\nChromaDB Path: {db_path}")
    print(f"Path exists: {os.path.exists(db_path)}")
    
    if os.path.exists(db_path):
        print("\nContents of database directory:")
        for root, dirs, files in os.walk(db_path):
            level = root.replace(db_path, '').count(os.sep)
            indent = ' ' * 4 * level
            print(f"{indent}{os.path.basename(root)}/")
            subindent = ' ' * 4 * (level + 1)
            for f in files:
                print(f"{subindent}{f}")
    
    # Check collection contents
    collection = client.get_or_create_collection(name="forecast_data")
    results = collection.get()
    
    print("\nDatabase contents:")
    if results and results.get('documents'):
        print(f"Number of documents: {len(results['documents'])}")
        for i, doc in enumerate(results['documents'][:5]):  # Show first 5 docs
            print(f"\nDocument {i+1}:")
            print(doc)
    else:
        print("No documents found in database")

if __name__ == "__main__":
    check_db_location() 