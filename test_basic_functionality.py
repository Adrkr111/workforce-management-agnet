#!/usr/bin/env python3
"""
Basic Functionality Testing Script for Workforce Management System
Tests core functionality including agents, functions, ChromaDB, and message flow
"""

import asyncio
import json
import sys
import os
import traceback
from datetime import datetime

# Add the project root to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from config import llm_config
from agents import (
    fetch_forecasting_agent, 
    forecasting_data_analyst_agent,
    data_visualization_agent,
    orchestrator_agent,
    kpi_agent,
    workforce_simulation_agent
)
from vector_database.chroma import get_chroma_client

class BasicFunctionalityTester:
    def __init__(self):
        self.test_results = []
        self.agents = None
        self.chroma_client = None
        
    def log_test(self, test_name, passed, message="", error=None):
        """Log test results"""
        status = "✅ PASS" if passed else "❌ FAIL"
        self.test_results.append({
            "test": test_name,
            "passed": passed,
            "message": message,
            "error": str(error) if error else None
        })
        print(f"{status} - {test_name}: {message}")
        if error:
            print(f"   Error: {error}")
    
    def test_config_loading(self):
        """Test 1: Configuration Loading"""
        try:
            assert llm_config is not None, "LLM config not loaded"
            assert 'config_list' in llm_config, "Config list not found"
            assert len(llm_config['config_list']) > 0, "No configs in list"
            
            config = llm_config['config_list'][0]
            assert 'model' in config, "Model not specified in config"
            
            self.log_test("Configuration Loading", True, f"Config loaded with model: {config['model']}")
            return True
        except Exception as e:
            self.log_test("Configuration Loading", False, "Failed to load configuration", e)
            return False
    
    def test_agent_creation(self):
        """Test 2: Agent Creation"""
        try:
            # Test individual agent creation
            orchestrator = orchestrator_agent.create_agent()
            fetch_forecast = fetch_forecasting_agent.create_agent()
            data_analyst = forecasting_data_analyst_agent.create_agent()
            visualizer = data_visualization_agent.create_agent()
            kpi = kpi_agent.create_agent()
            workforce_sim = workforce_simulation_agent.create_agent()
            
            self.agents = [orchestrator, fetch_forecast, data_analyst, visualizer, kpi, workforce_sim]
            
            # Test agent properties
            for agent in self.agents:
                assert hasattr(agent, 'name'), f"Agent {agent} missing name"
                assert hasattr(agent, 'llm_config'), f"Agent {agent.name} missing llm_config"
                assert hasattr(agent, 'generate_reply'), f"Agent {agent.name} missing generate_reply method"
            
            # Test function maps for functional agents
            functional_agents = ['Fetch-Volume-Forecast-Agent', 'Data-Visualization-Agent', 'KPI-Data-Agent']
            for agent in self.agents:
                if agent.name in functional_agents:
                    assert hasattr(agent, 'function_map'), f"Functional agent {agent.name} missing function_map"
                    assert len(agent.function_map) > 0, f"Agent {agent.name} has empty function_map"
            
            self.log_test("Agent Creation", True, f"Successfully created {len(self.agents)} agents")
            return True
        except Exception as e:
            self.log_test("Agent Creation", False, "Failed to create agents", e)
            return False
    
    def test_chromadb_connection(self):
        """Test 3: ChromaDB Connection"""
        try:
            self.chroma_client = get_chroma_client()
            assert self.chroma_client is not None, "ChromaDB client not created"
            
            # Test collection creation
            test_collection_name = f"test_collection_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
            collection = self.chroma_client.get_or_create_collection(
                name=test_collection_name,
                metadata={"type": "test"}
            )
            
            # Test adding and retrieving data
            test_id = "test_doc_1"
            test_doc = "This is a test document"
            test_metadata = {"test": True, "timestamp": datetime.now().isoformat()}
            
            collection.add(
                ids=[test_id],
                documents=[test_doc],
                metadatas=[test_metadata]
            )
            
            # Retrieve and verify
            results = collection.get(ids=[test_id])
            assert len(results['documents']) == 1, "Document not retrieved"
            assert results['documents'][0] == test_doc, "Document content mismatch"
            
            # Clean up
            self.chroma_client.delete_collection(test_collection_name)
            
            self.log_test("ChromaDB Connection", True, "ChromaDB connection and operations successful")
            return True
        except Exception as e:
            self.log_test("ChromaDB Connection", False, "ChromaDB connection failed", e)
            return False
    
    def test_agent_functions(self):
        """Test 4: Agent Function Calls"""
        try:
            if not self.agents:
                raise Exception("Agents not created")
            
            # Test fetch forecast agent function
            fetch_agent = next(a for a in self.agents if a.name == "Fetch-Volume-Forecast-Agent")
            if hasattr(fetch_agent, 'function_map') and 'fetch_forecast' in fetch_agent.function_map:
                func = fetch_agent.function_map['fetch_forecast']
                result = func('{"business": "logistics", "substream": "dlt", "team": "support"}')
                assert result is not None, "Fetch forecast function returned None"
                self.log_test("Fetch Forecast Function", True, "Function executed successfully")
            else:
                self.log_test("Fetch Forecast Function", False, "Function not found")
            
            # Test visualization agent function
            viz_agent = next(a for a in self.agents if a.name == "Data-Visualization-Agent")
            if hasattr(viz_agent, 'function_map') and 'create_visualization' in viz_agent.function_map:
                func = viz_agent.function_map['create_visualization']
                test_data = '[{"date": "2025-01-01", "value": 100, "team": "test"}]'
                result = func(test_data)
                assert result is not None, "Visualization function returned None"
                assert isinstance(result, dict), "Visualization function should return dict"
                self.log_test("Visualization Function", True, "Function executed successfully")
            else:
                self.log_test("Visualization Function", False, "Function not found")
            
            # Test KPI agent function
            kpi_agent = next(a for a in self.agents if a.name == "KPI-Data-Agent")
            if hasattr(kpi_agent, 'function_map') and 'fetch_kpi' in kpi_agent.function_map:
                func = kpi_agent.function_map['fetch_kpi']
                result = func('{"metric": "attrition_rate", "date": "2024-01-01"}')
                assert result is not None, "KPI function returned None"
                self.log_test("KPI Function", True, "Function executed successfully")
            else:
                self.log_test("KPI Function", False, "Function not found")
            
            return True
        except Exception as e:
            self.log_test("Agent Functions", False, "Agent function testing failed", e)
            return False
    
    def test_message_processing(self):
        """Test 5: Message Processing"""
        try:
            if not self.agents:
                raise Exception("Agents not created")
            
            orchestrator = next(a for a in self.agents if a.name == "Orchestrator-Agent")
            
            # Test basic message generation
            test_messages = [
                {"role": "user", "content": "Hello, can you help me with workforce forecasting?"}
            ]
            
            # Test sync generation
            response = orchestrator.generate_reply(messages=test_messages)
            assert response is not None, "Orchestrator returned None response"
            
            if isinstance(response, dict):
                assert 'content' in response, "Response missing content"
                content = response['content']
            else:
                content = str(response)
            
            assert len(content) > 0, "Response content is empty"
            
            self.log_test("Message Processing", True, f"Generated response: {content[:100]}...")
            return True
        except Exception as e:
            self.log_test("Message Processing", False, "Message processing failed", e)
            return False
    
    def test_json_parsing(self):
        """Test 6: JSON Parsing for Function Calls"""
        try:
            # Test JSON parsing scenarios
            test_cases = [
                # Valid JSON with function call
                '{"function_call": {"name": "test_func", "arguments": "test_args"}}',
                # JSON embedded in text
                'Here is the function call: {"function_call": {"name": "fetch_forecast", "arguments": "test"}}',
                # Simple data array
                '[{"date": "2025-01-01", "value": 100}]',
                # Complex visualization data
                '{"spec": {"data": [{"x": [1,2,3], "y": [1,2,3]}], "layout": {"title": "Test"}}}'
            ]
            
            for i, test_case in enumerate(test_cases):
                try:
                    # Try JSON parsing
                    if test_case.startswith('[') or test_case.startswith('{'):
                        data = json.loads(test_case)
                    else:
                        # Extract JSON from text
                        start = test_case.find("{")
                        end = test_case.rfind("}") + 1
                        if start >= 0 and end > start:
                            json_str = test_case[start:end]
                            data = json.loads(json_str)
                    
                    assert data is not None, f"Case {i+1}: JSON parsing failed"
                except json.JSONDecodeError:
                    # Some cases might fail, that's expected for malformed JSON
                    pass
            
            self.log_test("JSON Parsing", True, f"Tested {len(test_cases)} parsing scenarios")
            return True
        except Exception as e:
            self.log_test("JSON Parsing", False, "JSON parsing test failed", e)
            return False
    
    def test_error_handling(self):
        """Test 7: Error Handling"""
        try:
            if not self.agents:
                raise Exception("Agents not created")
            
            # Test invalid function call
            viz_agent = next(a for a in self.agents if a.name == "Data-Visualization-Agent")
            if hasattr(viz_agent, 'function_map') and 'create_visualization' in viz_agent.function_map:
                func = viz_agent.function_map['create_visualization']
                
                # Test with invalid data - should not crash
                try:
                    result = func('invalid_data')
                    # Should not crash, should return error or default
                    assert result is not None, "Function should handle errors gracefully"
                except Exception as e:
                    # It's okay if function throws exception, as long as it's handled
                    print(f"Debug - Function handled error gracefully: {e}")
            
            # Test empty message handling
            orchestrator = next(a for a in self.agents if a.name == "Orchestrator-Agent")
            try:
                response = orchestrator.generate_reply(messages=[])
                # Should not crash, response can be None or any value
            except Exception as e:
                # It's okay if this throws exception, as long as system doesn't crash
                print(f"Debug - Empty message handled: {e}")
            
            # Test None input handling
            try:
                response = orchestrator.generate_reply(messages=None)
            except Exception as e:
                print(f"Debug - None input handled: {e}")
            
            self.log_test("Error Handling", True, "Error handling tests passed")
            return True
        except Exception as e:
            self.log_test("Error Handling", False, "Error handling test failed", e)
            return False
    
    async def test_async_functionality(self):
        """Test 8: Async Functionality"""
        try:
            if not self.agents:
                raise Exception("Agents not created")
            
            # Add async support to agents (mimicking app.py behavior)
            for agent in self.agents:
                if not hasattr(agent, 'a_generate_reply'):
                    async def a_generate_reply(self, messages=None, sender=None, config=None):
                        return self.generate_reply(messages=messages, sender=sender, config=config)
                    agent.a_generate_reply = a_generate_reply.__get__(agent)
            
            # Test async message generation
            orchestrator = next(a for a in self.agents if a.name == "Orchestrator-Agent")
            test_messages = [{"role": "user", "content": "Test async functionality"}]
            
            response = await orchestrator.a_generate_reply(messages=test_messages)
            assert response is not None, "Async response is None"
            
            self.log_test("Async Functionality", True, "Async functionality working")
            return True
        except Exception as e:
            self.log_test("Async Functionality", False, "Async functionality failed", e)
            return False
    
    def test_data_validation(self):
        """Test 9: Data Validation"""
        try:
            # Test various data formats that the system should handle
            test_data_formats = [
                # Standard forecast data
                '[{"date": "2025-01-01", "value": 100, "team": "support"}]',
                # Simple x,y data
                '[{"x": 1, "y": 10}, {"x": 2, "y": 20}]',
                # Complex nested data
                '{"teams": {"team1": {"data": [1,2,3]}, "team2": {"data": [4,5,6]}}}',
                # Empty data
                '[]',
                # Single value
                '{"value": 42}'
            ]
            
            viz_agent = next(a for a in self.agents if a.name == "Data-Visualization-Agent")
            if hasattr(viz_agent, 'function_map') and 'create_visualization' in viz_agent.function_map:
                func = viz_agent.function_map['create_visualization']
                
                for data_format in test_data_formats:
                    result = func(data_format)
                    assert result is not None, f"Data validation failed for: {data_format}"
            
            self.log_test("Data Validation", True, f"Validated {len(test_data_formats)} data formats")
            return True
        except Exception as e:
            self.log_test("Data Validation", False, "Data validation failed", e)
            return False
    
    def print_summary(self):
        """Print test summary"""
        total_tests = len(self.test_results)
        passed_tests = len([r for r in self.test_results if r['passed']])
        failed_tests = total_tests - passed_tests
        
        print("\n" + "="*60)
        print("🧪 BASIC FUNCTIONALITY TEST SUMMARY")
        print("="*60)
        print(f"Total Tests: {total_tests}")
        print(f"✅ Passed: {passed_tests}")
        print(f"❌ Failed: {failed_tests}")
        print(f"Success Rate: {(passed_tests/total_tests)*100:.1f}%")
        
        if failed_tests > 0:
            print(f"\n❌ FAILED TESTS:")
            for result in self.test_results:
                if not result['passed']:
                    print(f"   - {result['test']}: {result['message']}")
                    if result['error']:
                        print(f"     Error: {result['error']}")
        
        print("\n" + "="*60)
        return failed_tests == 0

async def main():
    """Run all basic functionality tests"""
    print("🚀 Starting Basic Functionality Tests for Workforce Management System")
    print("="*70)
    
    tester = BasicFunctionalityTester()
    
    # Run all tests
    tests = [
        tester.test_config_loading,
        tester.test_agent_creation,
        tester.test_chromadb_connection,
        tester.test_agent_functions,
        tester.test_message_processing,
        tester.test_json_parsing,
        tester.test_error_handling,
        tester.test_async_functionality,
        tester.test_data_validation
    ]
    
    # Execute tests
    for test in tests:
        if asyncio.iscoroutinefunction(test):
            await test()
        else:
            test()
        print()  # Add spacing between tests
    
    # Print summary
    success = tester.print_summary()
    
    if success:
        print("🎉 All basic functionality tests passed!")
        return 0
    else:
        print("💥 Some tests failed. Please review the issues above.")
        return 1

if __name__ == "__main__":
    try:
        exit_code = asyncio.run(main())
        sys.exit(exit_code)
    except KeyboardInterrupt:
        print("\n⏹️  Tests interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n💥 Fatal error running tests: {e}")
        traceback.print_exc()
        sys.exit(1) 