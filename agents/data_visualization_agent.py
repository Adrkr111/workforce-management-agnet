from autogen import ConversableAgent
from config import llm_config
from .promp_engineering.visualization_agent_prompt import visualization_agent_system_message
import json
import re
from typing import Dict, List, Union, Any
from datetime import datetime
import pandas as pd

def create_visualization(data_str: str) -> Dict:
    """
    Ultra-robust visualization function that ALWAYS works and returns cl.Plotly compatible format
    """
    try:
        print(f"\n🎨 ROBUST VIZ - Processing: {data_str[:200]}...")
        
        # Step 1: Always try to extract SOMETHING meaningful
        parsed_data = smart_parse_any_format(data_str)
        
        # Step 2: Create Plotly specification no matter what
        plotly_spec = create_bulletproof_plotly_spec(parsed_data)
        
        # Step 3: Always return proper format for cl.Plotly
        result = {
            'spec': plotly_spec
        }
        
        print(f"✅ VIZ SUCCESS - Created chart with {len(plotly_spec.get('data', []))} traces")
        return result
        
    except Exception as e:
        print(f"⚠️ VIZ FALLBACK - Error: {e}")
        # NEVER fail - always return a valid chart
        return create_emergency_chart(data_str, str(e))

def smart_parse_any_format(data_str: str) -> Dict:
    """
    Parse ANY data format and extract meaningful information
    """
    print("🔍 Smart parsing starting...")
    
    # Try JSON first
    try:
        data = json.loads(data_str)
        print("✅ JSON parsed successfully")
        return extract_from_json(data)
    except:
        print("📝 JSON failed, trying text extraction")
        return extract_from_text(data_str)

def extract_from_json(data: Any) -> Dict:
    """
    Extract visualization data from JSON structure
    """
    if isinstance(data, list):
        return extract_from_list(data)
    elif isinstance(data, dict):
        return extract_from_dict(data)
    else:
        return {"type": "simple", "values": [data] if data is not None else [0]}

def extract_from_list(data: List) -> Dict:
    """
    Extract from list data - handles ALL possible list formats
    """
    if not data:
        return {"type": "empty", "x": ["No Data"], "y": [0]}
    
    # Check if list contains dictionaries
    if isinstance(data[0], dict):
        return extract_from_dict_list(data)
    else:
        # Simple list of numbers or strings
        return {
            "type": "simple_list",
            "x": [f"Item {i+1}" for i in range(len(data))],
            "y": [float(x) if isinstance(x, (int, float)) else 1 for x in data],
            "labels": [str(x) for x in data]
        }

def extract_from_dict_list(data: List[Dict]) -> Dict:
    """
    Extract from list of dictionaries - the most common format
    """
    # Get all possible field names
    all_fields = set()
    for item in data:
        all_fields.update(item.keys())
    
    print(f"🔑 Fields found: {all_fields}")
    
    # Smart field detection with multiple fallbacks
    x_field = detect_x_field(all_fields)
    y_field = detect_y_field(all_fields)
    team_field = detect_team_field(all_fields)
    
    print(f"📊 Using x={x_field}, y={y_field}, team={team_field}")
    
    # Extract data with fallbacks
    if team_field and len(set(str(item.get(team_field, '')) for item in data)) > 1:
        # Multi-series data (with teams/categories)
        return extract_multi_series(data, x_field, y_field, team_field)
    else:
        # Single series data
        return extract_single_series(data, x_field, y_field)

def detect_x_field(fields: set) -> str:
    """
    Detect X-axis field with multiple fallbacks
    """
    # Priority order for X-axis detection
    x_patterns = [
        ['date', 'time'],  # Time fields first
        ['month', 'year', 'period'],  # Time periods
        ['x', 'index', 'step'],  # Explicit x fields
        ['name', 'category', 'label']  # Category fields
    ]
    
    for pattern_group in x_patterns:
        for pattern in pattern_group:
            matches = [f for f in fields if pattern in f.lower()]
            if matches:
                return matches[0]
    
    # Absolute fallback - use first field
    return list(fields)[0] if fields else 'index'

def detect_y_field(fields: set) -> str:
    """
    Detect Y-axis field with multiple fallbacks
    """
    # Priority order for Y-axis detection
    y_patterns = [
        ['value', 'volume', 'amount', 'count'],  # Value fields
        ['total', 'sum', 'avg', 'average'],  # Aggregation fields
        ['ftes', 'required', 'needed', 'additional'],  # Workforce fields
        ['cost', 'price', 'rate', 'percentage'],  # Financial fields
        ['y', 'val', 'number', 'num']  # Explicit y fields
    ]
    
    for pattern_group in y_patterns:
        for pattern in pattern_group:
            matches = [f for f in fields if pattern in f.lower()]
            if matches:
                return matches[0]
    
    # Look for any numeric-looking field
    for field in fields:
        if any(num_word in field.lower() for num_word in ['_ftes', '_count', '_total', '_val']):
            return field
    
    # Absolute fallback - use second field or first field
    field_list = list(fields)
    return field_list[1] if len(field_list) > 1 else field_list[0] if field_list else 'value'

