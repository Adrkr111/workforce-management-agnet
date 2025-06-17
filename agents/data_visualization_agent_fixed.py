"""
Data Visualization Agent - PROPER AI VERSION with chronological sorting
"""

import json
import re
from autogen import ConversableAgent
from config import llm_config

visualization_agent_system_message = """
You are a specialized Data Visualization Agent with AI-powered analysis capabilities.

Your responsibilities:
1. Parse and understand data from ANY format using AI
2. Create appropriate charts based on data characteristics  
3. Ensure proper chronological ordering for time-based data
4. Handle different data types: forecasts, comparisons, trends, etc.
5. Return valid visualization specifications

Always respond with a dictionary containing a 'spec' key with chart specifications.
"""

def create_visualization(data_str: str):
    """Create visualization with AI analysis and proper chronological sorting"""
    
    print(f"🎯 Creating AI-powered visualization for: {data_str[:100]}...")
    
    try:
        # AI-powered data analysis
        analysis = analyze_data_with_ai(data_str)
        
        if analysis.get('success'):
            chart_spec = create_chart_from_ai_analysis(analysis, data_str)
            return str({'spec': chart_spec})
        else:
            # Fallback
            chart_spec = create_fallback_chart_spec(data_str)
            return str({'spec': chart_spec})
            
    except Exception as e:
        print(f"❌ Visualization error: {e}")
        return create_emergency_fallback(data_str)

def analyze_data_with_ai(text: str) -> dict:
    """AI-powered data analysis that can handle ANY data format"""
    
    analysis_prompt = f"""
    Analyze this data and extract structured information for visualization.
    
    DATA TO ANALYZE:
    {text}
    
    Instructions:
    1. Identify the data type (forecast, comparison, trend, etc.)
    2. Extract all data points with labels and values
    3. Determine appropriate chart type
    4. For time-based data, sort chronologically
    5. Return ONLY valid JSON
    
    Return JSON in this format:
    {{
        "success": true,
        "data_type": "forecast|comparison|trend|other",
        "chart_type": "line|bar|dual_line|scatter",
        "title": "Descriptive Title",
        "metrics": [
            {{
                "name": "Metric Name",
                "axis": "y1",
                "axis_title": "Axis Label", 
                "color": "#3498db",
                "data_points": [
                    {{"label": "Label", "value": number}},
                    ...
                ]
            }}
        ]
    }}
    
    CRITICAL: For time data, sort chronologically. Return ONLY JSON.
    """
    
    try:
        analysis_agent = ConversableAgent(
            name="data_analysis_agent",
            system_message="You are a data analyst. Analyze data and return ONLY valid JSON.",
            llm_config=llm_config,
            human_input_mode="NEVER"
        )
        
        response = analysis_agent.generate_reply(
            messages=[{"role": "user", "content": analysis_prompt}]
        )
        
        if isinstance(response, dict) and 'content' in response:
            response_text = response['content']
        else:
            response_text = str(response)
        
        # Extract JSON
        json_start = response_text.find('{')
        json_end = response_text.rfind('}') + 1
        
        if json_start != -1 and json_end > json_start:
            json_text = response_text[json_start:json_end]
            analysis_result = json.loads(json_text)
            
            if analysis_result.get('success') and 'metrics' in analysis_result:
                # Apply chronological sorting for time-based data
                analysis_result = sort_time_data_chronologically(analysis_result)
                print(f"✅ AI Analysis success: {analysis_result.get('title', 'Unknown')}")
                return analysis_result
            else:
                print("❌ AI analysis failed - invalid structure")
                return {"success": False}
        else:
            print("❌ AI analysis failed - no JSON found")
            return {"success": False}
            
    except Exception as e:
        print(f"❌ AI Analysis error: {e}")
        return {"success": False}

