import os
import sys
import traceback

# Set environment variables
os.environ["GOOGLE_CLOUD_PROJECT"] = "gen-lang-client-0449161426"

def test_config():
    """Test if config loads without errors"""
    try:
        from config import llm_config
        print("✅ Config loaded successfully")
        return True
    except Exception as e:
        print(f"❌ Config failed: {e}")
        return False

def test_kpi_agent():
    """Test if KPI agent can be created"""
    try:
        from agents.kpi_agent import create_agent, fetch_kpi
        agent = create_agent()
        print("✅ KPI Agent created successfully")
        
        # Test KPI function
        result = fetch_kpi("home loan attrition rate last month")
        print(f"✅ KPI function works: Found {len(result) if isinstance(result, list) else 'unknown'} results")
        return True
    except Exception as e:
        print(f"❌ KPI Agent failed: {e}")
        return False

def test_data_analyst_agent():
    """Test if Data Analyst agent can be created"""
    try:
        from agents.forecasting_data_analyst_agent import create_agent
        agent = create_agent()
        print("✅ Data Analyst Agent created successfully")
        return True
    except Exception as e:
        print(f"❌ Data Analyst Agent failed: {e}")
        return False

def test_visualization_agent():
    """Test if Visualization agent can be created"""
    try:
        from agents.data_visualization_agent import create_agent, create_visualization
        agent = create_agent()
        print("✅ Visualization Agent created successfully")
        
        # Test visualization function
        test_data = '[{"date": "2025-01-01", "value": 9.92}]'
        result = create_visualization(test_data)
        print(f"✅ Visualization function works: {type(result)}")
        return True
    except Exception as e:
        print(f"❌ Visualization Agent failed: {e}")
        return False

if __name__ == "__main__":
    print("🧪 Testing Basic Functionality (Fixed)\n")
    
    tests = [
        ("Config", test_config),
        ("KPI Agent", test_kpi_agent), 
        ("Data Analyst Agent", test_data_analyst_agent),
        ("Visualization Agent", test_visualization_agent)
    ]
    
    results = []
    for name, test_func in tests:
        print(f"\n📋 Testing {name}...")
        try:
            success = test_func()
            results.append((name, success))
        except Exception as e:
            print(f"❌ {name} failed with exception: {e}")
            results.append((name, False))
    
    print("\n" + "="*50)
    print("📊 Test Results:")
    for name, success in results:
        status = "✅ PASS" if success else "❌ FAIL"
        print(f"   {name}: {status}")
    
    total_passed = sum(1 for _, success in results if success)
    print(f"\n🎯 Overall: {total_passed}/{len(results)} tests passed")
    
    if total_passed == len(results):
        print("✅ All tests passed! Ready to run the app.")
        print("\n🚀 To run the app:")
        print("export GOOGLE_CLOUD_PROJECT=\"gen-lang-client-0449161426\" && chainlit run app.py --port 8080")
    else:
        print("❌ Some tests failed. Fix needed before running app.") 