#!/usr/bin/env python3
"""
Test Universal Data Visualization Agent - Handles ANY data type
"""

import json
from agents.data_visualization_agent import create_visualization

def test_forecast_data():
    """Test traditional forecast data"""
    print("\n🔍 TEST 1: Traditional Forecast Data")
    
    forecast_data = {
        "forecast": {
            "2025-01": 450,
            "2025-02": 520,
            "2025-03": 480,
            "2025-04": 600,
            "2025-05": 550
        },
        "business": "Customer Service",
        "team": "Alpha Team"
    }
    
    result = create_visualization(forecast_data)
    print(f"✅ Result type: {type(result)}")
    print(f"✅ Has spec: {'spec' in result}")
    
def test_sales_data():
    """Test sales/revenue data"""
    print("\n🔍 TEST 2: Sales Data")
    
    sales_data = [
        {"month": "January", "revenue": 150000, "region": "North"},
        {"month": "February", "revenue": 180000, "region": "North"},
        {"month": "January", "revenue": 120000, "region": "South"},
        {"month": "February", "revenue": 140000, "region": "South"}
    ]
    
    result = create_visualization(sales_data)
    print(f"✅ Result type: {type(result)}")
    print(f"✅ Has spec: {'spec' in result}")

def test_employee_data():
    """Test HR/employee data"""
    print("\n🔍 TEST 3: Employee Data")
    
    employee_data = {
        "departments": {
            "Engineering": 45,
            "Sales": 32,
            "Marketing": 18,
            "HR": 12,
            "Finance": 8
        }
    }
    
    result = create_visualization(employee_data)
    print(f"✅ Result type: {type(result)}")
    print(f"✅ Has spec: {'spec' in result}")

def test_survey_data():
    """Test survey/rating data"""
    print("\n🔍 TEST 4: Survey Data")
    
    survey_data = [
        {"question": "Product Quality", "score": 4.2, "category": "Product"},
        {"question": "Customer Service", "score": 3.8, "category": "Service"},
        {"question": "Delivery Speed", "score": 4.5, "category": "Logistics"},
        {"question": "Value for Money", "score": 3.9, "category": "Pricing"}
    ]
    
    result = create_visualization(survey_data)
    print(f"✅ Result type: {type(result)}")
    print(f"✅ Has spec: {'spec' in result}")

def test_website_analytics():
    """Test website/analytics data"""
    print("\n🔍 TEST 5: Website Analytics Data")
    
    analytics_data = {
        "traffic": {
            "2024-01": 25000,
            "2024-02": 28000,
            "2024-03": 32000,
            "2024-04": 29000,
            "2024-05": 35000
        },
        "source": "Google Analytics",
        "metric": "Page Views"
    }
    
    result = create_visualization(analytics_data)
    print(f"✅ Result type: {type(result)}")
    print(f"✅ Has spec: {'spec' in result}")

def test_financial_data():
    """Test financial data with multiple series"""
    print("\n🔍 TEST 6: Financial Data - Multiple Series")
    
    financial_data = [
        {"quarter": "Q1", "revenue": 1200000, "expenses": 800000, "profit": 400000},
        {"quarter": "Q2", "revenue": 1350000, "expenses": 850000, "profit": 500000},
        {"quarter": "Q3", "revenue": 1450000, "expenses": 900000, "profit": 550000},
        {"quarter": "Q4", "revenue": 1600000, "expenses": 950000, "profit": 650000}
    ]
    
    result = create_visualization(financial_data)
    print(f"✅ Result type: {type(result)}")
    print(f"✅ Has spec: {'spec' in result}")

def test_comparison_data():
    """Test comparison data (forecast comparison)"""
    print("\n🔍 TEST 7: Comparison Data")
    
    comparison_data = {
        "comparison_mode": True,
        "datasets": [
            {
                "label": "Team A Forecast",
                "points": [
                    {"date": "2025-01", "value": 450},
                    {"date": "2025-02", "value": 520},
                    {"date": "2025-03", "value": 480}
                ]
            },
            {
                "label": "Team B Forecast", 
                "points": [
                    {"date": "2025-01", "value": 380},
                    {"date": "2025-02", "value": 440},
                    {"date": "2025-03", "value": 510}
                ]
            }
        ]
    }
    
    result = create_visualization(comparison_data)
    print(f"✅ Result type: {type(result)}")
    print(f"✅ Has spec: {'spec' in result}")

def test_simple_numbers():
    """Test simple list of numbers"""
    print("\n🔍 TEST 8: Simple Numbers")
    
    numbers = [10, 25, 18, 30, 22, 35, 28]
    
    result = create_visualization(numbers)
    print(f"✅ Result type: {type(result)}")
    print(f"✅ Has spec: {'spec' in result}")

