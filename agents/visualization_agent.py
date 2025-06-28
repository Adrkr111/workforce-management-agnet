"""
Enterprise-Grade Visualization Agent with Tool-Based Architecture
The agent has access to professional Plotly functions as tools and intelligently selects the appropriate one.
"""

import json
import re
import numpy as np
import plotly.graph_objects as go
import plotly.express as px
from datetime import datetime
from autogen import ConversableAgent
from config import llm_config

# Enterprise-grade color palettes with high contrast for both light and dark modes
ENTERPRISE_COLORS = {
    'primary': ['#1f77b4', '#ff7f0e', '#2ca02c', '#d62728', '#9467bd', '#8c564b', '#e377c2', '#7f7f7f'],
    'professional': ['#2E86AB', '#A23B72', '#F18F01', '#C73E1D', '#592E83', '#118A7E', '#A4243B', '#D81159'],
    'corporate': ['#003f5c', '#2f4b7c', '#665191', '#a05195', '#d45087', '#f95d6a', '#ff7c43', '#ffa600'],
    'high_contrast': ['#1f77b4', '#ff7f0e', '#2ca02c', '#d62728', '#9467bd', '#8c564b', '#e377c2', '#7f7f7f'],
    'business_contrast': ['#2E86AB', '#FF6B35', '#34A853', '#EA4335', '#9C27B0', '#FF9800', '#795548', '#607D8B'],
    # UPDATED: High-contrast colors that work in both light and dark modes
    'banking_professional': ['#0066CC', '#FF6B35', '#00AA44', '#FF4444', '#9966CC', '#FF9933', '#2E8B57', '#E75480']
}

# Professional theme settings with reasonably large dimensions for enterprise banking
ENTERPRISE_THEME = {
    'paper_bgcolor': '#ffffff',
    'plot_bgcolor': '#fafafa',
    'font_family': 'Arial, sans-serif',
    'font_size': 18,  # Increased from 14
    'title_font_size': 28,  # Reasonable professional size (reduced from 36)
    'gridcolor': '#e1e1e1',
    'linewidth': 4,  # Increased from 3
    'marker_size': 12,  # Increased from 10
    # MUCH LARGER chart dimensions for professional banking presentation - DOUBLED FOR TEAMS
    'chart_width': 4800,   # DOUBLED: 2400px → 4800px for Teams display
    'chart_height': 3200,  # DOUBLED: 1600px → 3200px for Teams display  
    'value_font_size': 24,  # Increased from 18
    'axis_font_size': 22,   # Increased from 16
    'tick_font_size': 20,   # Increased from 14
    'legend_font_size': 20, # New for professional legend
    'subtitle_font_size': 18 # Reasonable subtitle size
}

