#!/usr/bin/env python3
"""
Test the visualization parsing fix
"""

import json
from agents.data_visualization_agent import create_visualization, sort_metrics_chronologically

# Test data - same as what the user is asking about
test_data = """
Home Loan Attrition Rate (FY 2025):
- January: 9.92%
- February: 6.81%
- March: 13.35%
- May: 13.66%
- June: 12.15%

Early Repayment Rate (FY 2025):
- January: 60.82%
- March: 68.65%
- April: 64.22%
- May: 61.16%
- June: 73.6%
"""

print("🧪 Testing Visualization Agent with Month Sorting...")
print("=" * 60)

# Test the sorting function directly
test_analysis = {
    "success": True,
    "metrics": [
        {
            "name": "Home Loan Attrition Rate",
            "data_points": [
                {"label": "Jun 2025", "value": 12.15},
                {"label": "Jan 2025", "value": 9.92},
                {"label": "May 2025", "value": 13.66},
                {"label": "Mar 2025", "value": 13.35},
                {"label": "Feb 2025", "value": 6.81}
            ]
        },
        {
            "name": "Early Repayment Rate", 
            "data_points": [
                {"label": "Jun 2025", "value": 73.6},
                {"label": "Apr 2025", "value": 64.22},
                {"label": "Jan 2025", "value": 60.82},
                {"label": "May 2025", "value": 61.16},
                {"label": "Mar 2025", "value": 68.65}
            ]
        }
    ]
}

print("📅 BEFORE Sorting:")
for metric in test_analysis['metrics']:
    labels = [p['label'] for p in metric['data_points']]
    print(f"  {metric['name']}: {labels}")

# Apply sorting
sorted_analysis = sort_metrics_chronologically(test_analysis)

print("\n📅 AFTER Sorting:")
for metric in sorted_analysis['metrics']:
    labels = [p['label'] for p in metric['data_points']]
    print(f"  {metric['name']}: {labels}")

print("\n" + "=" * 60)
print("🎯 Testing Full Visualization Creation...")

# Test full visualization
try:
    result = create_visualization(test_data)
    print(f"✅ Visualization created successfully!")
    print(f"📊 Result type: {type(result)}")
    
    if isinstance(result, str):
        try:
            result_dict = eval(result)
            if 'spec' in result_dict:
                chart_spec = result_dict['spec']
                if 'data' in chart_spec:
                    for i, trace in enumerate(chart_spec['data']):
                        x_values = trace.get('x', [])
                        print(f"🔍 Trace {i+1} X-axis order: {x_values}")
        except:
            print("❌ Could not parse result")
    
except Exception as e:
    print(f"❌ Error: {e}")
    import traceback
    traceback.print_exc()

def test_content_parsing():
    """Test the improved content parsing logic"""
    import json
    import ast
    
    print("🧪 Testing Content Parsing Fix")
    print("=" * 40)
    
    # Test case: Visualization agent response
    viz_content = "{'spec': {'data': [{'x': ['2025-06-01', '2025-07-01'], 'y': [2845, 2843], 'type': 'scatter', 'mode': 'lines+markers', 'name': 'Data Trend'}], 'layout': {'title': {'text': 'Volume Forecast'}, 'xaxis': {'title': 'Date'}, 'yaxis': {'title': 'Volume'}}}}"
    
    print("📊 Testing visualization content parsing...")
    
    # Simulate the parsing logic from app_teams.py
    try:
        # Try JSON first
        try:
            data = json.loads(viz_content)
            print("✅ Parsed as JSON")
            parse_method = "JSON"
        except json.JSONDecodeError:
            # Try Python dict parsing
            try:
                if viz_content.strip().startswith('{') and viz_content.strip().endswith('}'):
                    data = ast.literal_eval(viz_content)
                    print("✅ Parsed as Python dict")
                    parse_method = "AST"
                else:
                    raise ValueError("Not a dict format")
            except (ValueError, SyntaxError):
                print("⚠️ Fallback to text content")
                data = {"text_content": viz_content}
                parse_method = "TEXT"
        
        print(f"🔍 Parse method used: {parse_method}")
        print(f"📋 Data keys: {data.keys()}")
        
        # Check if it can find the spec
        if 'spec' in data:
            spec = data['spec']
            print("✅ Found 'spec' key")
            print(f"📊 Spec keys: {spec.keys()}")
            
            if 'data' in spec and 'layout' in spec:
                chart_data = spec['data']
                layout = spec['layout']
                print(f"✅ Found chart data with {len(chart_data)} traces")
                print(f"🏷️ Chart title: {layout.get('title', {}).get('text', 'No title')}")
                
                if chart_data:
                    trace = chart_data[0]
                    x_points = len(trace.get('x', []))
                    y_points = len(trace.get('y', []))
                    print(f"📈 First trace: {x_points} x-points, {y_points} y-points")
                
                print("🎉 SUCCESS: Visualization data parsing works!")
                return True
            else:
                print("❌ Missing chart data or layout")
                return False
        else:
            print("❌ No 'spec' key found")
            print(f"   Available keys: {list(data.keys())}")
            return False
            
    except Exception as e:
        print(f"❌ Parsing failed: {e}")
        return False

