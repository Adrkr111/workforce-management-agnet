#!/usr/bin/env python3

import sys
import os

# Add path for imports
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Test only the prompt - no database required
from agents.promp_engineering.fetch_forecasting_agent_prompt import fetch_forecasting_agent_system_message

def test_forecast_prompt_fix():
    """Test that the forecast agent prompt has been updated properly"""
    
    print("=== Testing Forecast Agent Prompt Fix ===")
    
    # Check that the prompt contains the critical instructions
    prompt = fetch_forecasting_agent_system_message
    
    print(f"📋 Checking prompt content...")
    
    # Critical checks
    checks = [
        ("CRITICAL instruction", "CRITICAL:" in prompt),
        ("MANDATORY function usage", "MANDATORY:" in prompt),
        ("NEVER provide dummy data", "NEVER provide dummy data" in prompt),
        ("Function call example", "function_call" in prompt),
        ("fetch_forecast function", "fetch_forecast" in prompt),
        ("business-logistics example", "business-logistics" in prompt),
    ]
    
    all_passed = True
    
    for check_name, passed in checks:
        if passed:
            print(f"✅ {check_name}: FOUND")
        else:
            print(f"❌ {check_name}: MISSING")
            all_passed = False
    
    # Check for old problematic content
    bad_content_checks = [
        ("Dummy 'Day 1' references", "Day 1" not in prompt),
        ("Dummy unit numbers", "150 units" not in prompt),
        ("Generic forecasts", "Weekly Total" not in prompt),
    ]
    
    for check_name, passed in bad_content_checks:
        if passed:
            print(f"✅ {check_name}: CLEAN")
        else:
            print(f"❌ {check_name}: STILL PRESENT")
            all_passed = False
    
    if all_passed:
        print("\n🎉 SUCCESS: Forecast agent prompt has been properly updated!")
        print("The agent should now:")
        print("- Call fetch_forecast function when given parameters")
        print("- Never return dummy/fake data")
        print("- Use real vector database results")
        return True
    else:
        print("\n❌ FAILURE: Forecast agent prompt still needs updates")
        return False

def show_relevant_prompt_section():
    """Show the critical section of the prompt"""
    prompt = fetch_forecasting_agent_system_message
    
    print("\n📄 Key sections of the updated prompt:")
    print("=" * 50)
    
    lines = prompt.split('\n')
    for i, line in enumerate(lines):
        if 'CRITICAL:' in line or 'MANDATORY:' in line or 'NEVER provide dummy' in line:
            # Show this line and a few around it
            start = max(0, i-1)
            end = min(len(lines), i+3)
            for j in range(start, end):
                prefix = ">>> " if j == i else "    "
                print(f"{prefix}{lines[j]}")
            print()

if __name__ == "__main__":
    success = test_forecast_prompt_fix()
    
    if success:
        show_relevant_prompt_section()
        print("\n✅ Ready to test with full app!")
    else:
        print("\n🔧 Prompt needs more work before testing app.")
    
    sys.exit(0 if success else 1) 