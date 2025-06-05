from autogen import ConversableAgent
from config import llm_config
from .promp_engineering.visualization_agent_prompt import visualization_agent_system_message
import json
import re
from typing import Dict, List, Union, Any
from datetime import datetime
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib
matplotlib.use('Agg')  # Use non-interactive backend
import io
import base64

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
    
    # Method 0: Handle case where input is already a dictionary
    if isinstance(data_str, dict):
        print("✅ Input is already a dictionary - using directly")
        return extract_from_dict(data_str)
    
    # Method 1: Try direct JSON parsing first
    try:
        data = json.loads(data_str)
        print("✅ JSON parsed successfully")
        return extract_from_json(data)
    except:
        print("📝 Direct JSON failed, trying to extract JSON from text...")
    
    # Method 2: Extract JSON from text (handles markdown code blocks)
    try:
        import re
        
        # Look for JSON in markdown code blocks
        json_pattern = r'```(?:json)?\s*(\{.*?\})\s*```'
        json_match = re.search(json_pattern, data_str, re.DOTALL)
        
        if json_match:
            json_str = json_match.group(1)
            print(f"🔍 Found JSON in markdown: {json_str[:100]}...")
            data = json.loads(json_str)
            print("✅ JSON from markdown parsed successfully")
            return extract_from_json(data)
            
    except Exception as e:
        print(f"📝 Markdown JSON extraction failed: {e}")
    
    # Method 3: Look for JSON objects anywhere in the text
    try:
        import re
        
        # Find JSON-like structures
        json_pattern = r'\{[^{}]*"[^"]*":\s*[^,}]*[^{}]*\}'
        json_matches = re.findall(json_pattern, data_str, re.DOTALL)
        
        for json_match in json_matches:
            try:
                # Expand to get the full JSON object
                start_idx = data_str.find(json_match)
                brace_count = 0
                end_idx = start_idx
                
                for i, char in enumerate(data_str[start_idx:], start_idx):
                    if char == '{':
                        brace_count += 1
                    elif char == '}':
                        brace_count -= 1
                        if brace_count == 0:
                            end_idx = i + 1
                            break
                
                full_json = data_str[start_idx:end_idx]
                print(f"🔍 Attempting to parse extracted JSON: {full_json[:100]}...")
                data = json.loads(full_json)
                print("✅ Extracted JSON parsed successfully")
                return extract_from_json(data)
                
            except Exception as e:
                print(f"⚠️ Failed to parse JSON match: {e}")
                continue
                
    except Exception as e:
        print(f"📝 JSON pattern extraction failed: {e}")
    
    # Method 4: Fallback to text extraction
    print("🔍 All JSON parsing failed, falling back to text extraction...")
    return extract_from_text(str(data_str))

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
    Extract from dictionary data - ENHANCED WITH COMPARISON MODE SUPPORT
    """
    # 🔄 HANDLE COMPARISON MODE
    if data.get("comparison_mode"):
        print("🔄 Processing comparison visualization")
        
        datasets = data.get("datasets", [])
        if len(datasets) < 2:
            print("⚠️ Insufficient datasets for comparison")
            return {"type": "error", "x": ["Error"], "y": [0], "title": "Insufficient Data for Comparison"}
        
        teams_data = {}
        colors = ['#2E86C1', '#E74C3C', '#28B463', '#F39C12', '#8E44AD', '#17A2B8']
        
        print(f"🔄 Processing {len(datasets)} datasets for comparison")
        
        for i, dataset in enumerate(datasets):
            label = dataset.get("label", f"Dataset {i+1}")
            points = dataset.get("points", [])
            
            if points:
                # Extract x and y values from points
                x_values = [point.get("date", "") for point in points]
                y_values = [point.get("value", 0) for point in points]
                
                teams_data[label] = {
                    "x": x_values,
                    "y": y_values,
                    "color": colors[i % len(colors)]
                }
                
                print(f"✅ Added comparison dataset: {label} ({len(points)} points)")
            else:
                print(f"⚠️ No data points for dataset: {label}")
        
        if len(teams_data) >= 2:
            return {
                "type": "multi_series_comparison",
                "teams": teams_data,
                "title": f"Forecast Comparison: {' vs '.join(teams_data.keys())}"
            }
        else:
            print("❌ Failed to create comparison data")
            return {"type": "error", "x": ["Error"], "y": [0], "title": "Comparison Data Processing Failed"}
    
    # Check if it's already processed data with teams
    if "teams" in data:
        return data
    
    # ✅ ENHANCED: Handle forecast_data structure specifically
    if "forecast_data" in data:
        print("🔍 Found forecast_data structure!")
        forecast_data = data["forecast_data"]
        
        if isinstance(forecast_data, list) and len(forecast_data) > 0:
            if isinstance(forecast_data[0], dict):
                print(f"📊 Processing forecast_data list with {len(forecast_data)} points")
                
                # Extract directly from forecast_data list
                dates = []
                values = []
                
                for item in forecast_data:
                    date_val = item.get("date", "")
                    value_val = item.get("value", 0)
                    
                    dates.append(str(date_val))
                    values.append(safe_float(value_val))
                
                print(f"📅 Extracted dates: {dates[:3]}... to {dates[-1] if dates else 'none'}")
                print(f"📊 Extracted values: {values[:3]}... to {values[-1] if values else 'none'}")
                
                # Build title from metadata
                business = data.get("business", "")
                substream = data.get("substream", "")
                team = data.get("team", "")
                
                title_parts = []
                if business:
                    title_parts.append(business.title())
                if substream:
                    title_parts.append(substream.upper())
                if team:
                    title_parts.append(team.title())
                
                if title_parts:
                    title = f"Volume Forecast - {' '.join(title_parts)}"
                else:
                    title = "Volume Forecast"
                
                print(f"📋 Chart title: {title}")
                
                return {
                    "type": "forecast_data_series",
                    "x": dates,
                    "y": values,
                    "title": title,
                    "business": business,
                    "substream": substream,
                    "team": team
                }
    
    # ✅ FORECAST DATA FIX - Handle forecast data structure specifically  
    if "Forecast" in data or "forecast" in data:
        print("🔍 Found forecast data structure!")
        forecast_data = data.get("Forecast") or data.get("forecast")
        
        if isinstance(forecast_data, dict):
            # Extract date-value pairs from forecast
            dates = list(forecast_data.keys())
            values = list(forecast_data.values())
            
            print(f"📅 Raw dates: {dates[:3]}...")
            print(f"📊 Raw values: {values[:3]}...")
            
            # Convert dates to readable format
            formatted_dates = []
            for date in dates:
                try:
                    # Try to format dates nicely
                    if isinstance(date, str) and len(date) == 10:  # YYYY-MM-DD format
                        year, month, day = date.split('-')
                        # Use short month format: 2025-06, 2025-07, etc.
                        formatted_dates.append(f"{year}-{month}")
                    else:
                        formatted_dates.append(str(date))
                except:
                    formatted_dates.append(str(date))
            
            business = data.get("Business", data.get("business", ""))
            stream = data.get("Stream", data.get("stream", ""))
            team = data.get("Team", data.get("team", ""))
            
            # Create meaningful title
            title_parts = []
            if business:
                title_parts.append(business.title())
            if stream:
                title_parts.append(stream.upper())
            if team:
                title_parts.append(team.title())
            
            if title_parts:
                title = f"Volume Forecast - {' '.join(title_parts)}"
            else:
                title = "Volume Forecast"
            
            print(f"📊 Extracted {len(dates)} forecast points:")
            print(f"   📅 Dates: {formatted_dates[:3]}... to {formatted_dates[-1] if formatted_dates else 'none'}")
            print(f"   📊 Values: {values[:3]}... to {values[-1] if values else 'none'}")
            print(f"   📋 Title: {title}")
            
            return {
                "type": "forecast_series",
                "x": formatted_dates,
                "y": [safe_float(v) for v in values],
                "title": title,
                "business": business,
                "stream": stream,
                "team": team
            }
    
    # Check if it's a nested structure
    if "data" in data and isinstance(data["data"], list):
        return extract_from_list(data["data"])
    
    # Simple key-value pairs (existing functionality)
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
    Create Plotly spec that ALWAYS works - ENHANCED WITH COMPARISON MODE SUPPORT
    """
    data_type = parsed_data.get("type", "simple")
    
    # Color palette for multi-series
    colors = [
        '#2E86C1', '#E74C3C', '#28B463', '#F39C12', 
        '#8E44AD', '#17A2B8', '#FD7E14', '#20C997'
    ]
    
    # 🔄 COMPARISON MODE VISUALIZATION
    if data_type == "multi_series_comparison" and "teams" in parsed_data:
        print("🔄 Creating multi-series comparison chart")
        
        traces = []
        teams = parsed_data["teams"]
        team_names = list(teams.keys())
        
        # Add primary data series for each team
        for i, (team_name, team_data) in enumerate(teams.items()):
            color = team_data.get("color", colors[i % len(colors)])
            traces.append({
                'x': team_data["x"],
                'y': team_data["y"],
                'type': 'scatter',
                'mode': 'lines+markers',
                'name': team_name,
                'line': {'color': color, 'width': 3},
                'marker': {'size': 8, 'color': color},
                'yaxis': 'y'
            })
            
            print(f"✅ Added primary trace: {team_name} ({len(team_data['y'])} points)")
        
        # 📊 ADD DELTA/DIFFERENCE CALCULATION for 2-team comparison
        if len(teams) == 2:
            team_list = list(teams.values())
            team1_data, team2_data = team_list[0], team_list[1]
            team1_name, team2_name = team_names[0], team_names[1]
            
            print(f"📊 Calculating delta between {team1_name} and {team2_name}")
            
            # Calculate differences (assuming same x-axis dates or align by index)
            min_length = min(len(team1_data["y"]), len(team2_data["y"]))
            if min_length > 0:
                deltas = []
                delta_x = []
                
                for i in range(min_length):
                    try:
                        y1 = float(team1_data["y"][i])
                        y2 = float(team2_data["y"][i])
                        delta = y2 - y1
                        deltas.append(delta)
                        
                        # Use x-axis from first team
                        if i < len(team1_data["x"]):
                            delta_x.append(team1_data["x"][i])
                        else:
                            delta_x.append(f"Point {i+1}")
                            
                    except (ValueError, TypeError):
                        print(f"⚠️ Error calculating delta for point {i}")
                        continue
                
                if deltas:
                    # Add delta trace on secondary y-axis
                    traces.append({
                        'x': delta_x,
                        'y': deltas,
                        'type': 'scatter',
                        'mode': 'lines',
                        'name': f'Δ ({team2_name} - {team1_name})',
                        'line': {'color': '#FFA500', 'width': 2, 'dash': 'dash'},
                        'yaxis': 'y2'  # Use secondary y-axis for delta
                    })
                    
                    print(f"✅ Added delta trace with {len(deltas)} difference points")
                    
                    # Calculate delta statistics
                    avg_delta = sum(deltas) / len(deltas)
                    max_delta = max(deltas)
                    min_delta = min(deltas)
                    
                    print(f"📊 Delta Statistics: Avg={avg_delta:.1f}, Max={max_delta:.1f}, Min={min_delta:.1f}")
        
        # Enhanced layout for comparison
        layout = {
            'title': {
                'text': parsed_data.get("title", "Team Comparison"),
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
                'title': 'Forecast Volume',
                'side': 'left',
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
            'margin': {'t': 60, 'b': 60, 'l': 60, 'r': 140}
        }
        
        # Add secondary y-axis if we have delta data
        if len(teams) == 2 and any(trace.get('yaxis') == 'y2' for trace in traces):
            layout['yaxis2'] = {
                'title': 'Difference (Δ)',
                'side': 'right',
                'overlaying': 'y',
                'showgrid': False,
                'tickfont': {'size': 12, 'color': '#FFA500'},
                'titlefont': {'color': '#FFA500'}
            }
            
            print("✅ Added secondary y-axis for delta visualization")
        
        print(f"✅ Created comparison chart with {len(traces)} traces")
        return {
            'data': traces,
            'layout': layout
        }
    
    # 🔄 EXISTING MULTI-SERIES LOGIC (for backward compatibility)
    elif data_type == "multi_series" and "teams" in parsed_data:
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
        # Single series chart (existing logic)
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

def create_visualization_with_pandas(data_str: str) -> Dict:
    """
    Alternative visualization using pandas DataFrame + matplotlib
    """
    try:
        print(f"\n🐼 PANDAS VIZ - Processing: {data_str[:200]}...")
        
        # Parse the data
        parsed_data = smart_parse_any_format(data_str)
        
        # Extract data for DataFrame
        x_data = parsed_data.get("x", ["Data"])
        y_data = parsed_data.get("y", [1])
        title = parsed_data.get("title", "Data Visualization")
        
        print(f"📊 DataFrame data: {len(x_data)} points")
        print(f"📋 Sample: {x_data[:3]} -> {y_data[:3]}")
        
        # Create DataFrame
        df = pd.DataFrame({
            'x': x_data,
            'y': y_data
        })
        
        # Create the plot
        plt.figure(figsize=(12, 6))
        
        # Plot based on data type
        if parsed_data.get("type") in ["forecast_data_series", "forecast_series"]:
            # Time series plot
            df.plot(x='x', y='y', kind='line', marker='o', linewidth=3, markersize=8, color='#2E86C1')
            plt.xticks(rotation=45)
        else:
            # Bar plot for other data
            df.plot(x='x', y='y', kind='bar', color='#2E86C1')
            plt.xticks(rotation=45)
        
        plt.title(title, fontsize=16, fontweight='bold')
        plt.xlabel('Date' if 'date' in title.lower() or 'forecast' in title.lower() else 'Categories')
        plt.ylabel('Volume' if 'forecast' in title.lower() else 'Values')
        plt.grid(True, alpha=0.3)
        plt.tight_layout()
        
        # Convert to base64 PNG
        buffer = io.BytesIO()
        plt.savefig(buffer, format='png', dpi=150, bbox_inches='tight')
        buffer.seek(0)
        png_base64 = base64.b64encode(buffer.getvalue()).decode()
        plt.close()  # Important: close to free memory
        
        print(f"✅ PANDAS VIZ SUCCESS - Created PNG chart")
        
        return {
            'type': 'pandas_chart',
            'png_base64': png_base64,
            'title': title,
            'data_points': len(x_data)
        }
        
    except Exception as e:
        print(f"⚠️ PANDAS VIZ ERROR: {e}")
        return create_emergency_chart(data_str, str(e))

def create_agent():
    """
    Creates a Data Visualization Agent that can handle any data format
    """
    visualization_agent = ConversableAgent(
        name="Data-Visualization-Agent",
        llm_config=llm_config,
        system_message=visualization_agent_system_message,
        function_map={
            "create_visualization": create_visualization,
            "create_visualization_with_pandas": create_visualization_with_pandas
        },
        human_input_mode="NEVER",
        max_consecutive_auto_reply=5,
        is_termination_msg=lambda x: x.get("content", "").rstrip().endswith("TERMINATE"),
    )
    
    return visualization_agent 