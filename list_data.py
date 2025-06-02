import os

# Set up environment variables
os.environ["GOOGLE_CLOUD_PROJECT"] = "gen-lang-client-0449161426"
os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = "/Users/aindrilkar/Downloads/gen-lang-client-0449161426-fe873ba9d72d.json"
os.environ["GEMINI_API_KEY"] = "AIzaSyDWYTRBtrMLETqTle3LuTLSSng5cAiE_aA"

from vector_database.chroma import get_chroma_client

def list_data():
    print("Connecting to ChromaDB...")
    client = get_chroma_client()
    collection = client.get_or_create_collection(name="forecast_data")
    
    print("\nGetting all data...")
    results = collection.get()
    
    print("\nDocuments in database:")
    if results and results.get('documents'):
        for i, doc in enumerate(results['documents']):
            print(f"\nDocument {i+1}:")
            print(doc)
            if results.get('metadatas') and results['metadatas'][i]:
                print("Metadata:", results['metadatas'][i])
    else:
        print("No documents found in database")

if __name__ == "__main__":
    list_data() 