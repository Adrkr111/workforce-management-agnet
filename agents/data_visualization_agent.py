from autogen import ConversableAgent
from config import llm_config
from .promp_engineering.visualization_agent_prompt import visualization_agent_system_message
import json
import re
from typing import Dict, List, Union, Any
from datetime import datetime
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import matplotlib
matplotlib.use('Agg')  # Use non-interactive backend
import io
import base64

def create_visualization(data_str: str) -> Dict:
    """
    UNIVERSAL VISUALIZATION FUNCTION - Handles ANY data type, ANY structure
    """
    try:
        # 🔥 RAW DATA LOGGING - COMPLETE INPUT DUMP
        print(f"\n🎨 UNIVERSAL VIZ - COMPLETE INPUT DUMP:")
        print(f"📝 Input Type: {type(data_str)}")
        print(f"📦 Input Size: {len(str(data_str))} characters")
        print(f"🔥 RAW COMPLETE DATA:")
        print(f"{'='*50}")
        print(str(data_str))
        print(f"{'='*50}")
        
        if isinstance(data_str, dict):
            print(f"📊 DICT RAW STRUCTURE:")
            for key, value in data_str.items():
                print(f"   🔑 [{key}] ({type(value)}): {str(value)[:200]}{'...' if len(str(value)) > 200 else ''}")
        elif isinstance(data_str, list):
            print(f"📋 LIST RAW STRUCTURE:")
            for i, item in enumerate(data_str[:5]):
                print(f"   🔢 [{i}] ({type(item)}): {str(item)[:200]}{'...' if len(str(item)) > 200 else ''}")
        
        print(f"🎨 UNIVERSAL VIZ - Processing: {str(data_str)[:200]}...")
        
        # Step 1: Universal data extraction
        parsed_data = universal_data_parser(data_str)
        
        # 🔥 RAW PARSED DATA LOGGING
        print(f"🔥 RAW PARSED DATA OUTPUT:")
        print(f"📝 Parsed Type: {type(parsed_data)}")
        if isinstance(parsed_data, dict):
            for key, value in parsed_data.items():
                print(f"   🔑 [{key}] ({type(value)}): {str(value)[:200]}{'...' if len(str(value)) > 200 else ''}")
        
        # Step 2: Create universal plotly specification
        plotly_spec = create_universal_plotly_spec(parsed_data)
        
        # 🔥 RAW PLOTLY SPEC LOGGING
        print(f"🔥 RAW PLOTLY SPEC OUTPUT:")
        print(f"📊 Spec Keys: {list(plotly_spec.keys()) if isinstance(plotly_spec, dict) else 'Not a dict'}")
        if 'data' in plotly_spec:
            print(f"📈 Data Traces: {len(plotly_spec['data'])}")
            for i, trace in enumerate(plotly_spec['data'][:3]):
                print(f"   📋 Trace [{i}]:")
                for key, value in trace.items():
                    print(f"      🔑 [{key}]: {str(value)[:100]}{'...' if len(str(value)) > 100 else ''}")
        
        # Step 3: Always return proper format for cl.Plotly
        result = {
            'spec': plotly_spec
        }
        
        print(f"✅ UNIVERSAL VIZ SUCCESS - Created chart with {len(plotly_spec.get('data', []))} traces")
        return result
        
    except Exception as e:
        print(f"⚠️ UNIVERSAL VIZ FALLBACK - Error: {e}")
        # NEVER fail - always return a valid chart
        return create_emergency_chart(data_str, str(e))

def universal_data_parser(data_input: Any) -> Dict:
    """
    UNIVERSAL DATA PARSER - Handles ANY data format imaginable
    """
    print("🌍 UNIVERSAL PARSER - Starting analysis...")
    
    # Stage 1: Handle direct data types
    if isinstance(data_input, dict):
        print("✅ Input is dictionary - using universal dict parser")
        return parse_any_dict(data_input)
    
    if isinstance(data_input, list):
        print("✅ Input is list - using universal list parser")
        return parse_any_list(data_input)
    
    if isinstance(data_input, (int, float)):
        print("✅ Input is single number")
        return {"type": "single_number", "x": ["Value"], "y": [float(data_input)], "title": f"Value: {data_input}"}
    
    # Stage 2: String parsing - extract structured data
    data_str = str(data_input)
    
    # Try JSON parsing first
    json_data = extract_json_from_string(data_str)
    if json_data:
        print("✅ Extracted JSON from string")
        return universal_data_parser(json_data)
    
    # Try CSV/table parsing
    table_data = extract_table_from_string(data_str)
    if table_data:
        print("✅ Extracted table data from string")
        return table_data
    
    # Try number extraction
    number_data = extract_numbers_from_string(data_str)
    if number_data:
        print("✅ Extracted numbers from string")
        return number_data
    
    # Try key-value extraction
    kv_data = extract_key_values_from_string(data_str)
    if kv_data:
        print("✅ Extracted key-value pairs from string")
        return kv_data
    
    # Ultimate fallback
    print("⚠️ Using fallback text analysis")
    return {"type": "text_fallback", "x": ["Text"], "y": [len(data_str)], "title": "Text Length Analysis"}

