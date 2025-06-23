"""
Data Visualization Agent - PROPER AI VERSION with chronological sorting
"""

import json
import re
from typing import Optional

import pandas as pd
from autogen import ConversableAgent
from config import llm_config


def _parse_date(label: str) -> Optional[pd.Timestamp]:
    """Parse a date string into a Timestamp if possible."""
    if not isinstance(label, str) or not label.strip():
        return None
    for fmt in [None, "%Y-%m", "%B %Y", "%b %Y", "%Y"]:
        try:
            if fmt:
                dt = pd.to_datetime(label, format=fmt, errors="coerce")
            else:
                dt = pd.to_datetime(label, errors="coerce")
            if not pd.isna(dt):
                return dt
        except Exception:
            continue
    return None

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
        "chart_type": "line|bar|dual_line|scatter|pie",
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
    """Sort time-based data points using pandas date parsing."""

    for metric in analysis.get('metrics', []):
        data_points = metric.get("data_points", [])
        if not data_points:
            continue

        parsed = []
        for point in data_points:
            label = point.get("label", "")
            dt = _parse_date(label)
            parsed.append((dt if dt is not None else pd.Timestamp.max, point))

        parsed.sort(key=lambda x: x[0])
        metric["data_points"] = [p for _, p in parsed]

        labels = [p.get("label") for p in metric["data_points"]]
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
        'showlegend': True,
        'plot_bgcolor': 'white',
        'paper_bgcolor': 'white',
        'hovermode': 'x unified'
    }

    if chart_type != 'pie':
        layout['xaxis'] = {
            'title': 'Time',
            'type': 'category',
            'categoryorder': 'array',
            'categoryarray': complete_timeline,
            'tickangle': -45
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

        label_to_value = {p.get('label', '').strip(): p.get('value') for p in data_points if p.get('label')}

        x_values = []
        y_values = []
        for time_label in complete_timeline:
            x_values.append(time_label)
            val = label_to_value.get(time_label)
            try:
                y_values.append(float(val) if val is not None else None)
            except (ValueError, TypeError):
                y_values.append(None)

        if chart_type == 'pie':
            labels = [p.get('label') for p in data_points]
            values = [p.get('value') for p in data_points]
            trace = {
                'type': 'pie',
                'labels': labels,
                'values': values,
                'name': metric_name,
                'textinfo': 'percent+label'
            }
        else:
            trace = {
                'x': x_values,
                'y': y_values,
                'type': 'scatter',
                'mode': 'lines+markers',
                'name': metric_name,
                'line': {'color': color, 'width': 3},
                'marker': {'color': color, 'size': 8},
                'connectgaps': False
            }

            if chart_type == 'bar':
                trace['type'] = 'bar'
                trace.pop('mode', None)
                trace.pop('line', None)
            elif chart_type == 'scatter':
                trace['mode'] = 'markers'

            if axis == 'y2':
                trace['yaxis'] = 'y2'

        traces.append(trace)
        if chart_type != 'pie':
            print(f"🔍 {metric_name} timeline: X={x_values}, Y={y_values}")

        # Configure axes
        if axis == 'y1':
            layout['yaxis'] = {'title': axis_title, 'side': 'left'}
        elif axis == 'y2':
            layout['yaxis2'] = {'title': axis_title, 'side': 'right', 'overlaying': 'y'}
    
    final_chart = {'data': traces, 'layout': layout}
    print(f"🎯 BULLETPROOF Chart created with perfect timeline order: {complete_timeline}")
    return final_chart

def create_complete_timeline(metrics: list) -> list:
    """Create a complete chronological timeline from all metric labels."""

    labels = set()
    for metric in metrics:
        for point in metric.get("data_points", []):
            lbl = point.get("label", "").strip()
            if lbl:
                labels.add(lbl)

    parsed = []
    remainder = []
    for lbl in labels:
        dt = _parse_date(lbl)
        if dt is not None:
            parsed.append((dt, lbl))
        else:
            remainder.append(lbl)

    parsed.sort(key=lambda x: x[0])
    ordered = [l for _, l in parsed] + sorted(remainder)
    return ordered


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