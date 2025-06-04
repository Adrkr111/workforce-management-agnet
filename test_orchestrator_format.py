import os
os.environ["GOOGLE_CLOUD_PROJECT"] = "gen-lang-client-0449161426"
os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = "/Users/aindrilkar/Downloads/gen-lang-client-0449161426-fe873ba9d72d.json"
os.environ["GEMINI_API_KEY"] = "AIzaSyDWYTRBtrMLETqTle3LuTLSSng5cAiE_aA"

from agents.kpi_agent import get_date_filter, fetch_kpi

def test_exact_orchestrator_format():
    # Test the exact format from the debug logs
    query = "kpi-attrition-rate department-home-loan range-4-months start-2025-02-01 end-2025-05-31"
    
    print(f"Testing exact orchestrator query: {query}")
    
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
        print("FAILED: No date filter generated")

if __name__ == "__main__":
    test_exact_orchestrator_format() 