import os
os.environ["GOOGLE_CLOUD_PROJECT"] = "gen-lang-client-0449161426"
os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = "/Users/aindrilkar/Downloads/gen-lang-client-0449161426-fe873ba9d72d.json"
os.environ["GEMINI_API_KEY"] = "AIzaSyDWYTRBtrMLETqTle3LuTLSSng5cAiE_aA"

from vector_database.chroma import get_chroma_client
import json

def check_kpi_data():
    client = get_chroma_client()
    collection = client.get_collection(name="kpi_data")
    print(f"Total records: {collection.count()}")
    
    # Get all records
    all_data = collection.get()
    home_loan_attrition = []
    
    for i, metadata in enumerate(all_data["metadatas"]):
        if metadata.get("kpi_name") == "Home Loan Attrition Rate" and metadata.get("department") == "Home Loan":
            home_loan_attrition.append(metadata)
    
    print(f"\nFound {len(home_loan_attrition)} Home Loan Attrition Rate records:")
    for record in sorted(home_loan_attrition, key=lambda x: x["created_date"]):
        print(f"Date: {record['created_date']}, Value: {record['kpi_value']}")
    
    # Test date range query
    print("\nTesting date range query for last 4 months:")
    from datetime import datetime
    from dateutil.relativedelta import relativedelta
    
    current_date = datetime.now()
    end_date = current_date.replace(day=1)
    start_date = end_date - relativedelta(months=3)  # 4 months = current + 3 back
    
    print(f"Date range: {start_date.strftime('%Y-%m-%d')} to {end_date.strftime('%Y-%m-%d')}")
    
    date_filter = {
        "$and": [
            {"created_date": {"$gte": start_date.strftime("%Y-%m-%d")}},
            {"created_date": {"$lte": end_date.strftime("%Y-%m-%d")}}
        ]
    }
    
    print(f"Filter: {date_filter}")
    
    # Test the query
    from embedding.embedding import get_gemini_embedding
    query_embedding = get_gemini_embedding("home loan attrition rate")
    
    results = collection.query(
        query_embeddings=[query_embedding],
        n_results=50,
        include=["metadatas", "distances"],
        where=date_filter
    )
    
    print(f"\nQuery results: {len(results['metadatas'][0])} records found")
    for metadata in results['metadatas'][0]:
        if metadata.get("kpi_name") == "Home Loan Attrition Rate":
            print(f"Date: {metadata['created_date']}, Value: {metadata['kpi_value']}")

if __name__ == "__main__":
    check_kpi_data() 