import os
os.environ["GOOGLE_CLOUD_PROJECT"] = "gen-lang-client-0449161426"
os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = "/Users/aindrilkar/Downloads/gen-lang-client-0449161426-fe873ba9d72d.json"
os.environ["GEMINI_API_KEY"] = "AIzaSyDWYTRBtrMLETqTle3LuTLSSng5cAiE_aA"

from agents.kpi_agent import get_date_filter, fetch_kpi
from vector_database.chroma import get_chroma_client
from embedding.embedding import get_gemini_embedding

def test_correct_query():
    # Test different query formats
    queries = [
        "home loan attrition rate last 4 months",
        "home loan attrition rate for the last 4 months",
        "what is the home loan attrition rate for last 4 months"
    ]
    
    for query in queries:
        print(f"\n=== Testing query: {query} ===")
        
        # Test date filter
        date_filter = get_date_filter(query)
        print(f"Date filter: {date_filter}")
        
        if date_filter:
            # Test full fetch_kpi function
            result = fetch_kpi(query)
            if "results" in result:
                print("SUCCESS!")
                print(result["results"])
            else:
                print("FAILED:", result.get("error", "Unknown error"))
        else:
            print("No date filter generated")

if __name__ == "__main__":
    test_correct_query() 