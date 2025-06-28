#!/usr/bin/env python3
"""
Test script to verify the visualization agent generates complete business context titles
"""

import json
import sys
import os

# Add the project directory to the path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from agents.visualization_agent import EnterpriseVisualizationAgent

def test_complete_business_title():
    """Test that the visualization agent generates complete business context titles"""
    
    print("🧪 Testing complete business context title generation...")
    
    # Create visualization agent
    viz_agent = EnterpriseVisualizationAgent()
    
    # Test data that matches the format sent by the orchestrator
    test_data = {
        "data_type": "forecast",
        "business": "logistics",
        "substream": "dlt",
        "team": "support",
        "forecast_data": [
            {"date": "June 2025", "value": 2845},
            {"date": "July 2025", "value": 2843},
            {"date": "August 2025", "value": 2519},
            {"date": "September 2025", "value": 3499},
            {"date": "October 2025", "value": 3597},
            {"date": "November 2025", "value": 2780},
            {"date": "December 2025", "value": 3295}
        ]
    }
    
    # Convert to JSON string (as the orchestrator does)
    json_data = json.dumps(test_data)
    
    # Add the visualization request prefix
    full_request = f"Data-Visualization-Agent: Please create a bar plot for the following logistics forecast data:\n\n{json_data}"
    
    print(f"📊 Input data preview: {full_request[:200]}...")
    
    try:
        # Call the visualization function
        result = viz_agent.create_visualization(full_request)
        print(f"✅ Generated visualization result")
        
        # Parse the result to check the title
        if isinstance(result, str):
            # The result is a string representation of a dict
            result_dict = eval(result)
        else:
            result_dict = result
            
        spec = result_dict.get('spec', {})
        layout = spec.get('layout', {})
        title = layout.get('title', {})
        
        if isinstance(title, dict):
            title_text = title.get('text', 'No title found')
        else:
            title_text = str(title)
            
        print(f"🏷️ Generated title: {title_text}")
        
        # Check if the title includes complete business context
        expected_parts = ['Logistics', 'DLT', 'Support', 'Team', 'Forecast']
        found_parts = [part for part in expected_parts if part in title_text]
        
        if len(found_parts) >= 4:  # Should have at least 4 of the 5 parts
            print(f"✅ SUCCESS: Title includes complete business context!")
            print(f"   Found parts: {found_parts}")
            return True
        else:
            print(f"❌ FAILED: Title missing business context")
            print(f"   Expected parts: {expected_parts}")
            print(f"   Found parts: {found_parts}")
            return False
            
    except Exception as e:
        print(f"❌ Error testing visualization: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = test_complete_business_title()
    if success:
        print("\n🎉 Test PASSED: Visualization agent now generates complete business context titles!")
    else:
        print("\n❌ Test FAILED: Visualization agent still not generating complete titles")
    
    sys.exit(0 if success else 1) 