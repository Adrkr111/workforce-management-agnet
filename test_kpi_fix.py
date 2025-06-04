#!/usr/bin/env python3

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from agents.kpi_agent import fetch_kpi

def test_kpi_fetch():
    """Test the KPI fetch function to ensure it returns actual data"""
    print("Testing KPI fetch function...")
    print("=" * 50)
    
    # Test 1: Last 4 months query (orchestrator format)
    print("\n1. Testing orchestrator format for last 4 months:")
    query1 = "kpi-attrition-rate department-home-loan range-4-months start-2025-02-01 end-2025-05-31"
    result1 = fetch_kpi(query1)
    print(f"Query: {query1}")
    print(f"Result: {result1}")
    
    # Test 2: Single month query
    print("\n2. Testing single month query:")
    query2 = "kpi-attrition-rate department-home-loan month-2025-02-01"
    result2 = fetch_kpi(query2)
    print(f"Query: {query2}")
    print(f"Result: {result2}")
    
    # Test 3: Last 4 months with natural language
    print("\n3. Testing natural language last 4 months:")
    query3 = "home-loan attrition rate last 4 months"
    result3 = fetch_kpi(query3)
    print(f"Query: {query3}")
    print(f"Result: {result3}")
    
    print("\n" + "=" * 50)
    print("Test completed!")

if __name__ == "__main__":
    test_kpi_fetch() 