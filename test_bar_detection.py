#!/usr/bin/env python3
"""
Test script to verify bar plot detection is working correctly
"""

from agents.visualization_agent import EnterpriseVisualizationAgent

def test_bar_plot_detection():
    """Test that bar plot requests are correctly detected"""
    agent = EnterpriseVisualizationAgent()
    
    # Test data with explicit bar plot request
    test_request = """
    Data-Visualization-Agent: Please create a bar plot for the logistics forecast data:
    2025-06: 2845
    2025-07: 2843
    2025-08: 2519
    2025-09: 3499
    2025-10: 3597
    """
    
    print("🧪 Testing bar plot detection...")
    print(f"Request: {test_request[:100]}...")
    
    try:
        result = agent.create_visualization(test_request)
        print(f"✅ Visualization created successfully")
        print(f"Result type: {type(result)}")
        
        # Check if result contains bar chart indicators
        if 'bar' in str(result).lower():
            print("✅ Result appears to contain bar chart data")
        else:
            print("❌ Result may not contain bar chart data")
            
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    test_bar_plot_detection() 