def sort_time_data_chronologically(analysis: dict) -> dict:
    """Sort time-based data points in chronological order"""
    
    def is_time_based(label: str) -> bool:
        """Check if label contains time information"""
        time_patterns = [
            r'\d{4}-\d{2}',  # YYYY-MM
            r'(jan|feb|mar|apr|may|jun|jul|aug|sep|oct|nov|dec)',  # Month names
            r'(january|february|march|april|may|june|july|august|september|october|november|december)',
            r'Q[1-4]',  # Quarters
            r'\d{4}'    # Years
        ]
        
        label_lower = label.lower()
        for pattern in time_patterns:
            if re.search(pattern, label_lower):
                return True
        return False
    
    def get_time_sort_key(label: str) -> tuple:
        """Generate sort key for time-based labels"""
        label_lower = label.lower()
        
        # Handle YYYY-MM format
        yyyy_mm_match = re.search(r'(\d{4})-(\d{2})', label)
        if yyyy_mm_match:
            year, month = int(yyyy_mm_match.group(1)), int(yyyy_mm_match.group(2))
            return (year, month, 0)
        
        # Handle month names
        months = {
            'jan': 1, 'january': 1, 'feb': 2, 'february': 2,
            'mar': 3, 'march': 3, 'apr': 4, 'april': 4,
            'may': 5, 'jun': 6, 'june': 6, 'jul': 7, 'july': 7,
            'aug': 8, 'august': 8, 'sep': 9, 'september': 9,
            'oct': 10, 'october': 10, 'nov': 11, 'november': 11,
            'dec': 12, 'december': 12
        }
        
        for month_name, month_num in months.items():
            if month_name in label_lower:
                # Try to extract year
                year_match = re.search(r'(\d{4})', label)
                year = int(year_match.group(1)) if year_match else 2025
                return (year, month_num, 0)
        
        # Handle quarters
        quarter_match = re.search(r'q([1-4])', label_lower)
        if quarter_match:
            quarter = int(quarter_match.group(1))
            year_match = re.search(r'(\d{4})', label)
            year = int(year_match.group(1)) if year_match else 2025
            return (year, quarter * 3, 0)  # Convert quarter to month
        
        # Handle year only
        year_match = re.search(r'(\d{4})', label)
        if year_match:
            year = int(year_match.group(1))
            return (year, 1, 0)
        
        return (9999, 99, 99)  # Put non-time data at end
    
    # Sort each metric's data points if they contain time data
    for metric in analysis.get('metrics', []):
        data_points = metric.get('data_points', [])
        if not data_points:
            continue
        
        # Check if this metric has time-based data
        first_label = data_points[0].get('label', '')
        if is_time_based(first_label):
            # Sort by time
            sorted_points = sorted(data_points, key=lambda x: get_time_sort_key(x.get('label', '')))
            metric['data_points'] = sorted_points
            
            labels = [p.get('label') for p in sorted_points]
            print(f"📅 Sorted time data for {metric.get('name', 'Unknown')}: {labels}")
    
    return analysis

def create_chart_from_ai_analysis(analysis: dict, original_text: str) -> dict:
    """Create chart with BULLETPROOF chronological sorting"""
    
    metrics = analysis.get('metrics', [])
    title = analysis.get('title', 'Data Visualization')
    chart_type = analysis.get('chart_type', 'line')
    
    if not metrics:
        return create_fallback_chart_spec(original_text)
    
    print(f"📊 Creating {chart_type} chart: {title}")
    
    # Create COMPLETE timeline for the data range
    complete_timeline = create_complete_timeline(metrics)
    print(f"📅 COMPLETE TIMELINE: {complete_timeline}")
    
    traces = []
    layout = {
        'title': title,
        'xaxis': {
            'title': 'Time',
            'type': 'category',
            'categoryorder': 'array',
            'categoryarray': complete_timeline,  # FORCE complete chronological order
            'tickangle': -45
        },
        'showlegend': len(metrics) > 1,
        'plot_bgcolor': 'white',
        'paper_bgcolor': 'white',
        'hovermode': 'x unified'
    }
    
    colors = ['#e74c3c', '#3498db', '#2ecc71', '#f39c12', '#9b59b6', '#1abc9c']
    
    for i, metric in enumerate(metrics):
        data_points = metric.get('data_points', [])
        metric_name = metric.get('name', f'Metric {i+1}')
        color = metric.get('color', colors[i % len(colors)])
        axis = metric.get('axis', 'y1')
        axis_title = metric.get('axis_title', 'Values')
        
        if not data_points:
            continue
        
        # Create mapping of label to value
        label_to_value = {}
        for point in data_points:
            label = point.get('label', '').strip()
            value = point.get('value')
            if label:
                label_to_value[label] = value
        
        # 🎯 BULLETPROOF FIX: Use COMPLETE timeline as X-axis, with None for missing data
        x_values = []
        y_values = []
        
        for time_label in complete_timeline:
            x_values.append(time_label)  # Always include ALL timeline points
            if time_label in label_to_value:
                try:
                    value = float(label_to_value[time_label]) if label_to_value[time_label] is not None else None
                    y_values.append(value)
                except (ValueError, TypeError):
                    y_values.append(None)
            else:
                y_values.append(None)  # Use None for missing data points
        
        # Create trace
        trace = {
            'x': x_values,
            'y': y_values,
            'type': 'scatter',
            'mode': 'lines+markers',
            'name': metric_name,
            'line': {'color': color, 'width': 3},
            'marker': {'color': color, 'size': 8},
            'connectgaps': False  # Show gaps for missing data
        }
        
        if chart_type == 'bar':
            trace['type'] = 'bar'
            trace.pop('mode', None)
            trace.pop('line', None)
        
        if axis == 'y2':
            trace['yaxis'] = 'y2'
        
        traces.append(trace)
        print(f"🔍 {metric_name} BULLETPROOF timeline:")
        print(f"   📅 X-axis: {x_values}")
        print(f"   📊 Y-axis: {y_values}")
        
        # Configure axes
        if axis == 'y1':
            layout['yaxis'] = {'title': axis_title, 'side': 'left'}
        elif axis == 'y2':
            layout['yaxis2'] = {'title': axis_title, 'side': 'right', 'overlaying': 'y'}
    
    final_chart = {'data': traces, 'layout': layout}
    print(f"🎯 BULLETPROOF Chart created with perfect timeline order: {complete_timeline}")
    return final_chart

