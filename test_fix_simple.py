#!/usr/bin/env python3

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from agents.kpi_agent import fetch_kpi

def test_simple_queries():
    """Test simple natural language queries"""
    print("Testing simple KPI queries...")
    print("=" * 50)
    
    # Test 1: Simple last month query
    print("\n1. Testing 'home-loan attrition rate last month':")
    query1 = "home-loan attrition rate last month"
    result1 = fetch_kpi(query1)
    print(f"Query: {query1}")
    print(f"Result: {result1}")
    
    # Test 2: Simple last 4 months query
    print("\n2. Testing 'home-loan attrition rate last 4 months':")
    query2 = "home-loan attrition rate last 4 months"
    result2 = fetch_kpi(query2)
    print(f"Query: {query2}")
    print(f"Result: {result2}")
    
    # Test 3: What the orchestrator was sending before
    print("\n3. Testing orchestrator format:")
    query3 = "kpi-attrition-rate department-home-loan month-2025-05-01"
    result3 = fetch_kpi(query3)
    print(f"Query: {query3}")
    print(f"Result: {result3}")

if __name__ == "__main__":
    test_simple_queries() 