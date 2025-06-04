import os
os.environ["GOOGLE_CLOUD_PROJECT"] = "gen-lang-client-0449161426"
os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = "/Users/aindrilkar/Downloads/gen-lang-client-0449161426-fe873ba9d72d.json"
os.environ["GEMINI_API_KEY"] = "AIzaSyDWYTRBtrMLETqTle3LuTLSSng5cAiE_aA"

from agents.kpi_agent import get_date_filter

def test_orchestrator_format():
    # Test the exact format the orchestrator sends
    query = "KPI Name: home-loan attrition rate, Months: 2025-02-01, 2025-03-01, 2025-04-01, 2025-05-01"
    
    print(f"Testing exact orchestrator query: {query}")
    print(f"Lowercase version: {query.lower()}")
    
    # Test our regex
    import re
    months_match = re.search(r"months:\s*([0-9,\-\s]+)", query.lower())
    print(f"Regex match: {months_match}")
    if months_match:
        date_string = months_match.group(1)
        print(f"Extracted date string: '{date_string}'")
        dates = re.findall(r"\d{4}-\d{2}-\d{2}", date_string)
        print(f"Found dates: {dates}")
    
    # Test the actual function
    date_filter = get_date_filter(query)
    print(f"Final date filter: {date_filter}")

if __name__ == "__main__":
    test_orchestrator_format() 