import os
from vector_database.chroma import get_chroma_client
from embedding.embedding import get_gemini_embedding

def test_queries():
    # Set up environment variables
    os.environ["GOOGLE_CLOUD_PROJECT"] = "gen-lang-client-0449161426"
    os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = "/Users/aindrilkar/Downloads/gen-lang-client-0449161426-fe873ba9d72d.json"
    os.environ["GEMINI_API_KEY"] = "AIzaSyDWYTRBtrMLETqTle3LuTLSSng5cAiE_aA"
    
    print("\nInitializing ChromaDB client...")
    client = get_chroma_client()
    collection = client.get_or_create_collection(name="forecast_data")
    
    # Test queries
    test_cases = [
        "business-energy substream-cst team-support",
        "work volume forecast for tech bks insights",
        "work volume forecast for logistics dlt support",
        "work volume forecast for finance prj marketing",
        "work volume forecast for retail hrm risk"
    ]
    
    print("\nTesting different query patterns:")
    for query in test_cases:
        print(f"\n\nTesting query: {query}")
        
        # Get embedding for the query
        print("Getting query embedding...")
        query_embedding = get_gemini_embedding(query)
        
        # Search with different parameters
        print("\nTesting with n_results=5:")
        results = collection.query(
            query_embeddings=[query_embedding],
            n_results=5,
            include=["documents", "metadatas", "distances"]
        )
        
        if results and results.get('documents') and results['documents'][0]:
            print(f"Found {len(results['documents'])} matches")
            for i, (doc, distance) in enumerate(zip(results['documents'][0], results['distances'][0])):
                print(f"\nMatch {i+1} (distance: {distance}):")
                print(doc[:200] + "..." if len(doc) > 200 else doc)
        else:
            print("No results found")

if __name__ == "__main__":
    test_queries() 