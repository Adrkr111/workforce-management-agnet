#!/usr/bin/env python3

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from agents.kpi_agent import fetch_kpi

def test_kpi_formats():
    """Test various KPI query formats"""
    print("Testing KPI fetch function with various formats...")
    print("=" * 50)
    
    # Test 1: Orchestrator format with month-
    print("\n1. Testing orchestrator month format:")
    query1 = "kpi-attrition-rate department-home-loan month-2025-05-01"
    result1 = fetch_kpi(query1)
    print(f"Query: {query1}")
    print(f"Result: {result1}")
    
    # Test 2: Simple last month
    print("\n2. Testing 'last month':")
    query2 = "home-loan attrition rate last month"
    result2 = fetch_kpi(query2)
    print(f"Query: {query2}")
    print(f"Result: {result2}")
    
    # Test 3: Previous 4 months
    print("\n3. Testing 'previous 4 months':")
    query3 = "home-loan attrition rate previous 4 months"
    result3 = fetch_kpi(query3)
    print(f"Query: {query3}")
    print(f"Result: {result3}")
    
    # Test 4: Date range format
    print("\n4. Testing date range format:")
    query4 = "kpi-attrition-rate department-home-loan start-2025-02-01 end-2025-05-31"
    result4 = fetch_kpi(query4)
    print(f"Query: {query4}")
    print(f"Result: {result4}")
    
    print("\n" + "=" * 50)
    print("Test complete!")

if __name__ == "__main__":
    test_kpi_formats() 