"""
Enhanced Visualization Agent with AI-powered data analysis and universal plotting capabilities.
Supports line, bar, pie, scatter, and dual-axis charts with professional styling.
"""

import json
import re
from datetime import datetime
from autogen import ConversableAgent
from config import llm_config

class VisualizationAgent:
    def __init__(self):
        self.name = "Data-Visualization-Agent"
        self.system_message = """You are a specialized Data Visualization Agent with AI-powered analysis capabilities.
Your responsibilities:
1. Parse and understand data from ANY format using AI.
2. Create appropriate charts (line, bar, pie, scatter, dual-axis) based on data characteristics and user requests.
3. Ensure proper chronological ordering for time-based data.
4. Handle different data types: forecasts, comparisons, trends, KPIs, categorical, part-to-whole.
5. Return valid, professional Plotly visualization specifications with detailed styling, annotations, and legends."""
        self.llm_config = llm_config

    def create_visualization(self, data_str: str):
        """Create visualization with AI analysis and proper chart selection/styling"""
        print(f"🎯 Creating AI-powered visualization for: {data_str[:150]}...")
        try:
            user_chart_type = self._extract_chart_type_from_user(data_str)
            print(f"[DEBUG] User requested chart type: {user_chart_type}")
            analysis = self._analyze_data_with_ai(data_str, user_chart_type)
            llm_chart_type = analysis.get('chart_type', '')
            print(f"[DEBUG] LLM suggested chart type: {llm_chart_type}")
            # Always prioritize user request if present
            final_chart_type = user_chart_type if user_chart_type else llm_chart_type
            print(f"[DEBUG] Final chart type used for rendering: {final_chart_type}")
            
            if analysis.get('success'):
                chart_spec = self._create_chart_from_ai_analysis(analysis, final_chart_type)
                return str({'spec': chart_spec})
            else:
                print("🚨 AI analysis failed. Using fallback.")
                chart_spec = self._create_fallback_chart_spec("AI analysis could not process the data.")
                return str({'spec': chart_spec})
                
        except Exception as e:
            print(f"❌ Top-level visualization error: {e}")
            return str({'spec': self._create_fallback_chart_spec(str(e))})

    def _extract_chart_type_from_user(self, text: str) -> str:
        """Detect if the user requested a specific chart type (bar, pie, etc.)"""
        lowered = text.lower()
        if 'bar plot' in lowered or 'bar chart' in lowered:
            return 'bar'
        if 'pie chart' in lowered or 'pie plot' in lowered:
            return 'pie'
        if 'scatter' in lowered:
            return 'scatter'
        if 'line' in lowered:
            return 'line'
        return ''  # Let AI decide

    def _analyze_data_with_ai(self, text: str, chart_type_hint: str = "") -> dict:
        """ENTERPRISE-LEVEL PROMPT: Enforce user chart type requests with explicit, high-priority instructions and examples"""
        chart_type_instruction = ""
        if chart_type_hint:
            chart_type_instruction = f"""
7. **CRITICAL ENTERPRISE RULE:** If the user requests a specific chart type (e.g., '{chart_type_hint}'), you MUST output 'chart_type': '{chart_type_hint}' and structure the data for that chart type. Do NOT use any other chart type. This is a hard requirement. If you do not follow this, it will be considered a system failure.
8. **NEGATIVE INSTRUCTION:** Do NOT use 'line', 'scatter', or any other chart type if the user requests 'bar'.
9. **EXAMPLE:**
If the user says 'bar plot', your output MUST look like this:
{
  "success": true,
  "data_type": "categorical",
  "chart_type": "bar",
  "title": "Home Loan Attrition Rates (Last Quarter)",
  "metrics": [
    {
      "name": "Home Loan Attrition Rate",
      "axis": "y1",
      "axis_title": "Attrition Rate (%)",
      "data_points": [
        {"label": "January 2025", "value": 9.92},
        {"label": "February 2025", "value": 6.81},
        {"label": "March 2025", "value": 13.35}
      ]
    }
  ]
}
"""
        analysis_prompt = f"""
Analyze the data below and extract structured information for visualization.

**Data to Analyze:**
---
{text}
---

**Instructions:**
1.  **Identify Metrics:** Detect all distinct metrics (e.g., "Home Loan Attrition Rate", "Early Repayment Rate").
2.  **Extract Data Points:** For each metric, extract all (label, value) pairs. Labels are typically time-based or categorical. Values are numeric. Remove percentage signs from values.
3.  **Handle Missing Data:** Notice where data is missing for a given metric. The extracted data should reflect this.
4.  **Determine Chart Type:** Based on the data and user request, choose the best chart type: 'line', 'bar', 'pie', 'dual_line', or 'scatter'.
5.  **Create Title:** Generate a descriptive title for the chart.
6.  **Return ONLY JSON:** Your entire output must be a single, valid JSON object.{chart_type_instruction}

**JSON Output Format:**
{{
    "success": true,
    "data_type": "comparison|categorical|part_to_whole|trend|other",
    "chart_type": "line|bar|pie|dual_line|scatter",
    "title": "Descriptive Title",
    "metrics": [
        {{
            "name": "Metric Name",
            "axis": "y1|y2",
            "axis_title": "Axis Label",
            "data_points": [
                {{"label": "Label", "value": number}},
                ...
            ]
        }}
    ]
}}
"""
        try:
            analysis_agent = ConversableAgent(
                name="data_analysis_agent",
                system_message="You are a data analyst. Your only output is a single valid JSON object based on the user's request. Do not add any commentary.",
                llm_config=self.llm_config,
                human_input_mode="NEVER"
            )
            response = analysis_agent.generate_reply(
                messages=[{"role": "user", "content": analysis_prompt}]
            )
            response_text = response if isinstance(response, str) else response.get('content', '')
            json_match = re.search(r'\{.*\}', response_text, re.DOTALL)
            if json_match:
                json_text = json_match.group(0)
                analysis_result = json.loads(json_text)
                print("✅ AI Analysis successful.")
                return analysis_result
            else:
                print("❌ AI Analysis error: No JSON object found in response.")
                return {"success": False, "error": "No JSON found in AI response"}
        except Exception as e:
            print(f"❌ AI Analysis error: {e}")
            return {"success": False, "error": str(e)}

    def _create_chart_from_ai_analysis(self, analysis: dict, user_chart_type: str = "") -> dict:
        """Create chart with bulletproof chronological/categorical sorting and professional styling"""
        metrics = analysis.get('metrics', [])
        title = analysis.get('title', 'Data Visualization')
        chart_type = user_chart_type or analysis.get('chart_type', 'line')
        
        if not metrics:
            return self._create_fallback_chart_spec("No metrics found in AI analysis.")

        print(f"📊 Creating chart: {title} (type: {chart_type})")
        
        # Professional color palette
        colors = ['#e74c3c', '#3498db', '#2ecc71', '#f39c12', '#9b59b6', '#1abc9c', '#8e44ad', '#34495e']
        traces = []
        layout = {
            'title': {'text': title, 'x': 0.5, 'font': {'size': 22, 'family': 'Arial Black'}},
            'showlegend': True,
            'legend': {'orientation': 'h', 'x': 0.5, 'xanchor': 'center', 'y': -0.2, 'font': {'size': 14}},
            'plot_bgcolor': '#fcfcfc',
            'paper_bgcolor': '#fcfcfc',
            'hovermode': 'x unified',
            'margin': {'l': 60, 'r': 30, 't': 80, 'b': 80}
        }
        
        # Determine x-axis (time, category, or part-to-whole)
        if chart_type in ['line', 'dual_line', 'scatter', 'bar']:
            x_labels = self._create_complete_timeline_or_categories(metrics)
            layout['xaxis'] = {
                'title': 'Time' if self._is_time_axis(x_labels) else 'Category',
                'type': 'category',
                'categoryorder': 'array',
                'categoryarray': x_labels,
                'tickangle': -30,
                'tickfont': {'size': 13, 'family': 'Arial'}
            }
        
        # Y-axis styling
        layout['yaxis'] = {'title': '', 'side': 'left', 'showgrid': True, 'gridcolor': '#e1e1e1', 'tickfont': {'size': 13, 'family': 'Arial'}}
        layout['yaxis2'] = {'title': '', 'side': 'right', 'overlaying': 'y', 'showgrid': False, 'tickfont': {'size': 13, 'family': 'Arial'}}
        
        # Handle each chart type
        if chart_type == 'pie':
            # Only the first metric is used for pie
            metric = metrics[0]
            labels = [p['label'] for p in metric['data_points']]
            values = [p['value'] for p in metric['data_points']]
            trace = {
                'type': 'pie',
                'labels': labels,
                'values': values,
                'name': metric['name'],
                'hole': 0.4,
                'textinfo': 'percent+label',
                'textfont': {'size': 15},
                'marker': {'colors': colors},
                'pull': [0.05]*len(labels),
                'showlegend': True
            }
            traces.append(trace)
            layout['legend']['orientation'] = 'v'
            layout['legend']['x'] = 1.05
            layout['legend']['y'] = 0.5
            layout['margin']['r'] = 120
        else:
            for i, metric in enumerate(metrics):
                data_points = metric.get('data_points', [])
                metric_name = metric.get('name', f'Metric {i+1}')
                color = colors[i % len(colors)]
                axis = metric.get('axis', 'y1')
                axis_title = metric.get('axis_title', 'Values')
                label_to_value = {p.get('label'): p.get('value') for p in data_points if p.get('label')}
                y_values = [float(label_to_value.get(x, None)) if label_to_value.get(x, None) is not None else None for x in x_labels]
                
                if chart_type == 'bar':
                    trace = {
                        'x': x_labels,
                        'y': y_values,
                        'type': 'bar',
                        'name': metric_name,
                        'marker': {'color': color, 'line': {'width': 1, 'color': '#333'}},
                        'text': [f"{v:,.2f}" if v is not None else '' for v in y_values],
                        'textposition': 'outside',
                        'hoverinfo': 'x+y+name',
                        'opacity': 0.92
                    }
                elif chart_type == 'scatter':
                    trace = {
                        'x': x_labels,
                        'y': y_values,
                        'type': 'scatter',
                        'mode': 'markers',
                        'name': metric_name,
                        'marker': {'color': color, 'size': 12, 'line': {'width': 1, 'color': '#333'}},
                        'hoverinfo': 'x+y+name'
                    }
                else:  # line or dual_line
                    trace = {
                        'x': x_labels,
                        'y': y_values,
                        'type': 'scatter',
                        'mode': 'lines+markers',
                        'name': metric_name,
                        'line': {'color': color, 'width': 3},
                        'marker': {'color': color, 'size': 10, 'line': {'width': 1, 'color': '#333'}},
                        'connectgaps': False,
                        'hoverinfo': 'x+y+name',
                        'text': [f"{v:,.2f}" if v is not None else '' for v in y_values],
                        'textposition': 'top center'
                    }
                if axis == 'y2':
                    trace['yaxis'] = 'y2'
                    layout['yaxis2']['title'] = axis_title
                else:
                    layout['yaxis']['title'] = axis_title
                traces.append(trace)
        
        return {'data': traces, 'layout': layout}

    def _is_time_axis(self, labels):
        # Heuristic: if most labels look like dates/months/years
        date_patterns = [r'\b\w+\s+\d{4}\b', r'\b\d{4}-\d{2}\b', r'\b\d{2}/\d{4}\b']
        for pat in date_patterns:
            if sum(bool(re.search(pat, l)) for l in labels) > len(labels)//2:
                return True
        return False

    def _create_complete_timeline_or_categories(self, metrics: list) -> list:
        """Create a complete, sorted timeline or category list from all data points."""
        all_labels = set()
        for metric in metrics:
            for point in metric.get('data_points', []):
                if point.get('label'):
                    all_labels.add(point['label'])
        labels = list(all_labels)
        if self._is_time_axis(labels):
            def sort_key(label):
                try:
                    return datetime.strptime(label, '%B %Y')
                except Exception:
                    try:
                        return datetime.strptime(label, '%Y-%m')
                    except Exception:
                        return (9999, label)
            return sorted(labels, key=sort_key)
        else:
            return sorted(labels)

    def _create_fallback_chart_spec(self, error_message: str) -> dict:
        """Emergency fallback chart"""
        print(f"🚨 Using fallback chart due to error: {error_message}")
        return {
            'data': [],
            'layout': {
                'title': {'text': 'Data Visualization Failed', 'x': 0.5},
                'xaxis': {'title': 'Error'},
                'yaxis': {'title': ''},
                'annotations': [{
                    'text': f'Could not generate chart:<br>{error_message}',
                    'showarrow': False, 'font': {'size': 14, 'color': 'red'}
                }],
                'plot_bgcolor': '#fffbe6',
                'paper_bgcolor': '#fffbe6'
            }
        }

def create_agent():
    """Create the AI visualization agent"""
    agent_instance = VisualizationAgent()
    return ConversableAgent(
        name=agent_instance.name,
        system_message=agent_instance.system_message,
        llm_config=agent_instance.llm_config,
        human_input_mode="NEVER",
        function_map={"create_visualization": agent_instance.create_visualization}
    ) 