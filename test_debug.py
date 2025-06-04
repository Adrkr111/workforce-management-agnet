import os
os.environ["GOOGLE_CLOUD_PROJECT"] = "gen-lang-client-0449161426"
os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = "/Users/aindrilkar/Downloads/gen-lang-client-0449161426-fe873ba9d72d.json"
os.environ["GEMINI_API_KEY"] = "AIzaSyDWYTRBtrMLETqTle3LuTLSSng5cAiE_aA"

from agents.kpi_agent import get_date_filter
from vector_database.chroma import get_chroma_client
from embedding.embedding import get_gemini_embedding

def debug_query():
    # Test the exact same query that's failing
    query_str = "kpi-attrition-rate department-home-loan range-4-months start-2025-02-01 end-2025-05-01"
    
    print(f"Testing query: {query_str}")
    
    # Get date filter
    date_filter = get_date_filter(query_str)
    print(f"Date filter: {date_filter}")
    
    # Query without semantic search first - just get all records with date filter
    client = get_chroma_client()
    collection = client.get_collection(name="kpi_data")
    
    print("\n=== Testing date filter only ===")
    try:
        results = collection.get(where=date_filter)
        print(f"Records found with date filter: {len(results['metadatas'])}")
        
        home_loan_records = []
        for metadata in results['metadatas']:
            if metadata.get("kpi_name") == "Home Loan Attrition Rate" and metadata.get("department") == "Home Loan":
                home_loan_records.append(metadata)
                print(f"Found: {metadata['created_date']} - {metadata['kpi_value']}")
        
        print(f"Home Loan Attrition Rate records: {len(home_loan_records)}")
        
    except Exception as e:
        print(f"Date filter failed: {e}")
    
    print("\n=== Testing semantic search + date filter ===")
    try:
        query_embedding = get_gemini_embedding("home loan attrition rate")
        
        results = collection.query(
            query_embeddings=[query_embedding],
            n_results=50,
            include=["metadatas", "distances"],
            where=date_filter
        )
        
        print(f"Records found with semantic + date filter: {len(results['metadatas'][0])}")
        
        home_loan_records = []
        for metadata in results['metadatas'][0]:
            if metadata.get("kpi_name") == "Home Loan Attrition Rate" and metadata.get("department") == "Home Loan":
                home_loan_records.append(metadata)
                print(f"Found: {metadata['created_date']} - {metadata['kpi_value']}")
        
        print(f"Home Loan Attrition Rate records: {len(home_loan_records)}")
        
    except Exception as e:
        print(f"Semantic + date filter failed: {e}")

if __name__ == "__main__":
    debug_query() 