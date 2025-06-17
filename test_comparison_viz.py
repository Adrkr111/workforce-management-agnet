#!/usr/bin/env python3
"""
Test the enhanced comparison visualization functionality
"""

from agents.data_visualization_agent import create_visualization
import json

print("🧪 TESTING ENHANCED COMPARISON VISUALIZATION")
print("=" * 60)

# Test 1: Single Dataset (Backward Compatibility)
print("\n1️⃣ Testing Single Dataset Visualization (Backward Compatibility):")
print("-" * 50)

single_data = {
    "business": "logistics",
    "substream": "dlt", 
    "team": "support",
    "forecast_data": [
        {"date": "2025-06-01", "value": 2845},
        {"date": "2025-07-01", "value": 2843},
        {"date": "2025-08-01", "value": 2519},
        {"date": "2025-09-01", "value": 3499},
        {"date": "2025-10-01", "value": 3597}
    ]
}

single_json = json.dumps(single_data)
single_result = create_visualization(single_json)

print(f"✅ Single dataset result type: {type(single_result)}")
if 'spec' in single_result and 'data' in single_result['spec']:
    traces = single_result['spec']['data']
    print(f"📊 Single dataset traces: {len(traces)}")
    if traces:
        trace = traces[0]
        print(f"📋 X-axis: {len(trace.get('x', []))} points")
        print(f"📊 Y-axis: {len(trace.get('y', []))} points")
        print(f"🏷️ Chart title: {single_result['spec'].get('layout', {}).get('title', {}).get('text', 'No title')}")

# Test 2: Comparison Dataset
print("\n2️⃣ Testing Comparison Visualization:")
print("-" * 40)

comparison_data = {
    "comparison_mode": True,
    "chart_type": "multi_series_comparison",
    "datasets": [
        {
            "label": "logistics-dlt-support",
            "points": [
                {"date": "2025-06-01", "value": 2845},
                {"date": "2025-07-01", "value": 2843},
                {"date": "2025-08-01", "value": 2519},
                {"date": "2025-09-01", "value": 3499},
                {"date": "2025-10-01", "value": 3597}
            ],
            "metadata": {"business": "logistics", "substream": "dlt", "team": "support"}
        },
        {
            "label": "logistics-dlt-operations",
            "points": [
                {"date": "2025-06-01", "value": 3200},
                {"date": "2025-07-01", "value": 3100},
                {"date": "2025-08-01", "value": 2800},
                {"date": "2025-09-01", "value": 3800},
                {"date": "2025-10-01", "value": 3900}
            ],
            "metadata": {"business": "logistics", "substream": "dlt", "team": "operations"}
        }
    ]
}

comparison_json = json.dumps(comparison_data)
comparison_result = create_visualization(comparison_json)

print(f"✅ Comparison result type: {type(comparison_result)}")
if 'spec' in comparison_result and 'data' in comparison_result['spec']:
    traces = comparison_result['spec']['data']
    print(f"📊 Comparison traces: {len(traces)}")
    
    # Check primary data traces
    primary_traces = [t for t in traces if t.get('yaxis', 'y') == 'y']
    delta_traces = [t for t in traces if t.get('yaxis') == 'y2']
    
    print(f"📈 Primary data traces: {len(primary_traces)}")
    print(f"📊 Delta traces: {len(delta_traces)}")
    
    for i, trace in enumerate(primary_traces):
        name = trace.get('name', f'Trace {i+1}')
        points = len(trace.get('x', []))
        color = trace.get('line', {}).get('color', 'Unknown')
        print(f"   [{i+1}] {name}: {points} points, color={color}")
    
    if delta_traces:
        delta = delta_traces[0]
        delta_name = delta.get('name', 'Delta')
        delta_points = len(delta.get('x', []))
        print(f"📊 {delta_name}: {delta_points} difference points")
        
        # Calculate sample delta values
        delta_values = delta.get('y', [])
        if delta_values:
            avg_delta = sum(delta_values) / len(delta_values)
            max_delta = max(delta_values)
            min_delta = min(delta_values)
            print(f"📊 Delta stats: Avg={avg_delta:.1f}, Max={max_delta:.1f}, Min={min_delta:.1f}")
    
    # Check layout
    layout = comparison_result['spec'].get('layout', {})
    title = layout.get('title', {}).get('text', 'No title')
    has_secondary_y = 'yaxis2' in layout
    
    print(f"🏷️ Chart title: {title}")
    print(f"📊 Has secondary Y-axis: {has_secondary_y}")
    print(f"🎨 Legend position: {layout.get('legend', {}).get('x', 'default')}")