def create_complete_timeline(metrics: list) -> list:
    """Create a complete chronological timeline from all data points"""
    
    # Collect all time labels from all metrics
    all_labels = set()
    for metric in metrics:
        for point in metric.get('data_points', []):
            label = point.get('label', '').strip()
            if label:
                all_labels.add(label)
    
    if not all_labels:
        return []
    
    # Determine the time format and create complete timeline
    sample_label = list(all_labels)[0].lower()
    
    if re.search(r'\d{4}-\d{2}', sample_label):
        # YYYY-MM format
        return create_yyyy_mm_timeline(all_labels)
    elif any(month in sample_label for month in ['jan', 'feb', 'mar', 'apr', 'may', 'jun', 'jul', 'aug', 'sep', 'oct', 'nov', 'dec']):
        # Month Year format
        return create_month_year_timeline(all_labels)
    else:
        # Fallback to simple sort
        return sorted(all_labels)

def create_month_year_timeline(labels: set) -> list:
    """Create complete timeline for Month Year format (e.g., 'Jan 2025', 'February 2025')"""
    
    # Parse all labels to get year-month pairs
    parsed_dates = []
    
    month_mapping = {
        'jan': 1, 'january': 1,
        'feb': 2, 'february': 2,
        'mar': 3, 'march': 3,
        'apr': 4, 'april': 4,
        'may': 5,
        'jun': 6, 'june': 6,
        'jul': 7, 'july': 7,
        'aug': 8, 'august': 8,
        'sep': 9, 'september': 9,
        'oct': 10, 'october': 10,
        'nov': 11, 'november': 11,
        'dec': 12, 'december': 12
    }
    
    month_names = {
        1: 'January', 2: 'February', 3: 'March', 4: 'April', 5: 'May', 6: 'June',
        7: 'July', 8: 'August', 9: 'September', 10: 'October', 11: 'November', 12: 'December'
    }
    
    for label in labels:
        label_lower = label.lower()
        
        # Find month
        found_month = 0
        for month_name, month_num in month_mapping.items():
            if month_name in label_lower:
                found_month = month_num
                break
        
        # Find year
        year_match = re.search(r'(\d{4})', label)
        found_year = int(year_match.group(1)) if year_match else 2025
        
        if found_month > 0:
            parsed_dates.append((found_year, found_month, label))
    
    if not parsed_dates:
        return sorted(labels)
    
    # Sort by year, month
    parsed_dates.sort(key=lambda x: (x[0], x[1]))
    
    # Get the range
    min_year, min_month = parsed_dates[0][0], parsed_dates[0][1]
    max_year, max_month = parsed_dates[-1][0], parsed_dates[-1][1]
    
    # Build complete timeline
    timeline = []
    current_year, current_month = min_year, min_month
    
    while (current_year, current_month) <= (max_year, max_month):
        # Use full month name consistently
        month_label = f"{month_names[current_month]} {current_year}"
        timeline.append(month_label)
        
        # Move to next month
        if current_month == 12:
            current_month = 1
            current_year += 1
        else:
            current_month += 1
    
    print(f"🗓️ Created complete timeline: {timeline}")
    return timeline

def create_yyyy_mm_timeline(labels: set) -> list:
    """Create complete timeline for YYYY-MM format"""
    
    parsed_dates = []
    for label in labels:
        match = re.search(r'(\d{4})-(\d{2})', label)
        if match:
            year, month = int(match.group(1)), int(match.group(2))
            parsed_dates.append((year, month))
    
    if not parsed_dates:
        return sorted(labels)
    
    parsed_dates.sort()
    min_year, min_month = parsed_dates[0]
    max_year, max_month = parsed_dates[-1]
    
    # Build complete timeline
    timeline = []
    current_year, current_month = min_year, min_month
    
    while (current_year, current_month) <= (max_year, max_month):
        timeline.append(f"{current_year}-{current_month:02d}")
        
        if current_month == 12:
            current_month = 1
            current_year += 1
        else:
            current_month += 1
    
    return timeline

def create_fallback_chart_spec(text: str) -> dict:
    """Emergency fallback chart"""
    print("🚨 Using fallback chart")
    
    return {
        'data': [],
        'layout': {
            'title': 'Data Visualization',
            'xaxis': {'title': 'Category'},
            'yaxis': {'title': 'Value'},
            'plot_bgcolor': 'white'
        }
    }

def create_emergency_fallback(text: str) -> str:
    """Emergency fallback"""
    chart_spec = create_fallback_chart_spec(text)
    return str({'spec': chart_spec})

def create_agent():
    """Create the PROPER AI visualization agent"""
    return ConversableAgent(
        name="Data-Visualization-Agent",
        system_message=visualization_agent_system_message,
        llm_config=llm_config,
        human_input_mode="NEVER",
        function_map={"create_visualization": create_visualization}
    ) 