def parse_any_dict(data: Dict) -> Dict:
    """
    UNIVERSAL DICTIONARY PARSER - Handles ANY dictionary structure
    """
    print(f"📊 UNIVERSAL DICT PARSER - Processing {len(data)} keys")
    
    # 🔄 COMPARISON MODE DETECTION
    if data.get("comparison_mode") or "compare" in str(data).lower():
        return handle_comparison_data(data)
    
    # 📊 FORECAST DATA DETECTION (but not limited to it)
    if any(key in data for key in ["forecast", "Forecast", "forecast_data", "prediction"]):
        forecast_result = handle_forecast_data(data)
        if forecast_result["type"] != "error":
            return forecast_result
    
    # 📋 MULTI-DATASET DETECTION
    if "datasets" in data or "data" in data:
        multi_result = handle_multi_dataset(data)
        if multi_result["type"] != "error":
            return multi_result
    
    # 🔍 TIME SERIES DETECTION
    time_result = detect_time_series(data)
    if time_result["type"] != "error":
        return time_result
    
    # 📈 SIMPLE NUMERIC DATA
    numeric_result = extract_numeric_data(data)
    if numeric_result["type"] != "error":
        return numeric_result
    
    # 🔄 NESTED STRUCTURE HANDLING
    nested_result = handle_nested_structures(data)
    if nested_result["type"] != "error":
        return nested_result
    
    # Fallback - create something from whatever we have
    return create_fallback_from_dict(data)

def parse_any_list(data: List) -> Dict:
    """
    UNIVERSAL LIST PARSER - Handles ANY list structure
    """
    print(f"📋 UNIVERSAL LIST PARSER - Processing {len(data)} items")
    
    if not data:
        return {"type": "empty", "x": ["No Data"], "y": [0], "title": "Empty Dataset"}
    
    # Check first item to determine list type
    first_item = data[0]
    
    # List of dictionaries
    if isinstance(first_item, dict):
        return handle_dict_list(data)
    
    # List of numbers
    if isinstance(first_item, (int, float)):
        return {
            "type": "number_list",
            "x": [f"Item {i+1}" for i in range(len(data))],
            "y": [float(x) for x in data],
            "title": f"Numeric Data ({len(data)} points)"
        }
    
    # List of strings
    if isinstance(first_item, str):
        return handle_string_list(data)
    
    # List of lists (matrix)
    if isinstance(first_item, list):
        return handle_matrix_data(data)
    
    # Mixed list
    return handle_mixed_list(data)

def handle_comparison_data(data: Dict) -> Dict:
    """
    Handle comparison data - IMPROVED to handle all comparison types
    """
    print("🔄 UNIVERSAL COMPARISON HANDLER")
    
    datasets = data.get("datasets", [])
    
    # If no explicit datasets, try to find multiple data series
    if not datasets:
        datasets = find_multiple_series(data)
    
    if len(datasets) < 2:
        print("⚠️ Insufficient datasets for comparison")
        return {"type": "error"}
    
    teams_data = {}
    colors = ['#2E86C1', '#E74C3C', '#28B463', '#F39C12', '#8E44AD', '#17A2B8', '#FD7E14', '#20C997']
    
    print(f"🔄 Processing {len(datasets)} datasets for comparison")
    
    for i, dataset in enumerate(datasets):
        label = extract_dataset_label(dataset, i)
        x_values, y_values = extract_xy_from_dataset(dataset)
        
        if x_values and y_values:
            teams_data[label] = {
                "x": x_values,
                "y": y_values,
                "color": colors[i % len(colors)]
            }
            print(f"✅ Added comparison dataset: {label} ({len(y_values)} points)")
    
    if len(teams_data) >= 2:
        return {
            "type": "multi_series_comparison",
            "teams": teams_data,
            "title": f"Data Comparison: {' vs '.join(list(teams_data.keys())[:3])}"
        }
    
    return {"type": "error"}

