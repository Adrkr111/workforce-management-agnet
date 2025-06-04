from autogen import ConversableAgent
from config import llm_config
from .promp_engineering.visualization_agent_prompt import visualization_agent_system_message
import json
import re
from typing import Dict, List, Union
from datetime import datetime
import pandas as pd

def infer_data_structure(data_str: str) -> Dict:
    """
    Intelligently infer the data structure and type from the input
    """
    try:
        # Check if it's forecast data (look for common patterns)
        if any(pattern in data_str.lower() for pattern in ["forecast", "volume", "team", "business", "substream"]):
            # Extract forecast-specific patterns
            volumes = re.findall(r'volume[s]?\s*:\s*(\d+)', data_str.lower())
            dates = re.findall(r'\d{4}-\d{2}-\d{2}|\d{2}/\d{2}/\d{4}', data_str)
            
            if dates and volumes:
                return {
                    "type": "forecast_timeseries",
                    "x": dates,
                    "y": [float(v) for v in volumes],
                    "title": "Forecast Volume Over Time"
                }
        
        # Check if it's a comparison (multiple teams/categories)
        if "compare" in data_str.lower() or len(re.findall(r'team[-:]', data_str.lower())) > 1:
            teams = re.findall(r'team[-:]\s*(\w+)', data_str.lower())
            values = re.findall(r'volume[s]?\s*:\s*(\d+)', data_str.lower())
            
            if teams and values:
                return {
                    "type": "comparison",
                    "x": teams,
                    "y": [float(v) for v in values],
                    "title": "Team Comparison"
                }
        
        # Default to simple data extraction
        numbers = re.findall(r'-?\d*\.?\d+', data_str)
        if numbers:
            return {
                "type": "trend",
                "x": list(range(len(numbers))),
                "y": [float(n) for n in numbers],
                "title": "Data Trend"
            }
        
        return {"error": "Could not infer data structure"}
            
    except Exception as e:
        return {"error": f"Error inferring data structure: {str(e)}"}

def create_visualization(data_str: str) -> Dict:
    """
    Creates visualizations using Plotly specifications
    """
    try:
        print("\nDebug - Visualization Agent - Starting visualization creation")
        print(f"Debug - Input data: {data_str[:200]}...")  # Print first 200 chars
        
        # Try to parse as JSON first
        try:
            data = json.loads(data_str)
            print("Debug - Successfully parsed input as JSON")
            
            # Handle simple list format: [{"date": "2025-02-01", "value": 6.81}, ...]
            if isinstance(data, list) and len(data) > 0 and all(isinstance(item, dict) for item in data):
                print("Debug - Found simple list format")
                
                # Check if all items have date and value keys
                if all("date" in item and "value" in item for item in data):
                    print("Debug - Converting simple list to Plotly format")
                    spec_data = {
                        "data": [{
                            "x": [item["date"] for item in data],
                            "y": [float(item["value"]) for item in data],
                            "type": "scatter",
                            "mode": "lines+markers",
                            "name": "KPI Trend",
                            "line": {"color": "#2E86C1"},
                            "marker": {"size": 8}
                        }],
                        "layout": {
                            "title": "KPI Trend Over Time",
                            "xaxis": {
                                "title": "Date",
                                "showgrid": True,
                                "gridcolor": "#E1E5EA"
                            },
                            "yaxis": {
                                "title": "Value (%)",
                                "showgrid": True,
                                "gridcolor": "#E1E5EA"
                            },
                            "plot_bgcolor": "white",
                            "paper_bgcolor": "white",
                            "margin": {"t": 60, "b": 60, "l": 60, "r": 40}
                        }
                    }
                    print("Debug - Created Plotly spec from simple list")
                    
                    # Check if we're in a Chainlit context before sending message
                    return {"spec": spec_data}
            
            # If it's already a Plotly spec, return it directly
            if isinstance(data, dict):
                if "data" in data and "values" in data["data"]:
                    print("Debug - Found existing Plotly spec")
                    return {"spec": data}
                
                # Convert data to Plotly format
                if "data" in data:
                    print("Debug - Converting data to Plotly format")
                    spec_data = {
                        "data": [{
                            "x": [point["date"] for point in data["data"]["values"]],
                            "y": [point["volume"] for point in data["data"]["values"]],
                            "type": "scatter",
                            "mode": "lines+markers",
                            "name": data.get("title", "Volume Forecast"),
                            "line": {"color": "#2E86C1"},
                            "marker": {"size": 8}
                        }],
                        "layout": {
                            "title": data.get("title", "Volume Forecast Over Time"),
                            "xaxis": {
                                "title": "Date",
                                "showgrid": True,
                                "gridcolor": "#E1E5EA"
                            },
                            "yaxis": {
                                "title": "Volume",
                                "showgrid": True,
                                "gridcolor": "#E1E5EA"
                            },
                            "plot_bgcolor": "white",
                            "paper_bgcolor": "white",
                            "margin": {"t": 60, "b": 60, "l": 60, "r": 40}
                        }
                    }
                    return {"spec": spec_data}
                    
        except json.JSONDecodeError as e:
            print(f"Debug - JSON parsing failed: {e}")
            pass
        
        print("Debug - Attempting to parse from text format")
        # Parse text format data
        dates = re.findall(r'date:\s*(\d{4}-\d{2}-\d{2})', data_str)
        volumes = re.findall(r'volume:\s*(\d+)', data_str)
        
        if dates and volumes:
            print("Debug - Found dates and volumes in text format")
            # Create Plotly spec
            spec_data = {
                "data": [{
                    "x": dates,
                    "y": [int(v) for v in volumes],
                    "type": "scatter",
                    "mode": "lines+markers",
                    "name": "Volume Forecast",
                    "line": {"color": "#2E86C1"},
                    "marker": {"size": 8}
                }],
                "layout": {
                    "title": "Volume Forecast Over Time",
                    "xaxis": {
                        "title": "Date",
                        "showgrid": True,
                        "gridcolor": "#E1E5EA"
                    },
                    "yaxis": {
                        "title": "Volume",
                        "showgrid": True,
                        "gridcolor": "#E1E5EA"
                    },
                    "plot_bgcolor": "white",
                    "paper_bgcolor": "white",
                    "margin": {"t": 60, "b": 60, "l": 60, "r": 40}
                }
            }
            
            return {"spec": spec_data}
            
        print("Debug - Could not parse input data in any format")
        return {"error": "Could not parse input data"}
            
    except Exception as e:
        print(f"Debug - Error in create_visualization: {str(e)}")
        import traceback
        print(f"Debug - Traceback: {traceback.format_exc()}")
        return {"error": f"Error creating visualization: {str(e)}"}

def create_agent():
    data_visualization_agent = ConversableAgent(
        name="Data-Visualization-Agent",
        llm_config=llm_config,
        system_message=visualization_agent_system_message,
        is_termination_msg=lambda x: "TERMINATE" in x.get("content", ""),
        human_input_mode="NEVER",
        function_map={
            "create_visualization": create_visualization
        }
    )
    return data_visualization_agent 