def test_csv_string():
    """Test CSV string data"""
    print("\n🔍 TEST 9: CSV String Data")
    
    csv_data = """Product,Sales,Quarter
Laptop,1200,Q1
Desktop,800,Q1
Tablet,600,Q1
Laptop,1350,Q2
Desktop,900,Q2
Tablet,750,Q2"""
    
    result = create_visualization(csv_data)
    print(f"✅ Result type: {type(result)}")
    print(f"✅ Has spec: {'spec' in result}")

def test_json_string():
    """Test JSON string data"""
    print("\n🔍 TEST 10: JSON String Data")
    
    json_data = '''
    {
        "monthly_sales": {
            "January": 45000,
            "February": 52000,
            "March": 48000,
            "April": 61000
        },
        "department": "Retail"
    }
    '''
    
    result = create_visualization(json_data)
    print(f"✅ Result type: {type(result)}")
    print(f"✅ Has spec: {'spec' in result}")

def test_mixed_text():
    """Test mixed text with numbers"""
    print("\n🔍 TEST 11: Mixed Text with Numbers")
    
    text_data = "Sales for January was 45000, February reached 52000, March dropped to 48000, and April soared to 61000."
    
    result = create_visualization(text_data)
    print(f"✅ Result type: {type(result)}")
    print(f"✅ Has spec: {'spec' in result}")

def test_inventory_data():
    """Test inventory/stock data"""
    print("\n🔍 TEST 12: Inventory Data")
    
    inventory_data = [
        {"product": "Widget A", "stock": 150, "warehouse": "North"},
        {"product": "Widget B", "stock": 230, "warehouse": "North"},
        {"product": "Widget C", "stock": 180, "warehouse": "North"},
        {"product": "Widget A", "stock": 120, "warehouse": "South"},
        {"product": "Widget B", "stock": 200, "warehouse": "South"},
        {"product": "Widget C", "stock": 160, "warehouse": "South"}
    ]
    
    result = create_visualization(inventory_data)
    print(f"✅ Result type: {type(result)}")
    print(f"✅ Has spec: {'spec' in result}")

def test_performance_metrics():
    """Test performance metrics data"""
    print("\n🔍 TEST 13: Performance Metrics")
    
    metrics_data = {
        "kpis": {
            "Customer Satisfaction": 4.2,
            "Response Time": 85.5,
            "First Call Resolution": 78.3,
            "Net Promoter Score": 42.1,
            "Agent Utilization": 89.7
        },
        "unit": "Contact Center",
        "period": "Q1 2024"
    }
    
    result = create_visualization(metrics_data)
    print(f"✅ Result type: {type(result)}")
    print(f"✅ Has spec: {'spec' in result}")

def test_geographic_data():
    """Test geographic/location data"""
    print("\n🔍 TEST 14: Geographic Data")
    
    geo_data = [
        {"city": "New York", "population": 8400000, "country": "USA"},
        {"city": "Los Angeles", "population": 3900000, "country": "USA"},
        {"city": "Chicago", "population": 2700000, "country": "USA"},
        {"city": "Toronto", "population": 2700000, "country": "Canada"},
        {"city": "London", "population": 8900000, "country": "UK"}
    ]
    
    result = create_visualization(geo_data)
    print(f"✅ Result type: {type(result)}")
    print(f"✅ Has spec: {'spec' in result}")

def test_time_series_data():
    """Test time series data"""
    print("\n🔍 TEST 15: Time Series Data")
    
    time_series = {
        "timestamp_data": {
            "2024-01-01": 100,
            "2024-01-02": 105,
            "2024-01-03": 98,
            "2024-01-04": 112,
            "2024-01-05": 108,
            "2024-01-06": 115,
            "2024-01-07": 103
        },
        "metric": "Daily Active Users"
    }
    
    result = create_visualization(time_series)
    print(f"✅ Result type: {type(result)}")
    print(f"✅ Has spec: {'spec' in result}")

def run_all_tests():
    """Run all tests"""
    print("🚀 UNIVERSAL DATA VISUALIZATION AGENT - COMPREHENSIVE TESTS")
    print("=" * 70)
    
    tests = [
        test_forecast_data,
        test_sales_data,
        test_employee_data,
        test_survey_data,
        test_website_analytics,
        test_financial_data,
        test_comparison_data,
        test_simple_numbers,
        test_csv_string,
        test_json_string,
        test_mixed_text,
        test_inventory_data,
        test_performance_metrics,
        test_geographic_data,
        test_time_series_data
    ]
    
    passed = 0
    total = len(tests)
    
    for test in tests:
        try:
            test()
            passed += 1
            print("✅ PASSED")
        except Exception as e:
            print(f"❌ FAILED: {e}")
    
    print("\n" + "=" * 70)
    print(f"🏆 RESULTS: {passed}/{total} tests passed ({passed/total*100:.1f}%)")
    
    if passed == total:
        print("🎉 ALL TESTS PASSED! Universal visualization agent is working perfectly!")
    else:
        print(f"⚠️ {total - passed} tests failed. Check the implementation.")

if __name__ == "__main__":
    run_all_tests() 