def handle_forecast_data(data: Dict) -> Dict:
    """
    Handle forecast data - ENHANCED but not limited to forecasts only
    """
    print("📊 UNIVERSAL FORECAST HANDLER")
    
    # Multiple ways to find forecast data
    forecast_data = (data.get("forecast") or data.get("Forecast") or 
                    data.get("forecast_data") or data.get("prediction") or
                    data.get("predictions"))
    
    if not forecast_data:
        return {"type": "error"}
    
    # Handle different forecast formats
    if isinstance(forecast_data, dict):
        # Date-value pairs
        dates = list(forecast_data.keys())
        values = [safe_float(v) for v in forecast_data.values()]
        
        return {
            "type": "forecast_series",
            "x": [format_date_string(d) for d in dates],
            "y": values,
            "title": build_title(data, "Forecast"),
            "metadata": extract_metadata(data)
        }
    
    elif isinstance(forecast_data, list):
        # List of data points
        x_values, y_values = extract_xy_from_list(forecast_data)
        
        return {
            "type": "forecast_series",
            "x": x_values,
            "y": y_values,
            "title": build_title(data, "Forecast"),
            "metadata": extract_metadata(data)
        }
    
    return {"type": "error"}

def handle_dict_list(data: List[Dict]) -> Dict:
    """
    UNIVERSAL DICT LIST HANDLER - Works with any dictionary structure
    """
    print(f"📋 DICT LIST HANDLER - Analyzing {len(data)} records")
    
    # Get all possible field names
    all_fields = set()
    for item in data:
        if isinstance(item, dict):
            all_fields.update(item.keys())
    
    print(f"🔑 All fields found: {sorted(all_fields)}")
    
    # Universal field detection
    x_field = detect_x_field_universal(all_fields)
    y_field = detect_y_field_universal(all_fields)
    group_field = detect_group_field_universal(all_fields)
    
    print(f"📊 Selected fields - X: {x_field}, Y: {y_field}, Group: {group_field}")
    
    # Extract data based on detected fields
    if group_field:
        return extract_grouped_data(data, x_field, y_field, group_field)
    else:
        return extract_simple_data(data, x_field, y_field)

def detect_x_field_universal(fields: set) -> str:
    """
    UNIVERSAL X-FIELD DETECTION - Works for any data type
    """
    # Priority patterns for X-axis (ordered by likelihood)
    x_patterns = [
        # Time-based fields
        ['date', 'time', 'timestamp', 'period', 'month', 'year', 'day'],
        # ID/sequence fields  
        ['id', 'index', 'seq', 'number', 'order', 'step', 'iteration'],
        # Category fields
        ['name', 'label', 'category', 'type', 'class', 'group'],
        # Location fields
        ['location', 'city', 'country', 'region', 'area', 'zone'],
        # Generic fields
        ['x', 'key', 'item', 'element', 'field']
    ]
    
    for pattern_group in x_patterns:
        for pattern in pattern_group:
            matches = [f for f in fields if pattern in f.lower()]
            if matches:
                print(f"🎯 X-field match: {matches[0]} (pattern: {pattern})")
                return matches[0]
    
    # Use first field as fallback
    field_list = sorted(list(fields))
    return field_list[0] if field_list else 'index'

def detect_y_field_universal(fields: set) -> str:
    """
    UNIVERSAL Y-FIELD DETECTION - Works for any numeric data
    """
    # Priority patterns for Y-axis (ordered by likelihood)
    y_patterns = [
        # Common numeric fields
        ['value', 'amount', 'count', 'quantity', 'volume', 'size'],
        # Financial fields
        ['cost', 'price', 'revenue', 'profit', 'budget', 'expense'],
        # Measurement fields
        ['score', 'rating', 'percentage', 'rate', 'ratio', 'level'],
        # Workforce fields
        ['ftes', 'headcount', 'employees', 'staff', 'resources'],
        # Statistical fields
        ['total', 'sum', 'average', 'mean', 'median', 'max', 'min'],
        # Generic numeric fields
        ['y', 'val', 'num', 'data', 'metric', 'measure', 'result']
    ]
    
    for pattern_group in y_patterns:
        for pattern in pattern_group:
            matches = [f for f in fields if pattern in f.lower()]
            if matches:
                print(f"🎯 Y-field match: {matches[0]} (pattern: {pattern})")
                return matches[0]
    
    # Look for fields with numeric-looking names
    for field in fields:
        if any(indicator in field.lower() for indicator in ['_value', '_count', '_total', '_sum', '_avg']):
            print(f"🎯 Y-field numeric indicator: {field}")
            return field
    
    # Find field with most numeric values
    return find_most_numeric_field(fields)

