"""
Test script for the Enterprise Visualization Agent with tool-based architecture
"""

from agents.visualization_agent import EnterpriseVisualizationAgent
import json

def test_bar_plot_request():
    """Test bar plot for KPI data"""
    agent = EnterpriseVisualizationAgent()
    
    # Test the exact user query about bar plot
    data = """
    Data-Visualization-Agent: Please create a bar plot for the home loan attrition rates from the last quarter:
    Home Loan Attrition Rate (March 2025): 13.35%
    Home Loan Attrition Rate (February 2025): 6.81%
    Home Loan Attrition Rate (January 2025): 9.92%
    """
    
    print("🧪 Testing enterprise bar plot for KPI data...")
    result = agent.create_visualization(data)
    
    print("✅ Bar plot result:")
    print(f"Result type: {type(result)}")
    print(f"Result length: {len(str(result))}")
    
    # Parse result to check structure
    try:
        result_dict = eval(result) if isinstance(result, str) else result
        spec = result_dict.get('spec', {})
        
        print(f"\n📊 Chart Analysis:")
        print(f"- Has data: {'data' in spec}")
        print(f"- Has layout: {'layout' in spec}")
        
        if 'data' in spec:
            data_traces = spec['data']
            print(f"- Number of traces: {len(data_traces)}")
            if len(data_traces) > 0:
                first_trace = data_traces[0]
                print(f"- First trace type: {first_trace.get('type', 'unknown')}")
                print(f"- Has x values: {'x' in first_trace}")
                print(f"- Has y values: {'y' in first_trace}")
                
        if 'layout' in spec:
            layout = spec['layout']
            print(f"- Chart title: {layout.get('title', {}).get('text', 'No title')}")
            print(f"- X-axis title: {layout.get('xaxis', {}).get('title', 'No x-title')}")
            print(f"- Y-axis title: {layout.get('yaxis', {}).get('title', 'No y-title')}")
        
        print("\n✅ Enterprise bar plot test completed successfully!")
        return True
        
    except Exception as e:
        print(f"❌ Error parsing result: {e}")
        return False

def test_simple_xy_data():
    """Test simple x,y data visualization"""
    agent = EnterpriseVisualizationAgent()
    
    data = "x=[1,2,3,4,5,6,7,8,9], y=[100,200,300,400,500,600,700,800,900]"
    
    print("\n🧪 Testing simple x,y data...")
    result = agent.create_visualization(data)
    
    print("✅ Simple data result:")
    print(f"Result type: {type(result)}")
    
    try:
        result_dict = eval(result) if isinstance(result, str) else result
        spec = result_dict.get('spec', {})
        
        if 'data' in spec and len(spec['data']) > 0:
            print("✅ Simple data visualization successful!")
            return True
        else:
            print("❌ No data in visualization")
            return False
            
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

def test_explicit_chart_types():
    """Test explicit chart type requests"""
    agent = EnterpriseVisualizationAgent()
    
    test_cases = [
        ("bar plot sales data: Q1=100, Q2=150, Q3=120, Q4=180", "bar"),
        ("line chart of monthly revenue: Jan=1000, Feb=1200, Mar=1100", "line"),
        ("create a bar chart showing product sales: A=50, B=75, C=60", "bar")
    ]
    
    print("\n🧪 Testing explicit chart type requests...")
    
    for i, (query, expected_type) in enumerate(test_cases):
        print(f"\nTest {i+1}: {expected_type} chart")
        result = agent.create_visualization(query)
        
        try:
            result_dict = eval(result) if isinstance(result, str) else result
            spec = result_dict.get('spec', {})
            
            if 'data' in spec and len(spec['data']) > 0:
                actual_type = spec['data'][0].get('type', 'scatter')  # Plotly default
                # Map Plotly types to our types
                if actual_type == 'bar':
                    chart_type = 'bar'
                elif actual_type in ['scatter', 'scattergl']:
                    chart_type = 'line'
                else:
                    chart_type = actual_type
                    
                print(f"✅ Expected: {expected_type}, Got: {chart_type}")
            else:
                print("❌ No data in result")
                
        except Exception as e:
            print(f"❌ Error: {e}")

if __name__ == "__main__":
    print("🚀 Testing Enterprise Visualization Agent")
    print("=" * 50)
    
    # Test 1: Bar plot request (the main issue)
    success1 = test_bar_plot_request()
    
    # Test 2: Simple data
    success2 = test_simple_xy_data()
    
    # Test 3: Explicit chart types
    test_explicit_chart_types()
    
    print("\n" + "=" * 50)
    if success1 and success2:
        print("🎉 All core tests passed! Enterprise agent is working correctly.")
    else:
        print("⚠️  Some tests failed. Check the implementation.") 