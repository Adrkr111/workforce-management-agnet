import os
os.environ["GOOGLE_CLOUD_PROJECT"] = "gen-lang-client-0449161426"
os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = "/Users/aindrilkar/Downloads/gen-lang-client-0449161426-fe873ba9d72d.json"
os.environ["GEMINI_API_KEY"] = "AIzaSyDWYTRBtrMLETqTle3LuTLSSng5cAiE_aA"

from agents.kpi_agent import get_date_filter, fetch_kpi

def test_orchestrator_formats():
    # Test the formats that the orchestrator might be sending
    test_queries = [
        "KPI Name: home-loan attrition rate, Months: 2025-02-01, 2025-03-01, 2025-04-01, 2025-05-01",
        "home-loan attrition rate Months: 2025-02-01, 2025-03-01, 2025-04-01, 2025-05-01",
        "Get the home-loan attrition rate for the months of February, March, April, and May 2025",
        "home loan attrition rate last 4 months",
        "last 4 months home loan attrition rate"
    ]
    
    for query in test_queries:
        print(f"\n=== Testing query: {query} ===")
        
        # Test date filter
        date_filter = get_date_filter(query)
        print(f"Date filter: {date_filter}")
        
        if date_filter:
            # Test full fetch_kpi function
            result = fetch_kpi(query)
            if "results" in result:
                print("SUCCESS!")
                lines = result["results"].split('\n')
                data_points = [line for line in lines if '2025-' in line and '%' in line]
                print(f"Found {len(data_points)} data points:")
                for point in data_points:
                    print(f"  {point}")
            else:
                print("FAILED:", result.get("error", "Unknown error"))
        else:
            print("No date filter generated - this will ask for time period")

if __name__ == "__main__":
    test_orchestrator_formats() 