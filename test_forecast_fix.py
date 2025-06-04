#!/usr/bin/env python3

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from agents.fetch_forecasting_agent import create_agent

def test_forecast_agent_function_call():
    """Test that forecast agent calls its function instead of returning dummy data"""
    
    print("=== Testing Forecast Agent Function Call ===")
    
    # Create forecast agent
    forecast_agent = create_agent()
    print(f"✅ Created agent: {forecast_agent.name}")
    
    # Test message that should trigger function call
    test_message = "Get forecast for business-logistics substream-dlt team-support"
    
    print(f"\n🧪 Testing with message: '{test_message}'")
    print("Expected: Agent should call fetch_forecast function")
    print("NOT Expected: Agent should NOT return dummy data like 'Day 1: 150 units'")
    
    try:
        # Generate response
        response = forecast_agent.generate_reply(
            messages=[{"role": "user", "content": test_message}],
            sender=None
        )
        
        print(f"\n📋 Agent Response:")
        print(f"Type: {type(response)}")
        print(f"Content: {response}")
        
        # Check if it's calling function vs returning dummy data
        response_str = str(response).lower()
        
        if "function_call" in response_str and "fetch_forecast" in response_str:
            print("\n✅ SUCCESS: Agent is calling fetch_forecast function!")
            return True
        elif "day 1" in response_str or "150 units" in response_str or "tomorrow" in response_str:
            print("\n❌ FAILURE: Agent is still returning dummy data!")
            print("The agent should call the function, not generate fake forecasts")
            return False
        else:
            print(f"\n⚠️  UNCLEAR: Response doesn't clearly show function call or dummy data")
            print("Response:", response)
            return False
            
    except Exception as e:
        print(f"\n❌ ERROR: {str(e)}")
        return False

if __name__ == "__main__":
    success = test_forecast_agent_function_call()
    
    if success:
        print("\n🎉 Forecast agent fix appears to be working!")
        print("The agent should now call real vector database functions.")
    else:
        print("\n🔧 Forecast agent still needs fixing.")
        print("Check the agent prompt and function configuration.")
    
    sys.exit(0 if success else 1) 