def detect_group_field_universal(fields: set) -> str:
    """
    UNIVERSAL GROUP FIELD DETECTION - For multi-series data
    """
    group_patterns = [
        'team', 'group', 'category', 'type', 'class', 'department',
        'business', 'unit', 'division', 'segment', 'stream', 'branch',
        'region', 'area', 'zone', 'location', 'site', 'office'
    ]
    
    for pattern in group_patterns:
        matches = [f for f in fields if pattern in f.lower()]
        if matches:
            print(f"🎯 Group field match: {matches[0]} (pattern: {pattern})")
            return matches[0]
    
    return None

def find_most_numeric_field(fields: set) -> str:
    """
    Find the field most likely to contain numeric data
    """
    # This is a heuristic - in practice, we'd check actual data
    numeric_indicators = ['value', 'count', 'total', 'amount', 'number', 'qty', 'vol']
    
    for indicator in numeric_indicators:
        matches = [f for f in fields if indicator in f.lower()]
        if matches:
            return matches[0]
    
    # Fallback to second field or first field
    field_list = sorted(list(fields))
    return field_list[1] if len(field_list) > 1 else field_list[0] if field_list else 'value'

def extract_grouped_data(data: List[Dict], x_field: str, y_field: str, group_field: str) -> Dict:
    """
    Extract multi-series data grouped by a field
    """
    print(f"📊 EXTRACTING GROUPED DATA: {group_field}")
    
    groups = {}
    for item in data:
        if not isinstance(item, dict):
            continue
            
        group = str(item.get(group_field, 'Unknown')).strip()
        if not group:
            group = 'Unknown'
            
        if group not in groups:
            groups[group] = {"x": [], "y": []}
        
        x_val = item.get(x_field, '')
        y_val = item.get(y_field, 0)
        
        groups[group]["x"].append(str(x_val))
        groups[group]["y"].append(safe_float(y_val))
    
    print(f"📊 Found {len(groups)} groups: {list(groups.keys())}")
    
    return {
        "type": "multi_series",
        "teams": groups,
        "title": f"{y_field.title()} by {group_field.title()}"
    }

def extract_simple_data(data: List[Dict], x_field: str, y_field: str) -> Dict:
    """
    Extract single-series data
    """
    print(f"📊 EXTRACTING SIMPLE DATA: {x_field} vs {y_field}")
    
    x_values = []
    y_values = []
    
    for item in data:
        if not isinstance(item, dict):
            continue
            
        x_val = item.get(x_field, '')
        y_val = item.get(y_field, 0)
        
        x_values.append(str(x_val))
        y_values.append(safe_float(y_val))
    
    return {
        "type": "single_series",
        "x": x_values,
        "y": y_values,
        "title": f"{y_field.title()} vs {x_field.title()}"
    }

def extract_json_from_string(text: str) -> Any:
    """
    Extract JSON from any string format
    """
    try:
        # Direct JSON
        return json.loads(text)
    except:
        pass
    
    try:
        # JSON in markdown code blocks
        json_pattern = r'```(?:json)?\s*(\{.*?\})\s*```'
        match = re.search(json_pattern, text, re.DOTALL)
        if match:
            return json.loads(match.group(1))
    except:
        pass
    
    try:
        # JSON objects anywhere in text
        json_pattern = r'\{[^{}]*"[^"]*":[^}]*\}'
        matches = re.findall(json_pattern, text, re.DOTALL)
        for match in matches:
            try:
                return json.loads(match)
            except:
                continue
    except:
        pass
    
    return None

def extract_table_from_string(text: str) -> Dict:
    """
    Extract tabular data from string (CSV, TSV, etc.)
    """
    try:
        # Try different separators
        for sep in [',', '\t', '|', ';']:
            lines = text.strip().split('\n')
            if len(lines) < 2:
                continue
                
            # Check if this looks like a table
            first_row = lines[0].split(sep)
            second_row = lines[1].split(sep)
            
            if len(first_row) >= 2 and len(second_row) == len(first_row):
                print(f"📋 Found table with separator: '{sep}'")
                
                headers = [h.strip() for h in first_row]
                data_rows = []
                
                for line in lines[1:]:
                    row = [cell.strip() for cell in line.split(sep)]
                    if len(row) == len(headers):
                        data_rows.append(dict(zip(headers, row)))
                
                if data_rows:
                    return parse_any_list(data_rows)
    except:
        pass
    
    return None

