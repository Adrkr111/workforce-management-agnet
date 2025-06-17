"""
Data Visualization Agent - Enhanced with AI-driven data analysis and chronological sorting
"""

import json
import re
from autogen import ConversableAgent
from config import llm_config

visualization_agent_system_message = """
You are a specialized Data Visualization Agent with AI-powered analysis capabilities.

Your responsibilities:
1. Parse and understand data from any format using AI
2. Create appropriate charts based on data characteristics  
3. Ensure proper chronological ordering for time-based data
4. Return valid visualization specifications

Always respond with a dictionary containing a 'spec' key with chart specifications.
"""

def create_visualization(data_str: str):
    """Create visualization with AI analysis and chronological sorting"""
    
    print(f"🎯 Creating visualization for data...")
    
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
    """AI-powered data analysis with explicit datetime sorting"""
    
    analysis_prompt = f"""
    Analyze this data and extract structured information for visualization:
    
    {text}
    
    Return JSON with this exact format:
    {{
        "success": true,
        "data_type": "dual_metric",
        "chart_type": "dual_line",
        "title": "Home Loan Attrition vs Early Repayment Correlation (FY 2025)",
        "metrics": [
            {{
                "name": "Home Loan Attrition Rate",
                "axis": "y1",
                "axis_title": "Attrition Rate (%)",
                "color": "#e74c3c",
                "data_points": [
                    {{"label": "Jan 2025", "value": 9.92}},
                    {{"label": "Feb 2025", "value": 6.81}},
                    {{"label": "Mar 2025", "value": 13.35}},
                    {{"label": "May 2025", "value": 13.66}},
                    {{"label": "Jun 2025", "value": 12.15}}
                ]
            }},
            {{
                "name": "Early Repayment Rate",
                "axis": "y2", 
                "axis_title": "Early Repayment Rate (%)",
                "color": "#3498db",
                "data_points": [
                    {{"label": "Jan 2025", "value": 60.82}},
                    {{"label": "Mar 2025", "value": 68.65}},
                    {{"label": "Apr 2025", "value": 64.22}},
                    {{"label": "May 2025", "value": 61.16}},
                    {{"label": "Jun 2025", "value": 73.6}}
                ]
            }}
        ]
    }}
    
    CRITICAL: Sort months chronologically (Jan, Feb, Mar, Apr, May, Jun). Return only JSON.
    """
    
    try:
        analysis_agent = ConversableAgent(
            name="data_analysis_agent",
            system_message="You are a data analyst. Return only valid JSON.",
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
                # Apply explicit chronological sorting
                analysis_result = sort_metrics_chronologically(analysis_result)
                print(f"✅ Analysis success: {len(analysis_result.get('metrics', []))} metrics")
                return analysis_result
            else:
                return {"success": False}
        else:
            return {"success": False}
            
    except Exception as e:
        print(f"❌ Analysis error: {e}")
        return {"success": False}

def sort_metrics_chronologically(analysis: dict) -> dict:
    """Sort all metrics data points in chronological order"""
    
    # Month order mapping
    month_order = {
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
    
    def get_month_order(label: str) -> int:
        """Extract month order from label"""
        label_lower = label.lower()
        for month, order in month_order.items():
            if month in label_lower:
                return order
        return 999  # Unknown months go to end
    
    # Sort each metric's data points
    for metric in analysis.get('metrics', []):
        data_points = metric.get('data_points', [])
        if data_points:
            # Sort by month order
            sorted_points = sorted(data_points, key=lambda x: get_month_order(x.get('label', '')))
            metric['data_points'] = sorted_points
            
            print(f"📅 Sorted {metric.get('name', 'Unknown')}: {[p.get('label') for p in sorted_points]}")
    
    return analysis

def sort_months_chronologically(months: list) -> list:
    """Sort month labels in chronological order"""
    
    month_order = {
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
    
    def get_month_order(month_label: str) -> int:
        """Extract month order from label"""
        label_lower = month_label.lower()
        for month, order in month_order.items():
            if month in label_lower:
                return order
        return 999  # Unknown months go to end
    
    # Sort months by chronological order
    sorted_months = sorted(months, key=get_month_order)
    print(f"🗓️ Month sort: {months} → {sorted_months}")
    return sorted_months

def create_chart_from_ai_analysis(analysis: dict, original_text: str) -> dict:
    """Create chart from AI analysis with FORCED chronological X-axis ordering"""
    
    metrics = analysis.get('metrics', [])
    title = analysis.get('title', 'Data Visualization')
    
    if not metrics:
        return create_fallback_chart_spec(original_text)
    
    print(f"📊 Creating chart: {title}")
    
    # Collect ALL unique month labels from all metrics
    all_months = set()
    for metric in metrics:
        for point in metric.get('data_points', []):
            month_label = point.get('label', '').strip()
            if month_label:
                all_months.add(month_label)
    
    # Sort months chronologically using our robust function
    sorted_months = sort_months_chronologically(list(all_months))
    print(f"📅 FINAL chronological order: {sorted_months}")
    
    traces = []
    layout = {
        'title': title,
        'xaxis': {
            'title': 'Month',
            'type': 'category',
            'categoryorder': 'array',
            'categoryarray': sorted_months  # FORCE this exact order
        },
        'showlegend': True,
        'plot_bgcolor': 'white',
        'paper_bgcolor': 'white',
        'hovermode': 'x unified'
    }
    
    for i, metric in enumerate(metrics):
        data_points = metric.get('data_points', [])
        metric_name = metric.get('name', f'Metric {i+1}')
        color = metric.get('color', '#3498db')
        axis = metric.get('axis', 'y1')
        axis_title = metric.get('axis_title', 'Values')
        
        if not data_points:
            continue
        
        # Create mapping of month to value
        month_to_value = {}
        for point in data_points:
            label = point.get('label', '').strip()
            value = point.get('value')
            if label:
                month_to_value[label] = value
        
        # Build trace data in exact chronological order
        x_values = []
        y_values = []
        
        for month in sorted_months:
            if month in month_to_value:
                x_values.append(month)
                try:
                    value = float(month_to_value[month]) if month_to_value[month] is not None else None
                    y_values.append(value)
                except (ValueError, TypeError):
                    y_values.append(None)
        
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
        
        # Assign to secondary y-axis if specified
        if axis == 'y2':
            trace['yaxis'] = 'y2'
        
        traces.append(trace)
        print(f"🔍 {metric_name} final X-axis: {x_values}")
        
        # Configure axes
        if axis == 'y1':
            layout['yaxis'] = {'title': axis_title, 'side': 'left'}
        elif axis == 'y2':
            layout['yaxis2'] = {'title': axis_title, 'side': 'right', 'overlaying': 'y'}
    
    final_chart = {'data': traces, 'layout': layout}
    print(f"🎯 Chart created with {len(traces)} traces")
    return final_chart

def create_fallback_chart_spec(text: str) -> dict:
    """Emergency fallback chart"""
    
    print("🚨 Using fallback chart")
    
    return {
        'data': [],
        'layout': {
            'title': 'Data Visualization',
            'xaxis': {'title': 'Time'},
            'yaxis': {'title': 'Value'},
            'plot_bgcolor': 'white'
        }
    }

def create_emergency_fallback(text: str) -> str:
    """Emergency fallback"""
    chart_spec = create_fallback_chart_spec(text)
    return str({'spec': chart_spec})

def create_agent():
    """Create the visualization agent"""
    return ConversableAgent(
        name="Data-Visualization-Agent",
        system_message=visualization_agent_system_message,
        llm_config=llm_config,
        human_input_mode="NEVER",
        function_map={"create_visualization": create_visualization}
    )