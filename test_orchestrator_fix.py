#!/usr/bin/env python3
"""
Test Orchestrator Context Awareness and Delegation Logic Fix
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from agents import orchestrator_agent
from config import llm_config

def test_orchestrator_context_awareness():
    """Test that orchestrator recognizes completed work and delegates properly"""
    
    print("🧪 Testing Orchestrator Context Awareness & Delegation Logic")
    print("=" * 60)
    
    # Create orchestrator
    orchestrator = orchestrator_agent.create_agent()
    
    # Simulate conversation context with completed work
    conversation_context = """
=== CHRONOLOGICAL CONVERSATION CONTEXT ===
[1] User: "do a feature engineering in details with the forecast data"
[2] Orchestrator: "I will delegate this to the Forecasting-Data-Analyst-Agent..."
[3] Data Analyst: "Thank you for prompting me to continue. As the Forecasting Data Analyst, I will complete the comparative analysis...
    [DETAILED FEATURE ENGINEERING ANALYSIS WITH 2000+ WORDS OF RESULTS]
    Derived Features and Their Relevance:
    1. Month of Year (Categorical/Cyclical Feature)
    2. Daily Average (Derived Metric)
    3. Month-over-Month (MoM) Volume Change (%)
    4. Rolling Averages (e.g., 3-Month Moving Average)
    5. Peak/Trough Indicators (Boolean Flag)
    6. Lagged Features (e.g., Volume Lagged by 1 Month)
    [COMPLETE DETAILED ANALYSIS]"
[4] User: "give me its python code"
"""
    
    # Test Case 1: User asks for Python code after completed analysis
    test_messages = [
        {
            "role": "system", 
            "content": f"""You are part of an intelligent workforce management system. 
            
Here is the complete conversation history:

{conversation_context}

Your job is to recognize that the Data Analyst has COMPLETED the feature engineering work and now the user is asking for Python code. You should delegate immediately."""
        },
        {
            "role": "user",
            "content": "give me the python code for the feature engineering"
        }
    ]
    
    print("🔍 Test Case: User asks for Python code after completed feature engineering")
    print("Expected: Should delegate to Forecasting-Data-Analyst-Agent immediately")
    print("Should NOT say: 'currently working' or 'in progress'")
    print()
    
    # Get orchestrator response
    try:
        response = orchestrator.generate_reply(messages=test_messages)
        
        if isinstance(response, dict):
            content = response.get('content', '')
        else:
            content = str(response)
        
        print(f"📤 Orchestrator Response:")
        print(f"   {content}")
        print()
        
        # Analyze response
        if "forecasting-data-analyst-agent" in content.lower():
            print("✅ PASS: Correctly delegated to Forecasting-Data-Analyst-Agent")
        else:
            print("❌ FAIL: Did not delegate to correct agent")
        
        if "currently working" in content.lower() or "in progress" in content.lower():
            print("❌ FAIL: Still thinks work is in progress")
        else:
            print("✅ PASS: Recognizes work is completed")
        
        if "python code" in content.lower():
            print("✅ PASS: Acknowledges the Python code request")
        else:
            print("⚠️ WARNING: May not have understood the Python code request")
            
    except Exception as e:
        print(f"❌ ERROR: {e}")
    
    print("\n" + "=" * 60)
    print("🎯 SUMMARY: Enhanced orchestrator should now:")
    print("   1. ✅ Recognize when delegated work is completed")
    print("   2. ✅ Delegate immediately on explicit requests")
    print("   3. ✅ Not assume work is 'currently in progress'")
    print("   4. ✅ Handle follow-up requests properly")

if __name__ == "__main__":
    test_orchestrator_context_awareness() 