def detect_team_field(fields: set) -> str:
    """
    Detect team/category field for color coding
    """
    team_patterns = ['team', 'group', 'category', 'type', 'name', 'business', 'department', 'unit']
    
    for pattern in team_patterns:
        matches = [f for f in fields if pattern in f.lower()]
        if matches:
            return matches[0]
    
    return None

def extract_single_series(data: List[Dict], x_field: str, y_field: str) -> Dict:
    """
    Extract single series data
    """
    x_values = []
    y_values = []
    
    for item in data:
        x_val = item.get(x_field, '')
        y_val = item.get(y_field, 0)
        
        # Convert values safely
        x_values.append(str(x_val))
        y_values.append(safe_float(y_val))
    
    return {
        "type": "single_series",
        "x": x_values,
        "y": y_values,
        "title": f"{y_field.title()} over {x_field.title()}"
    }

def extract_multi_series(data: List[Dict], x_field: str, y_field: str, team_field: str) -> Dict:
    """
    Extract multi-series data with color coding
    """
    # Group by team
    teams = {}
    for item in data:
        team = str(item.get(team_field, 'Unknown')).title()
        if team not in teams:
            teams[team] = {"x": [], "y": []}
        
        x_val = item.get(x_field, '')
        y_val = item.get(y_field, 0)
        
        teams[team]["x"].append(str(x_val))
        teams[team]["y"].append(safe_float(y_val))
    
    return {
        "type": "multi_series",
        "teams": teams,
        "title": f"{y_field.title()} by {team_field.title()} over {x_field.title()}"
    }

def extract_from_dict(data: Dict) -> Dict:
    """
    Extract from dictionary data
    """
    # Check if it's already processed data with teams
    if "teams" in data:
        return data
    
    # Check if it's a nested structure
    if "data" in data and isinstance(data["data"], list):
        return extract_from_list(data["data"])
    
    # Simple key-value pairs
    if all(isinstance(v, (int, float, str)) for v in data.values()):
        return {
            "type": "dict_simple",
            "x": list(data.keys()),
            "y": [safe_float(v) for v in data.values()],
            "title": "Data Overview"
        }
    
    # Complex dictionary - extract what we can
    numeric_fields = {k: v for k, v in data.items() if isinstance(v, (int, float))}
    if numeric_fields:
        return {
            "type": "dict_numeric",
            "x": list(numeric_fields.keys()),
            "y": list(numeric_fields.values()),
            "title": "Numeric Data"
        }
    
    # Fallback
    return {"type": "dict_fallback", "x": ["Data"], "y": [1], "title": "Data Present"}

def extract_from_text(data_str: str) -> Dict:
    """
    Extract data from plain text using regex
    """
    print("🔍 Extracting from text...")
    
    # Extract numbers
    numbers = re.findall(r'-?\d*\.?\d+', data_str)
    if numbers:
        y_values = [float(n) for n in numbers[:20]]  # Limit to 20 points
        x_values = [f"Point {i+1}" for i in range(len(y_values))]
        
        return {
            "type": "text_numbers",
            "x": x_values,
            "y": y_values,
            "title": "Extracted Data"
        }
    
    # Extract words as categories
    words = re.findall(r'\b[A-Za-z]+\b', data_str)
    if words:
        word_counts = {}
        for word in words[:10]:  # Top 10 words
            word_counts[word] = word_counts.get(word, 0) + 1
        
        return {
            "type": "text_words",
            "x": list(word_counts.keys()),
            "y": list(word_counts.values()),
            "title": "Word Frequency"
        }
    
    # Ultimate fallback
    return {"type": "text_fallback", "x": ["Text"], "y": [1], "title": "Text Data"}

def safe_float(value: Any) -> float:
    """
    Safely convert any value to float
    """
    try:
        if isinstance(value, (int, float)):
            return float(value)
        elif isinstance(value, str):
            # Remove common non-numeric characters
            cleaned = re.sub(r'[^\d.-]', '', value)
            return float(cleaned) if cleaned else 0.0
        else:
            return 0.0
    except:
        return 0.0

