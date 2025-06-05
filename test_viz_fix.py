#!/usr/bin/env python3
"""
Test the fixed visualization functions
"""

from agents.data_visualization_agent import create_visualization, create_visualization_with_pandas
import json

# Test data in the format that's being sent to visualization
test_data = {
    "business": "logistics",
    "substream": "dlt",
    "team": "support",
    "forecast_data": [
        {"date": "2025-06-01", "value": 2845},
        {"date": "2025-07-01", "value": 2843},
        {"date": "2025-08-01", "value": 2519},
        {"date": "2025-09-01", "value": 3499},
        {"date": "2025-10-01", "value": 3597},
        {"date": "2025-11-01", "value": 2780},
        {"date": "2025-12-01", "value": 3295},
        {"date": "2026-01-01", "value": 1921},
        {"date": "2026-02-01", "value": 3005},
        {"date": "2026-03-01", "value": 1144},
        {"date": "2026-04-01", "value": 2535},
        {"date": "2026-05-01", "value": 3758}
    ]
}

print("🧪 TESTING VISUALIZATION FIXES")
print("=" * 50)

# Convert to JSON string as it would be passed to the function
json_data = json.dumps(test_data)
print(f"📦 Test data: {len(test_data['forecast_data'])} points")
print(f"📋 Sample: {test_data['forecast_data'][0]} to {test_data['forecast_data'][-1]}")

print("\n1️⃣ Testing Enhanced Plotly Visualization:")
print("-" * 40)
try:
    plotly_result = create_visualization(json_data)
    print(f"✅ Plotly Result Type: {type(plotly_result)}")
    
    if 'spec' in plotly_result:
        spec = plotly_result['spec']
        if 'data' in spec and len(spec['data']) > 0:
            trace = spec['data'][0]
            x_data = trace.get('x', [])
            y_data = trace.get('y', [])
            print(f"📊 X-axis data: {len(x_data)} points - {x_data[:3]}... to {x_data[-1] if x_data else 'none'}")
            print(f"📊 Y-axis data: {len(y_data)} points - {y_data[:3]}... to {y_data[-1] if y_data else 'none'}")
            print(f"📋 Chart title: {spec.get('layout', {}).get('title', {}).get('text', 'No title')}")
            
            # Check if we have real data
            if len(x_data) > 1 and len(y_data) > 1 and not (x_data == ['Data'] and y_data == [1]):
                print("✅ SUCCESS: Real data extracted correctly!")
            else:
                print("❌ FAIL: Generic fallback data detected")
        else:
            print("❌ FAIL: No chart data found")
    else:
        print("❌ FAIL: No spec found in result")
        
except Exception as e:
    print(f"❌ ERROR: {e}")

print("\n2️⃣ Testing Pandas Visualization:")
print("-" * 40)
try:
    pandas_result = create_visualization_with_pandas(json_data)
    print(f"✅ Pandas Result Type: {type(pandas_result)}")
    
    if 'png_base64' in pandas_result:
        png_data = pandas_result['png_base64']
        title = pandas_result.get('title', 'No title')
        data_points = pandas_result.get('data_points', 0)
        
        print(f"📊 PNG data length: {len(png_data)} characters")
        print(f"📋 Chart title: {title}")
        print(f"📊 Data points: {data_points}")
        
        # Save PNG for inspection
        import base64
        png_bytes = base64.b64decode(png_data)
        with open('test_pandas_chart.png', 'wb') as f:
            f.write(png_bytes)
        print("✅ SUCCESS: PNG chart saved as 'test_pandas_chart.png'")
        
    else:
        print("❌ FAIL: No PNG data found")
        
except Exception as e:
    print(f"❌ ERROR: {e}")

print("\n🎯 SUMMARY:")
print("=" * 50)
print("✅ Both visualization approaches should now work correctly")
print("✅ Enhanced Plotly should extract real dates and values")
print("✅ Pandas approach should create proper DataFrame plots")
print("✅ You can check 'test_pandas_chart.png' to see the result") 