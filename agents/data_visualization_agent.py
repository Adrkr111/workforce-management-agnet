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

def create_visualization(data_str: str):
    """
    🎯 SIMPLE BULLETPROOF VISUALIZATION AGENT
    
    Rules:
    1. Find data patterns (dates + numbers)
    2. If 2+ datasets: create comparison
    3. If 1 dataset: create single chart  
    4. NEVER FAIL - always return something useful
    """
    
    print("🎯 SIMPLE VIZ AGENT - NO NONSENSE APPROACH")
    text = str(data_str)
    
    try:
        # 📊 STEP 1: Find all date-number pairs
        import re
        from datetime import datetime
        
        # Simple patterns - find any date followed by a number
        date_number_pairs = []
        
        # Pattern 1: 2025-06-01: 2845
        matches1 = re.findall(r'(\d{4}-\d{2}-\d{2})[^0-9]*(\d+)', text)
        for date, num in matches1:
            date_number_pairs.append((date, int(num), 'iso'))
            
        # Pattern 2: June 2025: 3141  
        matches2 = re.findall(r'((?:Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)[a-z]*\s+\d{4})[^0-9]*(\d+)', text, re.IGNORECASE)
        for date, num in matches2:
            date_number_pairs.append((date, int(num), 'month'))
            
        print(f"📊 Found {len(date_number_pairs)} data points")
        
        if len(date_number_pairs) < 2:
            return create_simple_fallback(text)
            
        # 📊 STEP 2: Split into datasets by detecting breaks in the data
        datasets = []
        current_dataset = []
        current_format = None
        
        for date, value, format_type in date_number_pairs:
            if current_format is None:
                current_format = format_type
                current_dataset = [(date, value)]
            elif format_type == current_format:
                current_dataset.append((date, value))
            else:
                # Format changed - new dataset
                if current_dataset:
                    datasets.append((current_dataset, current_format))
                current_dataset = [(date, value)]
                current_format = format_type
                
        # Add final dataset
        if current_dataset:
            datasets.append((current_dataset, current_format))
            
        print(f"📂 Split into {len(datasets)} datasets")
        
        # 📊 STEP 3: Create the chart
        if len(datasets) >= 2:
            return create_comparison_chart(datasets, text)
        else:
            return create_single_chart(datasets[0], text)
            
    except Exception as e:
        print(f"❌ Error: {e}")
        return create_simple_fallback(text)

def create_comparison_chart(datasets, text):
    """
    📊 CREATE CLEAN 2-SERIES COMPARISON
    """
    # Take first 2 datasets only
    dataset1, format1 = datasets[0] 
    dataset2, format2 = datasets[1]
    
    # Convert dates to standard format
    x1, y1 = standardize_dataset(dataset1, format1)
    x2, y2 = standardize_dataset(dataset2, format2)
    
    # Detect team names
    team1 = "Team 1"
    team2 = "Team 2"
    
    if "logistics" in text.lower():
        team1 = "Logistics Team"
    if "retail" in text.lower():
        team2 = "Retail Team"
        
    traces = [
        {
            'x': x1,
            'y': y1,
            'type': 'scatter',
            'mode': 'lines+markers',
            'name': team1,
            'line': {'color': '#2E86C1', 'width': 3},
            'marker': {'color': '#2E86C1', 'size': 8}
        },
        {
            'x': x2,
            'y': y2,
            'type': 'scatter',
            'mode': 'lines+markers', 
            'name': team2,
            'line': {'color': '#E74C3C', 'width': 3},
            'marker': {'color': '#E74C3C', 'size': 8}
        }
    ]
    
    layout = {
        'title': f'Forecast Comparison: {team1} vs {team2}',
        'xaxis': {'title': 'Time Period', 'tickangle': -45},
        'yaxis': {'title': 'Volume'},
        'showlegend': True,
        'plot_bgcolor': 'white'
    }
    
    spec = {'data': traces, 'layout': layout}
    print(f"✅ Created comparison: {team1} vs {team2}")
    return str({'spec': spec})

def create_single_chart(dataset_info, text):
    """
    📊 CREATE SINGLE SERIES CHART
    """
    dataset, format_type = dataset_info
    x, y = standardize_dataset(dataset, format_type)
    
    team_name = "Business Forecast"
    if "logistics" in text.lower():
        team_name = "Logistics Forecast"
    elif "retail" in text.lower():
        team_name = "Retail Forecast"
        
    trace = {
        'x': x,
        'y': y,
        'type': 'scatter',
        'mode': 'lines+markers',
        'name': team_name,
        'line': {'color': '#2E86C1', 'width': 3},
        'marker': {'color': '#2E86C1', 'size': 8}
    }
    
    layout = {
        'title': team_name,
        'xaxis': {'title': 'Time Period', 'tickangle': -45},
        'yaxis': {'title': 'Volume'},
        'showlegend': False,
        'plot_bgcolor': 'white'
    }
    
    spec = {'data': [trace], 'layout': layout}
    print(f"✅ Created single chart: {team_name}")
    return str({'spec': spec})

def standardize_dataset(dataset, format_type):
    """
    🧹 CLEAN AND STANDARDIZE DATES
    """
    from datetime import datetime
    
    x_vals = []
    y_vals = []
    
    for date_str, value in dataset:
        try:
            if format_type == 'iso':
                # 2025-06-01 -> Jun 2025
                dt = datetime.strptime(date_str, '%Y-%m-%d')
                clean_date = dt.strftime('%b %Y')
            else:
                # June 2025 -> Jun 2025  
                try:
                    dt = datetime.strptime(date_str, '%B %Y')
                    clean_date = dt.strftime('%b %Y')
                except:
                    # Already in short format
                    clean_date = date_str
                    
            x_vals.append(clean_date)
            y_vals.append(value)
        except:
            # Skip bad data
            continue
            
    return x_vals, y_vals

def create_simple_fallback(text):
    """
    🚨 SIMPLE FALLBACK - EXTRACT ANY NUMBERS
    """
    import re
    numbers = re.findall(r'\d+', text)
    
    if len(numbers) >= 2:
        values = [int(n) for n in numbers[:8]]  # Max 8 points
        labels = [f'Data {i+1}' for i in range(len(values))]
        
        trace = {
            'x': labels,
            'y': values,
            'type': 'bar',
            'marker': {'color': '#3498db'}
        }
        
        layout = {
            'title': 'Data Visualization',
            'xaxis': {'title': 'Data Points'},
            'yaxis': {'title': 'Values'},
            'plot_bgcolor': 'white'
        }
        
        spec = {'data': [trace], 'layout': layout}
        print("✅ Created fallback bar chart")
        return str({'spec': spec})
    else:
        # Ultimate fallback
        spec = {
            'data': [{'x': ['Input'], 'y': [len(text)], 'type': 'bar', 'marker': {'color': '#95a5a6'}}],
            'layout': {'title': 'Input Analysis', 'plot_bgcolor': 'white'}
        }
        print("✅ Created text analysis fallback")
        return str({'spec': spec})

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