class VisualizationTools:
    """Enterprise-grade Plotly visualization tools"""
    
    @staticmethod
    def create_line_plot(data, title="Line Chart", subtitle="", x_title="X Axis", y_title="Y Axis", 
                        show_markers=True, show_values=True, smooth_lines=False, area_fill=False, **kwargs):
        """Create professional line plot with enterprise styling matching reference image detail level"""
        
        fig = go.Figure()
        
        # ENHANCED HIGH-CONTRAST COLOR PALETTE for both light and dark modes
        professional_colors = [
            '#0066CC',  # Bright Blue - visible in both modes
            '#FF6B35',  # Bright Orange - high contrast
            '#00AA44',  # Bright Green - good visibility
            '#FF4444',  # Bright Red - strong contrast
            '#9966CC',  # Bright Purple - clear in both modes
            '#FF9933',  # Bright Amber - high visibility
            '#2E8B57',  # Sea Green - good contrast
            '#E75480'   # Bright Pink - visible in both modes
        ]
        
        if isinstance(data, dict) and 'series' in data:
            for i, series in enumerate(data['series']):
                x_vals = series.get('x', [])
                y_vals = series.get('y', [])
                name = series.get('name', f'Series {i+1}')
                
                # Professional color selection for multiple series
                line_color = professional_colors[i % len(professional_colors)]
                
                # Enhanced line trace with professional styling
                trace = go.Scatter(
                    x=x_vals,
                    y=y_vals,
                    mode='lines+markers',  # Always show both lines and markers for professional look
                    name=name,
                    line=dict(
                        color=line_color, 
                        width=3,  # Professional line width
                        shape='spline' if smooth_lines else 'linear'
                    ),
                    marker=dict(
                        size=8,  # Visible but not overwhelming markers
                        line=dict(width=2, color='white'),
                        color=line_color,
                        symbol='circle'
                    ),
                    # PROFESSIONAL AREA FILL for primary series (like the reference image)
                    fill='tonexty' if area_fill and i > 0 else 'tozeroy' if area_fill and i == 0 else None,
                    fillcolor=f'rgba({int(line_color[1:3], 16)}, {int(line_color[3:5], 16)}, {int(line_color[5:7], 16)}, 0.2)' if area_fill else None,
                    
                    # VALUE LABELS - Only show for primary series or on hover
                    text=[f"<b style='font-size:16px; color:#000000; font-weight:700;'>{y:,.0f}</b>" if y is not None and show_values and i == 0 else ""
                          for y in y_vals],
                    textposition='top center',
                    textfont=dict(
                        size=16,  # Reasonable size for professional charts
                        color='#000000',
                        family='Arial, sans-serif'
                    ),
                    
                    # ENHANCED hover template matching professional standards
                    hovertemplate=f'<b style="font-size:16px; font-weight:700">{name}</b><br>' + 
                                 f'<span style="font-size:14px">Date: %{{x}}</span><br>' +
                                 f'<span style="font-size:14px">Value: <b style="font-size:16px; font-weight:700">%{{y:,.0f}}</b></span>' +
                                 '<extra></extra>',
                                         hoverlabel=dict(
                         bgcolor="rgba(255,255,255,0.95)",
                         bordercolor=line_color,
                         font=dict(size=14, color="black", family="Arial, sans-serif")
                     ),
                    connectgaps=True  # Connect gaps in data
                )
                print(f"✅ Created professional Line trace for series: {name}")
                print(f"✅ Using color: {line_color} for series: {name}")
                fig.add_trace(trace)
        
        # PROFESSIONAL LAYOUT matching reference image standards
        fig.update_layout(
            # Professional chart dimensions
            width=ENTERPRISE_THEME['chart_width'],   # 2400px wide
            height=ENTERPRISE_THEME['chart_height'], # 1600px tall
            
            # Professional title styling with 📊 icon
            title=dict(
                text=f"<span style='font-size:28px;'>📊</span> <b style='font-size:28px; font-weight:900; color:#2c3e50'>{title}</b>" + 
                     (f"<br><span style='color:#666666; font-size:18px; font-weight:600'>{subtitle}</span>" if subtitle else ""),
                x=0.5,
                y=0.95,
                font=dict(size=28, family='Arial, sans-serif', color='#2c3e50'),
                pad=dict(t=20, b=20)
            ),
            
            # ENHANCED X-AXIS with professional styling
            xaxis=dict(
                title=dict(
                    text=f"<b style='font-size:20px; font-weight:700; color:#2c3e50'>{x_title}</b>", 
                    font=dict(family='Arial, sans-serif', size=20, color='#2c3e50'),
                    standoff=15
                ),
                showgrid=True,
                gridcolor='rgba(128,128,128,0.3)',  # Light professional grid
                gridwidth=1,
                zeroline=True,
                zerolinecolor='rgba(128,128,128,0.6)',
                zerolinewidth=2,
                tickfont=dict(family='Arial, sans-serif', size=16, color='#2c3e50'),
                linecolor='#2c3e50',
                linewidth=2,
                mirror=True,  # Show border on all sides
                showspikes=True,  # Show reference lines on hover
                spikecolor='rgba(128,128,128,0.6)',
                spikesnap='cursor',
                spikemode='across',
                automargin=True
            ),
            
            # ENHANCED Y-AXIS with professional styling  
            yaxis=dict(
                title=dict(
                    text=f"<b style='font-size:20px; font-weight:700; color:#2c3e50'>{y_title}</b>", 
                    font=dict(family='Arial, sans-serif', size=20, color='#2c3e50'),
                    standoff=15
                ),
                showgrid=True,
                gridcolor='rgba(128,128,128,0.3)',  # Light professional grid
                gridwidth=1,
                zeroline=True,
                zerolinecolor='rgba(128,128,128,0.6)',
                zerolinewidth=2,
                tickfont=dict(family='Arial, sans-serif', size=16, color='#2c3e50'),
                linecolor='#2c3e50',
                linewidth=2,
                mirror=True,  # Show border on all sides
                tickformat=',.0f',  # Format numbers with commas
                automargin=True
            ),
            
            # PROFESSIONAL BACKGROUND AND STYLING
            plot_bgcolor='rgba(248,249,250,0.8)',  # Very light professional background
            paper_bgcolor='white',
            font=dict(family='Arial, sans-serif', size=16, color='#2c3e50'),
            
            # ENHANCED LEGEND matching reference image
            legend=dict(
                orientation="v",  # Vertical legend like reference
                yanchor="top",
                y=0.98,
                xanchor="left", 
                x=1.02,  # Position to the right of chart
                font=dict(size=16, family='Arial, sans-serif', color='#2c3e50'),
                bgcolor='rgba(255,255,255,0.9)',
                bordercolor='rgba(128,128,128,0.5)',
                borderwidth=1,
                itemsizing='constant',
                itemwidth=30,
                traceorder='normal'
            ),
            
            # Professional margins for proper spacing
            margin=dict(l=100, r=150, t=120, b=80),  # More space for legend
            
            # PROFESSIONAL HOVER AND INTERACTION
            hovermode='x unified',  # Unified hover like reference
            hoverdistance=100,
            
            # Show legend for multiple series
            showlegend=True if len(data.get('series', [])) > 1 else False,
            
            # Professional styling
            dragmode='zoom',  # Enable professional zoom
            selectdirection='d'  # 'd' for diagonal selection (not 'diagonal')
        )
        
        # FORCE ENHANCED GRIDLINES (matching reference image detail)
        fig.update_xaxes(
            showgrid=True,
            gridcolor='rgba(128,128,128,0.3)',
            gridwidth=1,
            minor=dict(
                showgrid=True,
                gridcolor='rgba(128,128,128,0.15)',
                gridwidth=0.5
            )
        )
        fig.update_yaxes(
            showgrid=True,
            gridcolor='rgba(128,128,128,0.3)',
            gridwidth=1,
            minor=dict(
                showgrid=True,
                gridcolor='rgba(128,128,128,0.15)',
                gridwidth=0.5
            )
        )
        
        print(f"🎯 Created professional line chart with {len(data.get('series', []))} series")
        return fig.to_dict()

    @staticmethod
    def create_bar_plot(data, title="Bar Chart", subtitle="", x_title="Categories", y_title="Values", 
                       orientation="vertical", show_values=True, group_mode="group", **kwargs):
        """Create professional bar plot with enterprise banking styling and maximum readability"""
        
        fig = go.Figure()
        colors = ENTERPRISE_COLORS['banking_professional']  # Use professional banking colors
        
        if isinstance(data, dict) and 'series' in data:
            for i, series in enumerate(data['series']):
                x_vals = series.get('x', [])
                y_vals = series.get('y', [])
                name = series.get('name', f'Series {i+1}')
                
                if orientation == "horizontal":
                    x_vals, y_vals = y_vals, x_vals
                
                # Professional banking color selection with stronger contrast
                bar_color = colors[i % len(colors)]
                
                # Calculate value position and styling - Handle None values safely
                values_to_show = x_vals if orientation == "horizontal" else y_vals
                max_value = max([v for v in values_to_show if v is not None]) if values_to_show and any(v is not None for v in values_to_show) else 0
                
                trace = go.Bar(
                    x=x_vals,
                    y=y_vals,
                    name=name,
                    width=0.7,  # Slightly wider bars for better presence
                    marker=dict(
                        color=bar_color,
                        line=dict(color='white', width=4),  # Thicker white border for definition
                        opacity=0.9,  # Higher opacity for more solid appearance
                        # Professional pattern
                        pattern=dict(shape="", fillmode="replace")
                    ),
                    # HIGH-CONTRAST text styling for both light and dark mode visibility
                    text=[f"<b style='font-size:28px; color:#FFFFFF; font-weight:900; text-shadow: 2px 2px 4px rgba(0,0,0,0.8), -1px -1px 2px rgba(0,0,0,0.8);'>{v:,.0f}</b>" if v is not None else "<b style='font-size:28px; color:#CCCCCC; font-weight:900;'>N/A</b>"
                          for v in values_to_show] if show_values else None,
                    textposition='outside' if orientation == "vertical" else 'auto',
                    textfont=dict(
                        size=ENTERPRISE_THEME['value_font_size'],  # 24px for enterprise readability
                        color='#FFFFFF',  # White text with black shadow for maximum visibility in both modes
                        family='Arial Black, Helvetica, sans-serif'  # Bold font family for authority
                    ),
                    # Professional text template
                    texttemplate='%{text}',
                    cliponaxis=False,  # Don't clip text that goes outside plot area
                    # ENHANCED hover template with banking-grade readability
                    hovertemplate=f'<b style="font-size:20px; font-weight:700">{name}</b><br>' + 
                                 f'<span style="font-size:18px">%{{x}}: <b style="font-size:20px; font-weight:700">%{{y:,.0f}}</b></span>' +
                                 '<extra></extra>',
                    hoverlabel=dict(
                        bgcolor="white",
                        bordercolor=bar_color,
                        font=dict(size=18, color="black", family="Arial, sans-serif")
                    )
                )
                print(f"✅ Created Bar trace with type: {trace.type}")
                print(f"✅ Bar trace data - X: {x_vals[:3]}..., Y: {y_vals[:3]}...")
                print(f"✅ Using color: {bar_color} for series: {name}")
                fig.add_trace(trace)
        
        # ENTERPRISE BANKING LAYOUT with maximum professional appearance
        fig.update_layout(
            # ENTERPRISE CHART DIMENSIONS for boardroom presentation
            width=ENTERPRISE_THEME['chart_width'],   # 2400px wide for maximum visibility
            height=ENTERPRISE_THEME['chart_height'], # 1600px tall for authority
            # High-contrast title styling for both light and dark modes
            title=dict(
                text=f"<b style='font-size:40px; font-weight:900; color:#0066CC'>{title}</b><br><span style='color:#666666; font-size:24px; font-weight:600'>{subtitle}</span>" if subtitle else f"<b style='font-size:40px; font-weight:900; color:#0066CC'>{title}</b>",
                x=0.5,
                font=dict(size=ENTERPRISE_THEME['title_font_size'], family='Arial Black, Arial, sans-serif', color='#0066CC'),  # Bright blue for visibility
                pad=dict(t=40, b=40)  # More professional padding
            ),
            xaxis=dict(
                title=dict(
                    text=f"<b style='font-size:24px; font-weight:700; color:#0066CC'>{x_title}</b>", 
                    font=dict(family='Arial Black, sans-serif', size=ENTERPRISE_THEME['axis_font_size'], color='#0066CC')
                ),
                showgrid=True,  # Enable grid lines for x-axis
                gridcolor='#d0d0d0',  # More visible professional gray
                gridwidth=2,  # Thicker for better visibility
                tickfont=dict(family='Arial, sans-serif', size=ENTERPRISE_THEME['tick_font_size'], color='#0066CC', weight='bold'),  # 20px bold tick labels
                linecolor='#0066CC',
                linewidth=4,  # Thicker axis lines for authority
                tickangle=-45,  # Always rotate labels for better readability
                ticklen=12,  # Longer tick marks for professionalism
                tickwidth=3,
                # FORCE ALL LABELS TO SHOW with better spacing
                tickmode='array',  # Use array mode to explicitly control which ticks to show
                tickvals=list(range(len(data.get('series', [{}])[0].get('x', [])))) if data.get('series') else [],  # Show ALL positions
                ticktext=data.get('series', [{}])[0].get('x', []) if data.get('series') else [],  # Show ALL labels
                # Professional spacing and visibility
                range=[-0.7, len(data.get('series', [{}])[0].get('x', [])) - 0.3] if data.get('series') else None,
                # Better tick formatting
                tickformat='',  # Don't format dates automatically
                automargin=True,  # Automatically adjust margins for rotated labels
                # Professional positioning
                side='bottom'
            ),
            yaxis=dict(
                title=dict(
                    text=f"<b style='font-size:24px; font-weight:700; color:#0066CC'>{y_title}</b>", 
                    font=dict(family='Arial Black, sans-serif', size=ENTERPRISE_THEME['axis_font_size'], color='#0066CC')
                ),
                showgrid=True,
                gridcolor='#c0c0c0',  # More professional visible grid
                gridwidth=2,  # Medium thickness grid lines for authority
                tickfont=dict(family='Arial, sans-serif', size=ENTERPRISE_THEME['tick_font_size'], color='#0066CC', weight='bold'),  # 20px bold tick labels
                linecolor='#0066CC',
                linewidth=4,  # Thicker axis lines
                zeroline=True,
                zerolinecolor='#666',  # Professional zero line
                zerolinewidth=4,  # Thicker zero line for prominence
                ticklen=12,  # Longer tick marks to match x-axis
                tickwidth=3,
                # Professional tick spacing
                tickmode='linear',
                dtick=1000,  # Show major ticks every 1000 units for banking clarity
                minor=dict(
                    showgrid=True,
                    gridcolor='#e5e5e5',  # Lighter minor grid lines
                    gridwidth=1,
                    dtick=500  # Minor gridlines every 500 units
                ),
                # Add extra space at top for value labels - Handle None values safely
                range=[0, max([max([v for v in series.get('y', [0]) if v is not None] or [0]) for series in data.get('series', [])]) * 1.25] if data.get('series') else None,  # More space for professional labels
                # Format y-axis numbers with commas for banking standard
                tickformat=',.0f',
                automargin=True
            ),
            plot_bgcolor='#f8f9fa',  # Very light professional background
            paper_bgcolor='#ffffff',  # Pure white outer background for formality
            font=dict(family='Arial, sans-serif', size=ENTERPRISE_THEME['font_size'], color='#0066CC'),
            barmode=group_mode,
            bargap=0.15,  # Tighter spacing for professional look
            bargroupgap=0.08,  # Minimal gap between bars in group
            margin=dict(l=150, r=150, t=220, b=220),  # Generous margins for professional presentation
            # ENHANCED legend styling with enterprise appearance
            legend=dict(
                orientation="h",
                yanchor="bottom",
                y=1.08,
                xanchor="center", 
                x=0.5,
                font=dict(size=ENTERPRISE_THEME['legend_font_size'], family='Arial Black, sans-serif', color='#0066CC', weight='bold'),  # 20px bold legend
                bgcolor='rgba(255,255,255,0.98)',
                bordercolor='#0066CC',
                borderwidth=3,
                itemsizing='constant',
                itemwidth=40  # Wider legend items for readability
            ),
            # Professional hover mode
            hovermode='x unified',
            hoverdistance=60,
            # Enterprise styling
            showlegend=True if len(data.get('series', [])) > 1 else False
        )
        
        # FORCE PROFESSIONAL GRIDLINES - Override any template interference
        fig.update_xaxes(
            showgrid=True,
            gridcolor='#d0d0d0',
            gridwidth=2
        )
        fig.update_yaxes(
            showgrid=True,
            gridcolor='#c0c0c0',
            gridwidth=2,
            minor_showgrid=True,
            minor_gridcolor='#e5e5e5',
            minor_gridwidth=1
        )
        
        chart_dict = fig.to_dict()
        
        # FORCE BAR CHART - Explicitly verify trace types
        for i, trace in enumerate(chart_dict.get('data', [])):
            if trace.get('type') != 'bar':
                print(f"🚨 WARNING: Trace {i} type is {trace.get('type')}, forcing to 'bar'")
                trace['type'] = 'bar'
            else:
                print(f"✅ Confirmed trace {i} is type 'bar'")
        
        # FORCE PROFESSIONAL GRIDLINES IN FINAL DICT - Triple enforcement
        if 'layout' in chart_dict and 'xaxis' in chart_dict['layout']:
            chart_dict['layout']['xaxis']['showgrid'] = True
            chart_dict['layout']['xaxis']['gridcolor'] = '#d0d0d0'
            chart_dict['layout']['xaxis']['gridwidth'] = 2
            print("🔧 FORCED X-axis professional gridlines ON")
        
        if 'layout' in chart_dict and 'yaxis' in chart_dict['layout']:
            chart_dict['layout']['yaxis']['showgrid'] = True
            chart_dict['layout']['yaxis']['gridcolor'] = '#c0c0c0'
            chart_dict['layout']['yaxis']['gridwidth'] = 2
            if 'minor' not in chart_dict['layout']['yaxis']:
                chart_dict['layout']['yaxis']['minor'] = {}
            chart_dict['layout']['yaxis']['minor']['showgrid'] = True
            chart_dict['layout']['yaxis']['minor']['gridcolor'] = '#e5e5e5'
            chart_dict['layout']['yaxis']['minor']['gridwidth'] = 1
            chart_dict['layout']['yaxis']['minor']['dtick'] = 500
            print("🔧 FORCED Y-axis professional gridlines ON with minor gridlines")
        
        print(f"🎯 Final chart data types: {[trace.get('type') for trace in chart_dict.get('data', [])]}")
        return chart_dict

