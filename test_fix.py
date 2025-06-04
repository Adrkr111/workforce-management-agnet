import os
os.environ["GOOGLE_CLOUD_PROJECT"] = "gen-lang-client-0449161426"
os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = "/Users/aindrilkar/Downloads/gen-lang-client-0449161426-fe873ba9d72d.json"
os.environ["GEMINI_API_KEY"] = "AIzaSyDWYTRBtrMLETqTle3LuTLSSng5cAiE_aA"

from agents.kpi_agent import get_date_filter
from vector_database.chroma import get_chroma_client
from embedding.embedding import get_gemini_embedding

def test_fixed_query():
    # Test the new date filter
    print("Testing 'last 4 months' query:")
    date_filter = get_date_filter("home loan attrition rate last 4 months")
    print(f"Date filter: {date_filter}")
    
    # Test with ChromaDB
    client = get_chroma_client()
    collection = client.get_collection(name="kpi_data")
    
    query_embedding = get_gemini_embedding("home loan attrition rate")
    
    results = collection.query(
        query_embeddings=[query_embedding],
        n_results=50,
        include=["metadatas", "distances"],
        where=date_filter
    )
    
    print(f"\nQuery results: {len(results['metadatas'][0])} records found")
    home_loan_results = []
    for metadata in results['metadatas'][0]:
        if metadata.get("kpi_name") == "Home Loan Attrition Rate":
            home_loan_results.append(metadata)
    
    print(f"Home Loan Attrition Rate records: {len(home_loan_results)}")
    for metadata in sorted(home_loan_results, key=lambda x: x['created_date']):
        print(f"Date: {metadata['created_date']}, Value: {metadata['kpi_value']}")

if __name__ == "__main__":
    test_fixed_query() 