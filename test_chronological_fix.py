#!/usr/bin/env python3
"""
Test the BULLETPROOF chronological sorting fix
"""

import json
import sys
import os

# Add agents to path
sys.path.append(os.path.join(os.path.dirname(__file__), 'agents'))

from agents.data_visualization_agent_fixed import create_visualization

def test_home_loan_chronological_fix():
    """Test the exact Home Loan data that was showing wrong order"""
    
    print("🎯 TESTING BULLETPROOF CHRONOLOGICAL SORTING FIX")
    print("=" * 70)
    
    # Exact data from the user's issue - notice missing February and April
    test_data = """
    Home Loan Attrition Rate and Early Repayment Rate Correlation Analysis (FY 2025):
    
    Home Loan Attrition Rate (FY 2025):
    - January 2025: 9.92%
    - February 2025: 6.81%
    - March 2025: 13.35%
    - May 2025: 13.66%
    - June 2025: 12.15%
    
    Early Repayment Rate for Home Loans (FY 2025):
    - January 2025: 60.82%
    - March 2025: 68.65%
    - April 2025: 64.22%
    - May 2025: 61.16%
    - June 2025: 73.6%
    
    Analysis shows positive correlation: when early repayment increased from 60.82% to 68.65%, 
    attrition increased from 9.92% to 13.35%, suggesting customers are refinancing with competitors.
    """
    
    print("📋 Input Data Analysis:")
    print("   📊 Attrition Rate has: Jan, Feb, Mar, May, Jun (missing Apr)")
    print("   📊 Early Repayment has: Jan, Mar, Apr, May, Jun (missing Feb)")
    print("   📅 Expected chronological order: Jan → Feb → Mar → Apr → May → Jun")
    print()
    
    # Test the visualization
    print("🔧 Creating visualization with BULLETPROOF sorting...")
    try:
        result = create_visualization(test_data)
        
        # Parse the result
        if isinstance(result, str):
            result_data = eval(result)  # Parse string representation
        else:
            result_data = result
            
        spec = result_data.get('spec', {})
        data_traces = spec.get('data', [])
        layout = spec.get('layout', {})
        
        print("✅ VISUALIZATION RESULTS:")
        print(f"   📊 Chart Title: {layout.get('title', 'N/A')}")
        print(f"   📈 Number of traces: {len(data_traces)}")
        
        # Check X-axis configuration
        xaxis = layout.get('xaxis', {})
        category_array = xaxis.get('categoryarray', [])
        
        print(f"\n📅 X-AXIS CONFIGURATION:")
        print(f"   🔧 Type: {xaxis.get('type', 'N/A')}")
        print(f"   🔧 Category Order: {xaxis.get('categoryorder', 'N/A')}")
        print(f"   📅 Forced Timeline: {category_array}")
        
        # Analyze each trace
        for i, trace in enumerate(data_traces, 1):
            trace_name = trace.get('name', f'Trace {i}')
            x_values = trace.get('x', [])
            y_values = trace.get('y', [])
            
            print(f"\n📊 TRACE {i}: {trace_name}")
            print(f"   📅 X-values: {x_values}")
            print(f"   📈 Y-values: {y_values}")
            
            # Check for proper chronological order
            expected_order = ["January 2025", "February 2025", "March 2025", "April 2025", "May 2025", "June 2025"]
            if x_values == expected_order:
                print(f"   ✅ PERFECT chronological order!")
            else:
                print(f"   ❌ Order issue detected")
                print(f"   📋 Expected: {expected_order}")
                print(f"   📋 Actual: {x_values}")
        
        # Overall assessment
        print(f"\n🎯 BULLETPROOF FIX ASSESSMENT:")
        if category_array == ["January 2025", "February 2025", "March 2025", "April 2025", "May 2025", "June 2025"]:
            print("   ✅ COMPLETE TIMELINE: Perfect chronological order enforced")
        else:
            print("   ❌ TIMELINE ISSUE: Chronological order not properly enforced")
            
        if all(trace.get('x', []) == category_array for trace in data_traces):
            print("   ✅ ALL TRACES: Using consistent chronological X-axis")
        else:
            print("   ❌ TRACE INCONSISTENCY: Some traces not using complete timeline")
            
        # Check for proper gap handling
        gap_handling_correct = True
        for trace in data_traces:
            y_values = trace.get('y', [])
            if len(y_values) == len(category_array):
                none_count = sum(1 for val in y_values if val is None)
                print(f"   📊 {trace.get('name', 'Trace')}: {none_count} gap(s) properly handled")
            else:
                gap_handling_correct = False
                print(f"   ❌ {trace.get('name', 'Trace')}: Length mismatch with timeline")
        
        if gap_handling_correct:
            print("   ✅ GAP HANDLING: Missing data points properly represented as None")
        else:
            print("   ❌ GAP HANDLING: Issues with missing data representation")
            
        print(f"\n🏆 FINAL VERDICT:")
        if (category_array == ["January 2025", "February 2025", "March 2025", "April 2025", "May 2025", "June 2025"] and
            all(trace.get('x', []) == category_array for trace in data_traces) and
            gap_handling_correct):
            print("   🎉 BULLETPROOF FIX SUCCESSFUL!")
            print("   📅 Chronological order: PERFECT")
            print("   📊 Gap handling: PERFECT") 
            print("   🔧 X-axis enforcement: PERFECT")
        else:
            print("   ⚠️  PARTIAL SUCCESS - Some issues remain")
            
    except Exception as e:
        print(f"❌ Test failed with error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_home_loan_chronological_fix() 