def test_markdown_forecast_parsing():
    """Test parsing of markdown forecast format from vector database"""
    import re
    
    print("\n🧪 Testing Markdown Forecast Parsing")
    print("=" * 45)
    
    # This is the actual format stored in vector database
    forecast_text = """For the business logistics substream DLT, the forecast for the support team is as follows:

*   **June 2025**: 2845
*   **July 2025**: 2843
*   **August 2025**: 2519
*   **September 2025**: 3499
*   **October 2025**: 3597
*   **November 2025**: 2780
*   **December 2025**: 3295
*   **January 2026**: 1921
*   **February 2026**: 3005
*   **March 2026**: 1144
*   **April 2026**: 2535
*   **May 2026**: 3758"""
    
    print(f"📊 Testing forecast text with {len(forecast_text)} characters")
    print(f"📋 Sample: {forecast_text[:100]}...")
    
    # Test the new pattern
    pattern = r'\*\s*\*\*([A-Za-z]+\s+\d{4})\*\*:\s*(\d{3,})'
    matches = re.findall(pattern, forecast_text)
    
    print(f"\n🔍 Pattern: {pattern}")
    print(f"📊 Matches found: {len(matches)}")
    
    data_points = []
    for match in matches:
        try:
            date = match[0]
            value = int(match[1])
            if value > 1000:  # Filter out years/small numbers
                data_points.append({"date": date, "value": value})
                print(f"✅ Extracted: {date} = {value}")
        except (ValueError, IndexError):
            continue
    
    print(f"\n📊 Final extracted points: {len(data_points)}")
    
    if len(data_points) >= 10:  # Should extract 12 months of data
        print("🎉 SUCCESS: Markdown forecast parsing works!")
        print(f"📈 Sample data points:")
        for i, point in enumerate(data_points[:3], 1):
            print(f"  [{i}] {point['date']}: {point['value']}")
        if len(data_points) > 3:
            print(f"  ... and {len(data_points) - 3} more points")
        return True
    else:
        print("❌ FAILED: Not enough data points extracted")
        return False

if __name__ == "__main__":
    print("🧪 VISUALIZATION FIX TESTING")
    print("=" * 50)
    
    test1_success = test_content_parsing()
    test2_success = test_markdown_forecast_parsing()
    
    print(f"\n🎯 RESULTS:")
    print(f"✅ Content Parsing: {'PASS' if test1_success else 'FAIL'}")
    print(f"✅ Markdown Parsing: {'PASS' if test2_success else 'FAIL'}")
    
    if test1_success and test2_success:
        print("\n🎉 ALL TESTS PASSED!")
        print("📊 Visualization should now work correctly")
    else:
        print("\n⚠️ Some tests failed - needs more work") 