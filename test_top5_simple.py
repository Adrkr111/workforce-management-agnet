#!/usr/bin/env python3

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

def test_top5_kpi():
    """Test the KPI agent returns top 5 results in human format"""
    try:
        from agents.kpi_agent import fetch_kpi
        
        print("Testing Top 5 KPI Results...")
        print("=" * 50)
        
        # Test 1: Simple query
        print("\n1. Testing 'home loan attrition':")
        query1 = "home loan attrition"
        result1 = fetch_kpi(query1)
        print(f"Query: {query1}")
        if 'results' in result1:
            print("SUCCESS! Results:")
            print(result1['results'])
        elif 'error' in result1:
            print(f"Error: {result1['error']}")
        else:
            print(f"Unexpected result: {result1}")
        
        # Test 2: Attrition rate query  
        print("\n2. Testing 'attrition rate':")
        query2 = "attrition rate"
        result2 = fetch_kpi(query2)
        print(f"Query: {query2}")
        if 'results' in result2:
            print("SUCCESS! Results:")
            print(result2['results'])
        elif 'error' in result2:
            print(f"Error: {result2['error']}")
        else:
            print(f"Unexpected result: {result2}")
            
        # Test 3: Rate query
        print("\n3. Testing 'rate':")
        query3 = "rate"
        result3 = fetch_kpi(query3)
        print(f"Query: {query3}")
        if 'results' in result3:
            print("SUCCESS! Results:")
            print(result3['results'])
        elif 'error' in result3:
            print(f"Error: {result3['error']}")
        else:
            print(f"Unexpected result: {result3}")
            
    except Exception as e:
        print(f"Test failed with error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_top5_kpi() 