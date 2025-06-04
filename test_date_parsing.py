#!/usr/bin/env python3

import re
from datetime import datetime
from dateutil.relativedelta import relativedelta

def get_date_filter(query: str) -> dict:
    """
    Extract date or date range from query and return ChromaDB filter
    """
    current_date = datetime.now()
    print(f"Debug - Processing date filter from query: {query}")
    print(f"Debug - Current date: {current_date}")
    
    query_lower = query.lower()
    
    # Handle orchestrator's month-YYYY-MM-DD format
    if "month-" in query_lower:
        try:
            month_match = re.search(r"month-(\d{4}-\d{2}-\d{2})", query_lower)
            if month_match:
                date_str = month_match.group(1)
                print(f"Debug - Found month date: {date_str}")
                return {"created_date": date_str}
        except Exception as e:
            print(f"Debug - Error parsing month date: {str(e)}")
    
    # Handle "last X months" - this should be checked FIRST before specific dates
    if "last" in query_lower and ("months" in query_lower or "month" in query_lower):
        try:
            # Extract number of months
            if "last month" in query_lower and "months" not in query_lower:
                num_months = 1
            else:
                # Look for patterns like "last 4 months" or "4 months"
                month_match = re.search(r"(?:last\s+)?(\d+)\s+months?", query_lower)
                if month_match:
                    num_months = int(month_match.group(1))
                else:
                    num_months = 1
                
            print(f"Debug - Extracting data for last {num_months} months")
            
            # Generate list of dates for the last N months
            dates = []
            current_month = current_date.replace(day=1)
            
            for i in range(num_months):
                month_date = current_month - relativedelta(months=i+1)  # Start from previous month
                dates.append(month_date.strftime("%Y-%m-%d"))
            
            print(f"Debug - Date list for last {num_months} months: {dates}")
            
            return {"created_date": {"$in": dates}}
            
        except Exception as e:
            print(f"Debug - Error parsing month range: {str(e)}")
            # Fall through to other parsing methods
    
    # Handle "previous X months" (alternative to "last X months")
    if "previous" in query_lower and ("months" in query_lower or "month" in query_lower):
        try:
            # Extract number of months
            if "previous month" in query_lower and "months" not in query_lower:
                num_months = 1
            else:
                # Look for patterns like "previous 4 months" or "4 months"
                month_match = re.search(r"(?:previous\s+)?(\d+)\s+months?", query_lower)
                if month_match:
                    num_months = int(month_match.group(1))
                else:
                    num_months = 1
                
            print(f"Debug - Extracting data for previous {num_months} months")
            
            # Generate list of dates for the previous N months
            dates = []
            current_month = current_date.replace(day=1)
            
            for i in range(num_months):
                month_date = current_month - relativedelta(months=i+1)  # Start from previous month
                dates.append(month_date.strftime("%Y-%m-%d"))
            
            print(f"Debug - Date list for previous {num_months} months: {dates}")
            
            return {"created_date": {"$in": dates}}
            
        except Exception as e:
            print(f"Debug - Error parsing previous month range: {str(e)}")
    
    # Handle orchestrator's start-date end-date format
    if "start-" in query_lower and "end-" in query_lower:
        try:
            # Extract start and end dates
            start_match = re.search(r"start-(\d{4}-\d{2}-\d{2})", query_lower)
            end_match = re.search(r"end-(\d{4}-\d{2}-\d{2})", query_lower)
            
            print(f"Debug - Start match: {start_match}")
            print(f"Debug - End match: {end_match}")
            
            if start_match and end_match:
                start_date = datetime.strptime(start_match.group(1), "%Y-%m-%d")
                end_date = datetime.strptime(end_match.group(1), "%Y-%m-%d")
                
                print(f"Debug - Parsed start date: {start_date}")
                print(f"Debug - Parsed end date: {end_date}")
                
                # Generate list of first days of each month in the range
                dates = []
                current = start_date.replace(day=1)
                while current <= end_date:
                    dates.append(current.strftime("%Y-%m-%d"))
                    current = current + relativedelta(months=1)
                
                print(f"Debug - Date list for start-end range: {dates}")
                return {"created_date": {"$in": dates}}
        except Exception as e:
            print(f"Debug - Error parsing start-end date range: {str(e)}")
    
    print("Debug - No date filter found in query")
    return None

def test_queries():
    """Test different query formats"""
    test_cases = [
        "kpi-attrition-rate department-home-loan month-2025-05-01",
        "kpi-attrition-rate department-home-loan start-2025-02-01 end-2025-05-31",
        "home-loan attrition rate previous 4 months",
        "home-loan attrition rate last month",
        "kpi-attrition-rate department-home-loan range-4-months start-2025-02-01 end-2025-05-31"
    ]
    
    for i, query in enumerate(test_cases, 1):
        print(f"\n{'='*50}")
        print(f"Test {i}: {query}")
        print('='*50)
        result = get_date_filter(query)
        print(f"Result: {result}")

if __name__ == "__main__":
    test_queries() 