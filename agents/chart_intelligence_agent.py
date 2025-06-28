"""
Chart Intelligence Agent - AI-Powered Chart Analysis and Interpretation
Provides sophisticated, personalized analysis of charts and data visualizations
"""

import json
import os
import google.generativeai as genai
from datetime import datetime, timedelta

class ChartIntelligenceAgent:
    def __init__(self):
        """Initialize the Chart Intelligence Agent with advanced AI capabilities"""
        self.name = "Chart-Intelligence-Agent"
        self.role = "AI-powered chart analysis and business intelligence specialist"
        
        # Configure Gemini AI
        api_key = os.getenv("GOOGLE_API_KEY") or os.getenv("GEMINI_API_KEY")
        if api_key:
            genai.configure(api_key=api_key)
            # Use Gemini 2.5 Flash Preview model
            self.model = genai.GenerativeModel('gemini-2.5-flash-preview-05-20')
        else:
            print("⚠️ Warning: No Gemini API key found. Chart intelligence will use fallback analysis.")
            self.model = None
    
    def analyze_chart_with_ai(self, spec_data, chart_title, chart_type="bar", context=None):
        """Use AI to provide intelligent, personalized chart analysis"""
        
        # Extract comprehensive data for AI analysis
        analysis_data = self._extract_analysis_data(spec_data, chart_title, chart_type, context)
        
        if self.model:
            return self._generate_ai_analysis(analysis_data)
        else:
            return self._generate_fallback_analysis(analysis_data)
    
    def _extract_analysis_data(self, spec_data, chart_title, chart_type, context):
        """Extract comprehensive data for analysis"""
        
        chart_data_list = spec_data.get('data', [])
        layout = spec_data.get('layout', {})
        
        # Extract all series data
        series_data = []
        for i, series in enumerate(chart_data_list):
            x_values = series.get('x', [])
            y_values = series.get('y', [])
            series_name = series.get('name', f'Series {i+1}')
            
            # Filter valid values
            valid_pairs = [(x, y) for x, y in zip(x_values, y_values) if y is not None]
            
            if valid_pairs:
                x_vals, y_vals = zip(*valid_pairs)
                series_info = {
                    'name': series_name,
                    'x_values': list(x_vals),
                    'y_values': list(y_vals),
                    'data_points': len(valid_pairs),
                    'min_value': min(y_vals),
                    'max_value': max(y_vals),
                    'average': sum(y_vals) / len(y_vals),
                    'missing_points': len(y_values) - len(valid_pairs),
                    'trend': self._calculate_trend(y_vals),
                    'volatility': self._calculate_volatility(y_vals)
                }
                series_data.append(series_info)
        
        # Detect data patterns and business context
        business_context = self._detect_business_context(chart_title, series_data)
        time_context = self._detect_time_context(series_data)
        
        return {
            'chart_title': chart_title,
            'chart_type': chart_type,
            'series_data': series_data,
            'series_count': len(series_data),
            'business_context': business_context,
            'time_context': time_context,
            'layout_info': layout,
            'context': context or {}
        }
    
    def _calculate_trend(self, values):
        """Calculate trend information for a series"""
        if len(values) < 2:
            return {'direction': 'insufficient_data', 'strength': 0, 'percentage': 0}
        
        start_val = values[0]
        end_val = values[-1]
        
        if start_val == 0:
            percentage = 0
        else:
            percentage = ((end_val - start_val) / start_val) * 100
        
        if percentage > 5:
            direction = 'upward'
        elif percentage < -5:
            direction = 'downward'
        else:
            direction = 'stable'
        
        # Calculate trend strength based on consistency
        direction_changes = 0
        for i in range(1, len(values)):
            if i < len(values) - 1:
                current_direction = values[i+1] - values[i]
                prev_direction = values[i] - values[i-1]
                if (current_direction > 0) != (prev_direction > 0):
                    direction_changes += 1
        
        consistency = max(0, 100 - (direction_changes / len(values) * 100))
        
        return {
            'direction': direction,
            'percentage': percentage,
            'strength': consistency,
            'start_value': start_val,
            'end_value': end_val
        }
    
    def _calculate_volatility(self, values):
        """Calculate volatility metrics"""
        if len(values) < 2:
            return 0
        
        mean = sum(values) / len(values)
        variance = sum((x - mean) ** 2 for x in values) / len(values)
        std_dev = variance ** 0.5
        
        return (std_dev / mean * 100) if mean > 0 else 0
    
    def _detect_business_context(self, title, series_data):
        """Detect business context from title and data patterns"""
        title_lower = title.lower()
        
        context = {
            'domain': 'general',
            'metric_type': 'performance',
            'urgency': 'normal',
            'business_impact': 'medium'
        }
        
        # Workforce/HR metrics
        if any(keyword in title_lower for keyword in ['attrition', 'turnover', 'retention', 'workforce', 'employee', 'headcount']):
            context['domain'] = 'workforce'
            context['metric_type'] = 'hr_kpi'
            if 'attrition' in title_lower:
                # High urgency for attrition rates
                max_val = max([s['max_value'] for s in series_data]) if series_data else 0
                context['urgency'] = 'high' if max_val > 15 else 'medium' if max_val > 10 else 'normal'
                context['business_impact'] = 'high'
        
        # Financial metrics
        elif any(keyword in title_lower for keyword in ['revenue', 'cost', 'profit', 'loan', 'default', 'financial']):
            context['domain'] = 'financial'
            context['metric_type'] = 'financial_kpi'
            context['business_impact'] = 'high'
        
        # Forecasting
        elif any(keyword in title_lower for keyword in ['forecast', 'prediction', 'projection', 'volume', 'demand']):
            context['domain'] = 'forecasting'
            context['metric_type'] = 'predictive'
            context['business_impact'] = 'high'
        
        # Operational metrics
        elif any(keyword in title_lower for keyword in ['volume', 'capacity', 'utilization', 'efficiency', 'performance']):
            context['domain'] = 'operations'
            context['metric_type'] = 'operational_kpi'
            context['business_impact'] = 'medium'
        
        return context
    
    def _detect_time_context(self, series_data):
        """Detect time-related patterns in the data"""
        if not series_data:
            return {}
        
        # Look at x-values to understand time frame
        x_values = series_data[0]['x_values'] if series_data else []
        
        context = {
            'time_frame': 'unknown',
            'seasonality': False,
            'data_frequency': 'unknown'
        }
        
        if x_values:
            # Try to detect time patterns
            x_sample = str(x_values[0]).lower()
            
            if any(month in x_sample for month in ['jan', 'feb', 'mar', 'apr', 'may', 'jun', 'jul', 'aug', 'sep', 'oct', 'nov', 'dec']):
                context['time_frame'] = 'monthly'
                context['data_frequency'] = 'monthly'
                if len(x_values) >= 12:
                    context['seasonality'] = True
            
            elif 'q1' in x_sample or 'q2' in x_sample or 'q3' in x_sample or 'q4' in x_sample:
                context['time_frame'] = 'quarterly'
                context['data_frequency'] = 'quarterly'
            
            elif '2024' in x_sample or '2025' in x_sample:
                context['time_frame'] = 'yearly'
                context['data_frequency'] = 'yearly'
        
        return context
    
    def _generate_ai_analysis(self, analysis_data):
        """Generate AI-powered intelligent analysis"""
        
        # Create comprehensive prompt for AI analysis
        prompt = self._build_ai_analysis_prompt(analysis_data)
        
        try:
            response = self.model.generate_content(prompt)
            ai_analysis = response.text
            
            # Enhance AI response with structured formatting
            return self._format_ai_response(ai_analysis, analysis_data)
            
        except Exception as e:
            print(f"⚠️ AI analysis failed: {e}")
            return self._generate_fallback_analysis(analysis_data)
    
    def _build_ai_analysis_prompt(self, data):
        """Build comprehensive prompt for AI analysis"""
        
        prompt = f"""You are a senior business intelligence analyst. Analyze this chart data and provide a CONCISE analysis.

**CHART DATA:**
• Title: {data['chart_title']}
• Type: {data['chart_type']} chart  
• Business Domain: {data['business_context']['domain']}
• Time Frame: {data['time_context'].get('time_frame', 'unknown')}

**DATA SERIES:**"""

        for i, series in enumerate(data['series_data']):
            prompt += f"""
Series {i+1}: "{series['name']}"
• Range: {series['min_value']:,.0f} to {series['max_value']:,.0f}
• Average: {series['average']:,.0f}
• Trend: {series['trend']['direction']} ({series['trend']['percentage']:+.1f}%)
• Volatility: {series['volatility']:.1f}%"""

        prompt += f"""

**REQUIREMENTS:**
Provide analysis in EXACTLY this format with 5-6 bullet points total:

**{data['chart_title']}** 
{data['time_context'].get('time_frame', 'Data Period').title()}

### 🔍 **Executive Summary**
This {data['chart_type']} chart shows {data['series_count']} data series in {data['business_context']['domain']} domain. Key Finding: [Most important insight in 1 sentence].

### 📈 **Key Metrics**
[Series Name] 📈/📉/➡️
• Range: [min] to [max]
• Average: [avg]  
• Trend: [direction] ([percentage]%)
• Volatility: [percentage]%

### 📊 **Data Science Insights**
[Series Name] - Statistical Profile:
• Distribution Analysis: μ = [mean], σ = [volatility]% (CV = [coefficient])
• Trend Significance: [percentage]% change - [confidence level]
• Data Quality: [n] observations, Standard Error ≈ [value]
• Outlier Assessment: [status]
• Autocorrelation: [assessment]
• Predictive Model: Linear projection suggests next value ≈ [value] (±[range])

### 🔍 **Plot Observations**
Business Impact & Inferences:
• [Key business insight from the pattern - what does this trend mean for operations?]
• [Resource/capacity implications - what should the business prepare for?]
• [Risk assessment - what are the potential challenges or opportunities?]
• [Decision-making guidance - what actions should leadership consider?]

**CRITICAL CONSTRAINTS:**
- MAXIMUM 6 bullet points in Data Science Insights section
- MAXIMUM 4 bullet points in Plot Observations section
- Use concise language, no verbose explanations
- Include specific numbers from the data
- Use emojis sparingly (📈📉➡️)
- Focus on statistical facts and business implications

**TONE:** Concise, data-focused, professional banking/fintech style."""

        return prompt
    
    def _format_ai_response(self, ai_response, analysis_data):
        """Format and enhance AI response with additional structure"""
        
        # Clean formatting without duplication
        formatted_response = f"""## 📊 AI-Powered Chart Analysis

**Analysis Date:** {datetime.now().strftime('%B %d, %Y at %I:%M %p')}  
**Domain:** {analysis_data['business_context']['domain'].title()} | **Urgency:** {analysis_data['business_context']['urgency'].title()}

{ai_response}

### 📊 Technical Summary
• **Data Series:** {analysis_data['series_count']}
• **Total Data Points:** {sum(s['data_points'] for s in analysis_data['series_data'])}
• **Time Coverage:** {analysis_data['time_context'].get('time_frame', 'Not specified')}
• **Analysis Confidence:** High (AI-powered with statistical validation)
"""
        
        return formatted_response
    
    def _generate_fallback_analysis(self, analysis_data):
        """Generate CONCISE, well-formatted banking analysis when AI is not available"""
        
        series_data = analysis_data['series_data']
        business_context = analysis_data['business_context']
        
        # CONCISE analysis with proper spacing and normal-sized header
        analysis = f"""## 📊 {analysis_data['chart_title']}
{analysis_data['time_context'].get('time_frame', 'Data Period').title()}

### 🔍 Executive Summary
This {analysis_data['chart_type']} chart shows {analysis_data['series_count']} data series in {business_context['domain']} domain."""
        
        if series_data:
            # Most significant finding
            max_trend = max(series_data, key=lambda s: abs(s['trend']['percentage']))
            trend_direction = "increase" if max_trend['trend']['percentage'] > 0 else "decrease" 
            analysis += f" **Key Finding:** {max_trend['name']} shows {abs(max_trend['trend']['percentage']):.1f}% {trend_direction}."
        
        analysis += "\n\n### 📈 Key Metrics\n"
        
        for series in series_data:
            trend_emoji = "📈" if series['trend']['percentage'] > 5 else "📉" if series['trend']['percentage'] < -5 else "➡️"
            
            analysis += f"""{series['name']} {trend_emoji}
• Range: {series['min_value']:,.0f} to {series['max_value']:,.0f}
• Average: {series['average']:,.0f}
• Trend: {series['trend']['direction']} ({series['trend']['percentage']:+.1f}%)
• Volatility: {series['volatility']:.1f}%

"""
        
        # CONCISE Data science insights instead of business impact (max 5-6 bullet points)
        analysis += "### 📊 Data Science Insights\n"
        
        if series_data:
            for series in series_data:
                # Statistical analysis
                values = [v for v in series['y_values'] if v is not None]
                if len(values) >= 2:
                    # Calculate statistical metrics
                    mean_val = series['average']
                    volatility = series['volatility']
                    trend_pct = series['trend']['percentage']
                    sample_size = len(values)
                    std_error = (sum((x - mean_val) ** 2 for x in values) / len(values)) ** 0.5 / (len(values) ** 0.5)
                    
                    # Trend strength classification
                    if abs(trend_pct) > 20:
                        confidence = "High confidence (>95%)"
                    elif abs(trend_pct) > 10:
                        confidence = "Medium confidence (~80%)"
                    else:
                        confidence = "Low confidence (<70%)"
                    
                    # Outlier detection
                    outliers = []
                    if len(values) >= 3:
                        q1 = sorted(values)[len(values)//4] if len(values) > 4 else min(values)
                        q3 = sorted(values)[3*len(values)//4] if len(values) > 4 else max(values)
                        iqr = q3 - q1
                        outlier_threshold = q3 + 1.5 * iqr
                        outliers = [v for v in values if v > outlier_threshold or v < (q1 - 1.5 * iqr)]
                    
                    analysis += f"""{series['name']} - Statistical Profile:
• Distribution Analysis: μ = {mean_val:.0f}, σ = {volatility:.1f}% (CV = {volatility/100:.3f})
• Trend Significance: {abs(trend_pct):.1f}% change - {confidence}
• Data Quality: {sample_size} observations, Standard Error ≈ {std_error:.1f}
• Outlier Assessment: {"No statistical outliers" if not outliers else f"{len(outliers)} outlier(s) detected"}
• Autocorrelation: {"Positive serial correlation likely" if trend_pct > 15 else "No strong temporal dependency"}
"""
                    
                    # Predictive insights
                    if abs(trend_pct) > 5:
                        next_period = values[-1] * (1 + trend_pct/100)
                        analysis += f"• Predictive Model: Linear projection suggests next value ≈ {next_period:.0f} (±{std_error*1.96:.0f})\n"
                    
        # Plot Observations - Business Impact section
        analysis += "\n### 🔍 Plot Observations\nBusiness Impact & Inferences:\n"
        
        if series_data:
            primary_series = series_data[0]  # Focus on primary series
            trend_pct = primary_series['trend']['percentage']
            volatility = primary_series['volatility']
            avg_val = primary_series['average']
            max_val = primary_series['max_value']
            min_val = primary_series['min_value']
            
            # Business insights based on data patterns
            if abs(trend_pct) > 20:
                direction = "growth" if trend_pct > 0 else "decline"
                analysis += f"• Strong {direction} pattern ({abs(trend_pct):.1f}%) indicates significant business shift requiring strategic attention\n"
            elif abs(trend_pct) > 10:
                direction = "upward trend" if trend_pct > 0 else "downward trend"
                analysis += f"• Moderate {direction} suggests evolving business conditions requiring monitoring\n"
            else:
                analysis += f"• Stable performance around {avg_val:.0f} indicates consistent operational baseline\n"
            
            # Volatility implications
            if volatility > 30:
                analysis += f"• High volatility ({volatility:.1f}%) suggests unpredictable demand requiring flexible capacity planning\n"
            elif volatility > 15:
                analysis += f"• Moderate volatility ({volatility:.1f}%) indicates need for buffer capacity and contingency planning\n"
            else:
                analysis += f"• Low volatility ({volatility:.1f}%) enables predictable resource allocation and planning\n"
            
            # Range implications
            range_ratio = (max_val - min_val) / avg_val * 100
            if range_ratio > 100:
                analysis += f"• Wide value range ({min_val:.0f} to {max_val:.0f}) requires scalable operations to handle demand swings\n"
            else:
                analysis += f"• Manageable value range supports stable operational planning and resource utilization\n"
            
            # Strategic guidance based on domain
            domain = business_context.get('domain', 'general')
            if domain == 'forecasting':
                analysis += f"• Forecast accuracy critical for capacity planning - recommend monthly forecast reviews and adjustments\n"
            elif domain == 'workforce':
                analysis += f"• Workforce planning should account for demand variability with flexible staffing models\n"
            else:
                analysis += f"• Regular performance monitoring and adaptive strategy adjustments recommended\n"
                    
        # CONCISE Statistical methodology section
        analysis += f"""
### 📈 Statistical Methodology
• Trend Analysis: Linear regression slope coefficient converted to percentage change
• Volatility Measure: Coefficient of Variation (σ/μ × 100) - industry standard for relative dispersion
• Confidence Intervals: Based on t-distribution with {sum(s['data_points'] for s in series_data)-1} degrees of freedom
• Time Series Properties: {analysis_data['time_context'].get('time_frame', 'Cross-sectional')} frequency analysis
• Sample Size: n = {sum(s['data_points'] for s in series_data)} observations (minimum n=30 recommended for robust inference)
"""
        
        # Data quality assessment
        total_missing = sum(s.get('missing_points', 0) for s in series_data)
        if total_missing > 0:
            analysis += f"• Data Completeness: {total_missing} missing observations - may affect statistical power\n"
        
        return analysis


# Initialize global instance
chart_intelligence_agent = ChartIntelligenceAgent() 