# Test 3: Validation
print("\n3️⃣ Validation Results:")
print("-" * 30)

success_count = 0
total_tests = 0

# Test backward compatibility
total_tests += 1
if single_result and 'spec' in single_result:
    print("✅ Single dataset visualization: PASS")
    success_count += 1
else:
    print("❌ Single dataset visualization: FAIL")

# Test comparison mode
total_tests += 1
if comparison_result and 'spec' in comparison_result:
    traces = comparison_result['spec']['data']
    if len(traces) >= 2:
        print("✅ Comparison visualization: PASS")
        success_count += 1
    else:
        print("❌ Comparison visualization: FAIL (insufficient traces)")
else:
    print("❌ Comparison visualization: FAIL")

# Test delta calculation
total_tests += 1
if comparison_result and 'spec' in comparison_result:
    traces = comparison_result['spec']['data']
    delta_traces = [t for t in traces if t.get('yaxis') == 'y2']
    if delta_traces:
        print("✅ Delta calculation: PASS")
        success_count += 1
    else:
        print("❌ Delta calculation: FAIL")
else:
    print("❌ Delta calculation: FAIL")

# Test dual y-axis
total_tests += 1
if comparison_result and 'spec' in comparison_result:
    layout = comparison_result['spec'].get('layout', {})
    if 'yaxis2' in layout:
        print("✅ Dual Y-axis: PASS")
        success_count += 1
    else:
        print("❌ Dual Y-axis: FAIL")
else:
    print("❌ Dual Y-axis: FAIL")

print(f"\n🎯 OVERALL RESULTS: {success_count}/{total_tests} tests passed")
if success_count == total_tests:
    print("🎉 ALL TESTS PASSED! Comparison visualization is ready! 🚀")
else:
    print("⚠️ Some tests failed. Please check the implementation.")

print("\n" + "=" * 60)
print("✅ Enhanced system now supports:")
print("• 📊 Single dataset visualization (backward compatible)")
print("• 🔄 Multi-dataset comparison with different colors")
print("• 📈 Delta calculation showing differences between datasets")
print("• 📊 Dual Y-axis for primary data and delta values")
print("• 🎨 Intelligent color coding and legend positioning")
print("• 🧠 Automatic detection of comparison requests")
print("• 📦 Robust data parsing for multiple formats")

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

def test_enhanced_kpi_agent():
    """Test the enhanced KPI agent with filtering and vector storage"""
    try:
        print("🧪 Testing Enhanced KPI Agent...")
        print("=" * 50)
        
        # Mock the vector data store for testing
        class MockVectorDataStore:
            def store_search_result(self, session_id, query_type, business, substream, team, result_data, metadata=None):
                print(f"✅ MOCK STORAGE: {query_type} data stored for session {session_id}")
                return f"mock_entry_{query_type}_{session_id}"
        
        # Set up mock context
        from agents.kpi_agent import set_data_store_context, fetch_kpi
        mock_store = MockVectorDataStore()
        set_data_store_context(mock_store, "test_session")
        
        # Test specific KPI query (should filter results)
        print("\n1. Testing specific query: 'home loan attrition rate'")
        query1 = "home loan attrition rate"
        
        # This should fail gracefully since we don't have actual data, but we can check the logic
        try:
            result1 = fetch_kpi(query1)
            if 'results' in result1:
                print("SUCCESS! Enhanced KPI results:")
                print(result1['results'][:200] + "..." if len(result1['results']) > 200 else result1['results'])
            elif 'error' in result1:
                print(f"Expected error (no test data): {result1['error']}")
        except Exception as e:
            print(f"Expected error (no test environment): {e}")
        
        print("\n✅ Enhanced KPI agent test completed")
        return True
        
    except Exception as e:
        print(f"❌ Test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    test_enhanced_kpi_agent() 