def extract_numbers_from_string(text: str) -> Dict:
    """
    Extract numeric data from any string
    """
    # Find all numbers
    numbers = re.findall(r'-?\d*\.?\d+', text)
    
    if len(numbers) >= 2:  # Need at least 2 points for a chart
        y_values = [float(n) for n in numbers[:50]]  # Limit to 50 points
        x_values = [f"Point {i+1}" for i in range(len(y_values))]
        
        return {
            "type": "numeric_extraction",
            "x": x_values,
            "y": y_values,
            "title": f"Numeric Data ({len(y_values)} points)"
        }
    
    return None

def extract_key_values_from_string(text: str) -> Dict:
    """
    Extract key-value pairs from string
    """
    # Look for key:value or key=value patterns
    patterns = [
        r'(\w+):\s*([+-]?\d*\.?\d+)',  # key: number
        r'(\w+)=([+-]?\d*\.?\d+)',     # key=number
        r'(\w+)\s+([+-]?\d*\.?\d+)'    # key number
    ]
    
    for pattern in patterns:
        matches = re.findall(pattern, text)
        if len(matches) >= 2:
            keys = [m[0] for m in matches]
            values = [float(m[1]) for m in matches]
            
            return {
                "type": "key_value_pairs",
                "x": keys,
                "y": values,
                "title": "Key-Value Data"
            }
    
    return None

def handle_string_list(data: List[str]) -> Dict:
    """
    Handle list of strings
    """
    # Try to extract numbers from strings
    numeric_values = []
    labels = []
    
    for item in data:
        numbers = re.findall(r'-?\d*\.?\d+', str(item))
        if numbers:
            numeric_values.append(float(numbers[0]))
            labels.append(str(item))
        else:
            labels.append(str(item))
    
    if numeric_values and len(numeric_values) == len(data):
        return {
            "type": "string_numeric",
            "x": labels,
            "y": numeric_values,
            "title": "String Data with Numeric Values"
        }
    else:
        # Word frequency or category count
        unique_items = list(set(data))
        counts = [data.count(item) for item in unique_items]
        
        return {
            "type": "string_frequency",
            "x": unique_items,
            "y": counts,
            "title": "String Frequency"
        }

def handle_matrix_data(data: List[List]) -> Dict:
    """
    Handle matrix/2D array data
    """
    if not data or not data[0]:
        return {"type": "error"}
    
    # Use first row as headers if they look like strings
    if all(isinstance(item, str) for item in data[0]):
        headers = data[0]
        matrix_data = data[1:]
    else:
        headers = [f"Col_{i+1}" for i in range(len(data[0]))]
        matrix_data = data
    
    # Convert to list of dictionaries
    dict_list = []
    for row in matrix_data:
        if len(row) == len(headers):
            dict_list.append(dict(zip(headers, row)))
    
    return handle_dict_list(dict_list)

def handle_mixed_list(data: List) -> Dict:
    """
    Handle list with mixed data types
    """
    # Try to convert everything to numeric
    numeric_data = []
    labels = []
    
    for i, item in enumerate(data):
        if isinstance(item, (int, float)):
            numeric_data.append(float(item))
            labels.append(f"Item {i+1}")
        elif isinstance(item, str):
            numbers = re.findall(r'-?\d*\.?\d+', item)
            if numbers:
                numeric_data.append(float(numbers[0]))
                labels.append(item)
            else:
                numeric_data.append(i)  # Use index
                labels.append(item)
        else:
            numeric_data.append(i)  # Use index
            labels.append(str(item))
    
    return {
        "type": "mixed_data",
        "x": labels,
        "y": numeric_data,
        "title": "Mixed Data Types"
    }

def detect_time_series(data: Dict) -> Dict:
    """
    Detect and handle time series data
    """
    # Look for time-related keys
    time_keys = ['date', 'time', 'timestamp', 'period', 'month', 'year']
    
    for key in data.keys():
        if any(time_word in key.lower() for time_word in time_keys):
            # Found potential time series
            time_data = data[key]
            if isinstance(time_data, dict):
                dates = list(time_data.keys())
                values = [safe_float(v) for v in time_data.values()]
                
                return {
                    "type": "time_series",
                    "x": [format_date_string(d) for d in dates],
                    "y": values,
                    "title": f"Time Series: {key.title()}"
                }
    
    return {"type": "error"}

