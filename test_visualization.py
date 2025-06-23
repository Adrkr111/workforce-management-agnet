"""
Test script for the enhanced visualization agent
"""

from agents.visualization_agent import VisualizationAgent
import json

def test_simple_plot():
    """Test simple x,y plot"""
    agent = VisualizationAgent()
    
    # Test data from user query
    data = "x=[1,2,3,4,5,6,7,8,9], y=[100,200,300,400,500,600,700,800,900]"
    
    print("Testing simple x,y plot...")
    result = agent.create_visualization(data)
    
    print("\nVisualization result:")
    print(json.dumps(result, indent=2))
    
    assert 'spec' in result, "Result should contain 'spec' key"
    assert 'data' in result['spec'], "Spec should contain 'data' key"
    assert len(result['spec']['data']) > 0, "Should have at least one trace"
    
    trace = result['spec']['data'][0]
    assert len(trace['x']) == 9, "Should have 9 x values"
    assert len(trace['y']) == 9, "Should have 9 y values"
    
    print("✅ Simple plot test passed!")

def test_time_series():
    """Test time series data"""
    agent = VisualizationAgent()
    
    # Test forecast data
    data = """
    Month-Year Forecast Value
    2025-06 3141
    2025-07 3049
    2025-08 2965
    2025-09 2796
    2025-10 4029
    2025-11 4186
    2025-12 2775
    2026-01 4506
    2026-02 2909
    2026-03 5139
    2026-04 1351
    2026-05 4780
    """
    
    print("\nTesting time series plot...")
    result = agent.create_visualization(data)
    
    print("\nVisualization result:")
    print(json.dumps(result, indent=2))
    
    assert 'spec' in result, "Result should contain 'spec' key"
    assert 'data' in result['spec'], "Spec should contain 'data' key"
    assert len(result['spec']['data']) > 0, "Should have at least one trace"
    
    trace = result['spec']['data'][0]
    assert len(trace['x']) == 12, "Should have 12 time points"
    assert len(trace['y']) == 12, "Should have 12 values"
    
    print("✅ Time series test passed!")

if __name__ == "__main__":
    print("🧪 Running visualization agent tests...\n")
    test_simple_plot()
    test_time_series()
    print("\n✨ All tests completed!") 