def create_bulletproof_plotly_spec(parsed_data: Dict) -> Dict:
    """
    Create Plotly spec that ALWAYS works
    """
    data_type = parsed_data.get("type", "simple")
    
    # Color palette for multi-series
    colors = [
        '#2E86C1', '#E74C3C', '#28B463', '#F39C12', 
        '#8E44AD', '#17A2B8', '#FD7E14', '#20C997'
    ]
    
    if data_type == "multi_series" and "teams" in parsed_data:
        # Multi-series chart with color coding
        traces = []
        teams = parsed_data["teams"]
        
        for i, (team_name, team_data) in enumerate(teams.items()):
            color = colors[i % len(colors)]
            traces.append({
                'x': team_data["x"],
                'y': team_data["y"],
                'type': 'scatter',
                'mode': 'lines+markers',
                'name': f"{team_name} Team",
                'line': {'color': color, 'width': 3},
                'marker': {'size': 8, 'color': color}
            })
        
        layout = {
            'title': {
                'text': parsed_data.get("title", "Multi-Team Analysis"),
                'x': 0.5,
                'font': {'size': 18, 'family': 'Arial, sans-serif'}
            },
            'xaxis': {
                'title': 'Date',
                'showgrid': True,
                'gridcolor': '#E1E5EA',
                'tickfont': {'size': 12}
            },
            'yaxis': {
                'title': 'Volume',
                'showgrid': True,
                'gridcolor': '#E1E5EA',
                'tickfont': {'size': 12}
            },
            'legend': {
                'x': 1.02,
                'y': 1,
                'bgcolor': 'rgba(255,255,255,0.8)',
                'bordercolor': '#E1E5EA',
                'borderwidth': 1
            },
            'plot_bgcolor': 'white',
            'paper_bgcolor': 'white',
            'margin': {'t': 60, 'b': 60, 'l': 60, 'r': 120}
        }
        
    else:
        # Single series chart
        x_values = parsed_data.get("x", ["Data"])
        y_values = parsed_data.get("y", [1])
        
        traces = [{
            'x': x_values,
            'y': y_values,
            'type': 'scatter',
            'mode': 'lines+markers',
            'name': 'Data Trend',
            'line': {'color': colors[0], 'width': 3},
            'marker': {'size': 8, 'color': colors[0]}
        }]
        
        layout = {
            'title': {
                'text': parsed_data.get("title", "Data Visualization"),
                'x': 0.5,
                'font': {'size': 18, 'family': 'Arial, sans-serif'}
            },
            'xaxis': {
                'title': 'Categories',
                'showgrid': True,
                'gridcolor': '#E1E5EA',
                'tickfont': {'size': 12}
            },
            'yaxis': {
                'title': 'Values',
                'showgrid': True,
                'gridcolor': '#E1E5EA',
                'tickfont': {'size': 12}
            },
            'plot_bgcolor': 'white',
            'paper_bgcolor': 'white',
            'margin': {'t': 60, 'b': 60, 'l': 60, 'r': 40}
        }
    
    return {
        'data': traces,
        'layout': layout
    }

def create_emergency_chart(data_str: str, error_msg: str) -> Dict:
    """
    Emergency fallback chart that ALWAYS works
    """
    print(f"🚨 EMERGENCY CHART - Creating fallback for: {error_msg}")
    
    # Extract any numbers from the string as a last resort
    numbers = re.findall(r'\d+', data_str)
    if numbers:
        y_values = [float(n) for n in numbers[:10]]
        x_values = [f"Value {i+1}" for i in range(len(y_values))]
    else:
        # Absolute minimum chart
        x_values = ["Error", "Fallback", "Data"]
        y_values = [1, 2, 1]
    
    return {
        'spec': {
            'data': [{
                'x': x_values,
                'y': y_values,
                'type': 'scatter',
                'mode': 'lines+markers',
                'name': 'Emergency Data',
                'line': {'color': '#E74C3C', 'width': 2},
                'marker': {'size': 6, 'color': '#E74C3C'}
            }],
            'layout': {
                'title': {
                    'text': f'Data Processing Error: {error_msg[:50]}...',
                    'x': 0.5,
                    'font': {'size': 16}
                },
                'xaxis': {'title': 'Index', 'showgrid': True},
                'yaxis': {'title': 'Value', 'showgrid': True},
                'plot_bgcolor': 'white',
                'paper_bgcolor': 'white',
                'margin': {'t': 60, 'b': 40, 'l': 60, 'r': 40}
            }
        }
    }

def create_agent():
    """
    Creates a Data Visualization Agent that can handle any data format
    """
    visualization_agent = ConversableAgent(
        name="Data-Visualization-Agent",
        llm_config=llm_config,
        system_message=visualization_agent_system_message,
        function_map={
            "create_visualization": create_visualization
        },
        human_input_mode="NEVER",
        max_consecutive_auto_reply=5,
        is_termination_msg=lambda x: x.get("content", "").rstrip().endswith("TERMINATE"),
    )
    
    return visualization_agent 