def extract_numeric_data(data: Dict) -> Dict:
    """
    Extract any numeric data from dictionary
    """
    numeric_pairs = []
    
    for key, value in data.items():
        if isinstance(value, (int, float)):
            numeric_pairs.append((key, float(value)))
        elif isinstance(value, str):
            numbers = re.findall(r'-?\d*\.?\d+', value)
            if numbers:
                numeric_pairs.append((key, float(numbers[0])))
    
    if len(numeric_pairs) >= 2:
        keys = [pair[0] for pair in numeric_pairs]
        values = [pair[1] for pair in numeric_pairs]
        
        return {
            "type": "numeric_dict",
            "x": keys,
            "y": values,
            "title": "Numeric Data"
        }
    
    return {"type": "error"}

def handle_nested_structures(data: Dict) -> Dict:
    """
    Handle nested dictionary structures
    """
    # Look for nested data
    for key, value in data.items():
        if isinstance(value, dict) and len(value) >= 2:
            result = universal_data_parser(value)
            if result["type"] != "error":
                result["title"] = f"{key.title()}: {result.get('title', 'Data')}"
                return result
        elif isinstance(value, list) and len(value) >= 2:
            result = universal_data_parser(value)
            if result["type"] != "error":
                result["title"] = f"{key.title()}: {result.get('title', 'Data')}"
                return result
    
    return {"type": "error"}

def create_fallback_from_dict(data: Dict) -> Dict:
    """
    Create visualization from any dictionary as last resort
    """
    # Get keys and try to assign numeric values
    keys = list(data.keys())[:10]  # Limit to 10 items
    values = []
    
    for key in keys:
        value = data[key]
        if isinstance(value, (int, float)):
            values.append(float(value))
        elif isinstance(value, str):
            values.append(len(value))  # String length
        elif isinstance(value, list):
            values.append(len(value))  # List length
        elif isinstance(value, dict):
            values.append(len(value))  # Dict length
        else:
            values.append(1)  # Default value
    
    return {
        "type": "dict_fallback",
        "x": keys,
        "y": values,
        "title": "Data Structure Overview"
    }

def find_multiple_series(data: Dict) -> List:
    """
    Find multiple data series in a dictionary
    """
    series = []
    
    for key, value in data.items():
        if isinstance(value, dict) and len(value) >= 2:
            series.append({"label": key, "data": value})
        elif isinstance(value, list) and len(value) >= 2:
            series.append({"label": key, "data": value})
    
    return series

def extract_dataset_label(dataset: Any, index: int) -> str:
    """
    Extract label from dataset
    """
    if isinstance(dataset, dict):
        return (dataset.get("label") or dataset.get("name") or 
                dataset.get("title") or f"Dataset {index + 1}")
    else:
        return f"Dataset {index + 1}"

def extract_xy_from_dataset(dataset: Any) -> tuple:
    """
    Extract X and Y values from any dataset format
    """
    if isinstance(dataset, dict):
        if "data" in dataset:
            return extract_xy_from_dataset(dataset["data"])
        elif "points" in dataset:
            return extract_xy_from_list(dataset["points"])
        elif len(dataset) >= 2:
            keys = list(dataset.keys())
            values = [safe_float(v) for v in dataset.values()]
            return keys, values
    elif isinstance(dataset, list):
        return extract_xy_from_list(dataset)
    
    return [], []

def extract_xy_from_list(data: List) -> tuple:
    """
    Extract X and Y from list data
    """
    if not data:
        return [], []
    
    if isinstance(data[0], dict):
        # List of dictionaries
        x_values = []
        y_values = []
        
        # Find best x and y fields
        all_fields = set()
        for item in data:
            if isinstance(item, dict):
                all_fields.update(item.keys())
        
        x_field = detect_x_field_universal(all_fields)
        y_field = detect_y_field_universal(all_fields)
        
        for item in data:
            if isinstance(item, dict):
                x_values.append(str(item.get(x_field, '')))
                y_values.append(safe_float(item.get(y_field, 0)))
        
        return x_values, y_values
    else:
        # Simple list
        x_values = [f"Point {i+1}" for i in range(len(data))]
        y_values = [safe_float(v) for v in data]
        return x_values, y_values