class EnterpriseVisualizationAgent:
    def __init__(self):
        self.name = "Data-Visualization-Agent"
        self.tools = VisualizationTools()
        self.system_message = """You are an Enterprise-Grade Data Visualization Agent with access to professional Plotly tools.

**Available Tools:**
- create_line_plot: Professional line charts with markers, value labels, area fill
- create_bar_plot: Enterprise bar charts with value labels, grouping options

**Your Process:**
1. Analyze the user's data and visualization request
2. Select the most appropriate tool based on:
   - Data characteristics (time series, categorical, numerical)
   - User's explicit request (bar plot, line chart, etc.)
   - Best practices for the data type
3. Call the selected tool with appropriate parameters
4. Always use professional styling and enterprise-grade features

**Tool Selection Guidelines:**
- Bar plots: For categorical comparisons, rankings, discrete values
- Line plots: For time series, trends, continuous data over time

Always honor the user's explicit chart type requests while ensuring enterprise-grade quality."""

        self.llm_config = llm_config

    def create_visualization(self, data_str: str):
        """Main visualization function that analyzes data and calls appropriate tool"""
        print(f"🎯 Enterprise visualization for: {data_str[:150]}...")
        
        try:
            # Parse and analyze the data
            analysis = self._analyze_data_and_intent(data_str)
            
            if not analysis.get('success'):
                return str({'spec': self._create_error_chart("Failed to analyze data")})
            
            # Prepare data in standard format
            formatted_data = self._format_data_for_tools(analysis)
            
            # Select and call appropriate tool
            chart_spec = self._call_visualization_tool(analysis, formatted_data, data_str)
            
            return str({'spec': chart_spec})
            
        except Exception as e:
            print(f"❌ Visualization error: {e}")
            return str({'spec': self._create_error_chart(str(e))})

    def _analyze_data_and_intent(self, text: str) -> dict:
        """Analyze data and user intent using AI"""
        prompt = f"""
Analyze this visualization request and return a JSON response:

{text}

CRITICAL REQUIREMENTS:
1. Pay close attention to explicit chart type requests!
2. SCAN FOR MULTIPLE DATASETS - Look for phrases like "both datasets", "Dataset 1", "Dataset 2", multiple data tables, etc.
3. EXTRACT ALL DATA SERIES - If there are multiple datasets mentioned, extract ALL of them as separate series
4. EXTRACT BUSINESS CONTEXT - Look for JSON structure with business metadata

Chart Type Detection Rules:
- If text contains "bar plot", "bar chart", "bar graph" → chart_type: "bar"
- If text contains "line plot", "line chart", "line graph" → chart_type: "line"  
- If text contains "pie chart", "pie plot" → chart_type: "pie"
- If text contains "scatter plot", "scatter chart" → chart_type: "scatter"
- If user explicitly asks for a specific chart type, ALWAYS honor that request

Multiple Dataset Detection:
- Look for "both datasets", "Dataset 1", "Dataset 2", "first dataset", "second dataset"
- Look for multiple data tables or lists
- Look for different business units, substreams, or categories
- Extract each dataset as a separate series with appropriate names

Business Context Extraction Rules:
- Look for JSON structure like: {{"data_type": "forecast", "business": "logistics", "substream": "dlt", "team": "support"}}
- Extract "business", "substream", "team" fields from JSON if present
- Also look for plain text mentions: "Business:", "Substream:", "Team:"
- If JSON structure exists, prioritize it over plain text

Data Extraction Rules:
- Parse ALL dates/categories as x-axis values
- Parse ALL numerical values as y-axis values (extract numbers but preserve units for axis labeling)
- Handle missing data: Convert "Data Not Available", "N/A", "Missing" to null/None values
- Convert dates to consistent format (e.g., "Jun 2025", "Jul 2025")
- For missing months, include the month in x-axis but use null for y-value
- Use descriptive names from the text for series names
- Extract units from data (e.g., "cases", "employees", "%") and include in y_title

Title Generation Rules:
- PRIORITY: Extract business context from JSON structure or plain text
- Include FULL business hierarchy in title: "[Business] - [Substream] - [Team] [Data Type]" 
- Example: "Logistics - DLT - Support Team Forecast" instead of just "Logistics Forecast"
- If forecast data, use format: "[Business] - [Substream] - [Team] Team Forecast"
- If KPI data, use format: "[Business] - [Substream] - [Team] [KPI Name]"
- Always use complete names, not abbreviated forms
- If no business context found, use descriptive title based on data content

Return JSON format:
{{
    "success": true,
    "chart_type": "bar|line|pie|scatter|dual_axis",
    "title": "Complete Business Context Title (e.g., 'Logistics - DLT - Support Team Forecast')",
    "subtitle": "Optional subtitle with time period",
    "x_title": "X Axis Label",
    "y_title": "Y Axis Label (include units like 'Number of Cases' if data has units)",
    "business_context": {{
        "business": "extracted business unit",
        "substream": "extracted substream",
        "team": "extracted team"
    }},
    "series": [
        {{
            "name": "Logistics DLT Support Forecast",
            "x": ["Jun 2025", "Jul 2025", "Aug 2025"],
            "y": [2845, 2843, 2519],
            "axis": "y1"
        }}
    ],
    "options": {{
        "show_values": true,
        "show_trendline": false,
        "orientation": "vertical|horizontal"
    }}
}}

CRITICAL: If you find JSON data with business context like {{"business": "logistics", "substream": "dlt", "team": "support"}}, 
extract this and build the title as "Logistics - DLT - Support Team [Data Type]"

IMPORTANT: If you see multiple datasets, you MUST extract ALL of them as separate series in the "series" array!
"""
        
        try:
            analysis_agent = ConversableAgent(
                name="analysis_agent",
                system_message="You analyze data requests and return only valid JSON.",
                llm_config=self.llm_config,
                human_input_mode="NEVER"
            )
            
            response = analysis_agent.generate_reply(
                messages=[{"role": "user", "content": prompt}]
            )
            
            response_text = response if isinstance(response, str) else response.get('content', '')
            json_match = re.search(r'\{.*\}', response_text, re.DOTALL)
            
            if json_match:
                return json.loads(json_match.group(0))
            else:
                return {"success": False}
                
        except Exception as e:
            print(f"❌ Analysis error: {e}")
            return {"success": False}

    def _format_data_for_tools(self, analysis: dict) -> dict:
        """Format analysis data for visualization tools"""
        return {
            'series': analysis.get('series', [])
        }

    def _call_visualization_tool(self, analysis: dict, data: dict, original_request: str) -> dict:
        """Call the appropriate visualization tool based on analysis"""
        chart_type = analysis.get('chart_type', 'line')
        options = analysis.get('options', {})
        
        # ENHANCED keyword detection for bar charts - check multiple variations
        bar_keywords = ['bar plot', 'bar chart', 'bar graph', 'as a bar', 'in bar format', 'as bars']
        line_keywords = ['line plot', 'line chart', 'line graph', 'trend line', 'time series']
        
        request_lower = original_request.lower()
        
        # Priority detection: explicit bar chart requests
        if any(keyword in request_lower for keyword in bar_keywords):
            chart_type = 'bar'
            print(f"🔍 BAR CHART DETECTED: Found bar request in '{original_request[:100]}...'")
        # Only override with line if explicitly requested AND no bar keywords found
        elif any(keyword in request_lower for keyword in line_keywords) and not any(keyword in request_lower for keyword in bar_keywords):
            chart_type = 'line'
            print(f"🔍 LINE CHART DETECTED: Found line request")
        # If AI analysis detected bar but we missed it in keywords, trust the AI
        elif analysis.get('chart_type') == 'bar':
            chart_type = 'bar'
            print(f"🔍 AI ANALYSIS DETECTED: Bar chart from analysis")
        
        # BUILD COMPLETE BUSINESS CONTEXT TITLE
        title = analysis.get('title', 'Visualization')
        business_context = analysis.get('business_context', {})
        
        # If we have business context, build the complete title
        if business_context and business_context.get('business') and business_context.get('substream') and business_context.get('team'):
            business = business_context['business'].title()
            substream = business_context['substream'].upper()
            team = business_context['team'].title()
            
            # Determine data type from chart context
            if 'forecast' in original_request.lower():
                data_type = "Team Forecast"
            elif 'kpi' in original_request.lower():
                data_type = "KPI Analysis"
            else:
                data_type = "Analysis"
            
            title = f"{business} - {substream} - {team} {data_type}"
            print(f"🏷️ ENHANCED TITLE: {title}")
        else:
            print(f"⚠️ No business context found, using AI title: {title}")
        
        common_params = {
            'data': data,
            'title': title,
            'subtitle': analysis.get('subtitle', ''),
            'x_title': analysis.get('x_title', 'X Axis'),
            'y_title': analysis.get('y_title', 'Y Axis')
        }
        
        print(f"📊 FINAL DECISION: Creating {chart_type.upper()} chart with enterprise styling")
        
        if chart_type == 'bar':
            return self.tools.create_bar_plot(
                **common_params,
                orientation=options.get('orientation', 'vertical'),
                show_values=options.get('show_values', True)
            )
        else:  # Default to line
            return self.tools.create_line_plot(
                **common_params,
                show_values=options.get('show_values', True),
                area_fill=options.get('area_fill', False)
            )

    def _create_error_chart(self, error_msg: str) -> dict:
        """Create error visualization"""
        return {
            'data': [],
            'layout': {
                'title': 'Visualization Error',
                'annotations': [{
                    'text': f'Error: {error_msg}',
                    'showarrow': False,
                    'font': {'size': 16, 'color': 'red'}
                }]
            }
        }

def create_agent():
    """Create the enterprise visualization agent"""
    agent_instance = EnterpriseVisualizationAgent()
    return ConversableAgent(
        name=agent_instance.name,
        system_message=agent_instance.system_message,
        llm_config=agent_instance.llm_config,
        human_input_mode="NEVER",
        function_map={"create_visualization": agent_instance.create_visualization}
    ) 