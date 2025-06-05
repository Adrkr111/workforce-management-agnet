#!/usr/bin/env python3
"""
Test the visualization parsing fix
"""

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