def build_title(data: Dict, default: str) -> str:
    """
    Build meaningful title from data
    """
    title_parts = []
    
    # Look for common title fields
    title_fields = ['title', 'name', 'business', 'team', 'department', 'category']
    
    for field in title_fields:
        value = data.get(field) or data.get(field.title())
        if value:
            title_parts.append(str(value).title())
    
    if title_parts:
        return f"{default}: {' - '.join(title_parts)}"
    else:
        return default

def extract_metadata(data: Dict) -> Dict:
    """
    Extract metadata from data
    """
    metadata = {}
    
    meta_fields = ['business', 'team', 'department', 'category', 'type', 'unit', 'source']
    
    for field in meta_fields:
        value = data.get(field) or data.get(field.title())
        if value:
            metadata[field] = str(value)
    
    return metadata

def format_date_string(date_str: str) -> str:
    """
    Format date string for display
    """
    try:
        if isinstance(date_str, str) and len(date_str) == 10:  # YYYY-MM-DD
            year, month, day = date_str.split('-')
            return f"{year}-{month}"
        else:
            return str(date_str)
    except:
        return str(date_str)

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

def create_universal_plotly_spec(parsed_data: Dict) -> Dict:
    """
    Create Plotly spec that works with ANY data type
    """
    data_type = parsed_data.get("type", "simple")
    
    # Color palette for multi-series
    colors = [
        '#2E86C1', '#E74C3C', '#28B463', '#F39C12', 
        '#8E44AD', '#17A2B8', '#FD7E14', '#20C997',
        '#6C757D', '#495057', '#FF6B6B', '#4ECDC4'
    ]
    
    # 🔄 MULTI-SERIES COMPARISON
    if data_type in ["multi_series_comparison", "multi_series"]:
        print("🔄 Creating multi-series visualization")
        
        traces = []
        teams = parsed_data.get("teams", {})
        
        for i, (team_name, team_data) in enumerate(teams.items()):
            color = team_data.get("color", colors[i % len(colors)])
            
            trace = {
                'x': team_data.get("x", []),
                'y': team_data.get("y", []),
                'type': 'scatter',
                'mode': 'lines+markers',
                'name': str(team_name),
                'line': {'color': color, 'width': 3},
                'marker': {'size': 8, 'color': color}
            }
            traces.append(trace)
            print(f"✅ Added trace: {team_name} ({len(team_data.get('y', []))} points)")
        
        # 📊 ADD DIFFERENCE CALCULATION for 2-series comparison
        if len(teams) == 2:
            team_list = list(teams.values())
            if len(team_list[0].get("y", [])) == len(team_list[1].get("y", [])):
                y1 = team_list[0]["y"]
                y2 = team_list[1]["y"]
                diff = [y2[i] - y1[i] for i in range(len(y1))]
                
                traces.append({
                    'x': team_list[0]["x"],
                    'y': diff,
                    'type': 'scatter',
                    'mode': 'lines',
                    'name': 'Difference',
                    'line': {'color': '#FF6B6B', 'width': 2, 'dash': 'dash'},
                    'yaxis': 'y2'
                })
                print("✅ Added difference trace")
        
        layout = {
            'title': {'text': parsed_data.get("title", "Multi-Series Data"), 'font': {'size': 16}},
            'xaxis': {'title': 'X-Axis', 'showgrid': True},
            'yaxis': {'title': 'Values', 'showgrid': True},
            'legend': {'x': 0, 'y': 1.1, 'orientation': 'h'},
            'hovermode': 'x unified',
            'showlegend': True
        }
        
        # Add secondary y-axis if we have difference
        if len(traces) > len(teams):
            layout['yaxis2'] = {
                'title': 'Difference',
                'overlaying': 'y',
                'side': 'right',
                'showgrid': False
            }
        
        return {'data': traces, 'layout': layout}
    
    # 📊 SINGLE SERIES DATA
    elif data_type in ["single_series", "forecast_series", "forecast_data_series", 
                       "time_series", "numeric_extraction", "key_value_pairs"]:
        print("📊 Creating single-series visualization")
        
        x_data = parsed_data.get("x", [])
        y_data = parsed_data.get("y", [])
        
        # Determine chart type based on data
        if any(word in data_type for word in ["time", "forecast", "date"]):
            chart_type = 'scatter'
            mode = 'lines+markers'
        else:
            chart_type = 'bar' if len(x_data) <= 20 else 'scatter'
            mode = 'markers' if chart_type == 'scatter' else None
        
        trace = {
            'x': x_data,
            'y': y_data,
            'type': chart_type,
            'name': parsed_data.get("title", "Data"),
            'marker': {'color': colors[0], 'size': 8} if chart_type == 'scatter' else {'color': colors[0]},
        }
        
        if mode:
            trace['mode'] = mode
            trace['line'] = {'color': colors[0], 'width': 3}
        
        layout = {
            'title': {'text': parsed_data.get("title", "Data Visualization"), 'font': {'size': 16}},
            'xaxis': {'title': 'X-Axis', 'showgrid': True},
            'yaxis': {'title': 'Values', 'showgrid': True},
            'hovermode': 'closest',
            'showlegend': False
        }
        
        return {'data': [trace], 'layout': layout}
    
    # 📈 SIMPLE LISTS AND NUMBERS
    elif data_type in ["number_list", "string_frequency", "mixed_data", "dict_fallback"]:
        print("📈 Creating simple data visualization")
        
        x_data = parsed_data.get("x", [])
        y_data = parsed_data.get("y", [])
        
        # Use bar chart for categorical data
        trace = {
            'x': x_data,
            'y': y_data,
            'type': 'bar',
            'name': parsed_data.get("title", "Data"),
            'marker': {'color': colors[:len(x_data)] if len(x_data) <= len(colors) else colors[0]}
        }
        
        layout = {
            'title': {'text': parsed_data.get("title", "Data Overview"), 'font': {'size': 16}},
            'xaxis': {'title': 'Categories', 'showgrid': True},
            'yaxis': {'title': 'Values', 'showgrid': True},
            'hovermode': 'closest',
            'showlegend': False
        }
        
        return {'data': [trace], 'layout': layout}
    
    # 🚨 EMERGENCY FALLBACK
    else:
        print(f"🚨 Creating emergency fallback for type: {data_type}")
        
        trace = {
            'x': ['Data'],
            'y': [1],
            'type': 'bar',
            'name': 'Data Present',
            'marker': {'color': colors[0]}
        }
        
        layout = {
            'title': {'text': 'Data Visualization', 'font': {'size': 16}},
            'xaxis': {'title': 'Data', 'showgrid': True},
            'yaxis': {'title': 'Count', 'showgrid': True},
            'showlegend': False
        }
        
        return {'data': [trace], 'layout': layout}

