"""
Test script for the enhanced KPI visualization agent.
"""

import json
from agents.visualization_agent import VisualizationAgent

def test_kpi_visualization():
    """Test KPI data with multiple series and missing points"""
    agent = VisualizationAgent()
    
    # Test data from user query
    data = """
    Data-Visualization-Agent: Please create a plot showing both the Home Loan Attrition Rate and the Early Repayment Rate for FY 2025 using the following data:
    Home Loan Attrition Rate (FY 2025):
    January 2025: 9.92%
    February 2025: 6.81%
    March 2025: 13.35%
    May 2025: 13.66%
    June 2025: 12.15%
    Early Repayment Rate for Home Loans (FY 2025):
    January 2025: 60.82%
    March 2025: 68.65%
    April 2025: 64.22%
    May 2025: 61.16%
    June 2025: 73.6%
    """
    
    print("🧪 Testing KPI visualization...")
    
    # Run the visualization creation
    result_str = agent.create_visualization(data)
    result = eval(result_str) # Convert string representation back to dict
    
    print("\n📊 Visualization result:")
    print(json.dumps(result, indent=2))
    
    # Assertions to validate the output
    assert 'spec' in result, "Result should contain 'spec' key"
    spec = result['spec']
    assert 'data' in spec, "Spec should contain 'data' key"
    assert len(spec['data']) == 2, "Should have two traces for the two metrics"
    
    # Check timeline
    timeline = spec['layout']['xaxis']['categoryarray']
    expected_timeline = ['January 2025', 'February 2025', 'March 2025', 'April 2025', 'May 2025', 'June 2025']
    assert timeline == expected_timeline, f"Timeline is incorrect. Expected {expected_timeline}, got {timeline}"
    
    # Check trace data
    attrition_trace = spec['data'][0]
    repayment_trace = spec['data'][1]
    
    assert attrition_trace['name'] == "Home Loan Attrition Rate"
    assert repayment_trace['name'] == "Early Repayment Rate"
    
    # Note: Using 'is None' for April value in attrition
    assert attrition_trace['y'] == [9.92, 6.81, 13.35, None, 13.66, 12.15], "Attrition data is incorrect"
    # Note: Using 'is None' for February value in repayment
    assert repayment_trace['y'] == [60.82, None, 68.65, 64.22, 61.16, 73.6], "Repayment data is incorrect"
    
    # Check for dual axis
    assert repayment_trace.get('yaxis') == 'y2', "Repayment should be on secondary y-axis"
    
    print("\n✅ KPI visualization test passed!")

if __name__ == "__main__":
    test_kpi_visualization()
    print("\n✨ All tests completed successfully!") 