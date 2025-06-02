import os

# Set up environment variables
os.environ["GOOGLE_CLOUD_PROJECT"] = "gen-lang-client-0449161426"
os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = "/Users/aindrilkar/Downloads/gen-lang-client-0449161426-fe873ba9d72d.json"
os.environ["GEMINI_API_KEY"] = "AIzaSyDWYTRBtrMLETqTle3LuTLSSng5cAiE_aA"

from agents.fetch_forecasting_agent import fetch_forecast

def test_fetch():
    # Test cases
    test_queries = [
        "business-energy substream-cst team-support",
        "business-tech substream-bks team-insights",
        "business-logistics substream-dlt team-support",
        "business-finance substream-prj team-marketing",
        "business-retail substream-hrm team-risk"
    ]
    
    for query in test_queries:
        print("\n" + "="*50)
        print(f"Testing query: {query}")
        print("="*50)
        
        result = fetch_forecast(query)
        if 'error' in result:
            print(f"Error: {result['error']}")
        else:
            print(result['results'])

if __name__ == "__main__":
    test_fetch() 