def create_emergency_chart(data_str: str, error_msg: str) -> Dict:
    """
    Create emergency chart when everything else fails
    """
    print(f"🚨 EMERGENCY CHART: {error_msg}")
    
    # Try to extract ANY numbers from the input
    numbers = re.findall(r'-?\d*\.?\d+', str(data_str))
    
    if numbers and len(numbers) >= 2:
        y_values = [float(n) for n in numbers[:10]]
        x_values = [f"Value {i+1}" for i in range(len(y_values))]
        
        trace = {
            'x': x_values,
            'y': y_values,
            'type': 'scatter',
            'mode': 'lines+markers',
            'name': 'Extracted Data',
            'line': {'color': '#E74C3C', 'width': 3},
            'marker': {'color': '#E74C3C', 'size': 8}
        }
        
        title = f"Emergency Data Extraction ({len(y_values)} points)"
    else:
        # Absolute emergency - just show that we received data
        trace = {
            'x': ['Input Received'],
            'y': [len(str(data_str))],
            'type': 'bar',
            'name': 'Data Length',
            'marker': {'color': '#FD7E14'}
        }
        
        title = "Emergency Visualization"
    
    layout = {
        'title': {'text': title, 'font': {'size': 16}},
        'xaxis': {'title': 'Data Points', 'showgrid': True},
        'yaxis': {'title': 'Values', 'showgrid': True},
        'annotations': [{
            'text': f"Error: {error_msg[:100]}{'...' if len(error_msg) > 100 else ''}",
            'x': 0.5,
            'y': 0.95,
            'xref': 'paper',
            'yref': 'paper',
            'showarrow': False,
            'font': {'color': 'red', 'size': 12}
        }],
        'showlegend': False
    }
    
    return {
        'spec': {
            'data': [trace],
            'layout': layout
        }
    }

def create_agent():
    """
    Create the universal data visualization agent
    """
    agent = ConversableAgent(
        name="Data-Visualization-Agent",
        system_message=visualization_agent_system_message,
        llm_config=llm_config,
        human_input_mode="NEVER",
    )
    
    # Register the universal visualization function
    agent.register_for_execution()(create_visualization)
    agent.register_for_llm(description="Create visualization from ANY data format")(create_visualization)
    
    return agent 