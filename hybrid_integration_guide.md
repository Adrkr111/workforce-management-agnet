#!/usr/bin/env python3
"""
Shared Services Layer for Workforce Management System
Can be used by both Chainlit and Teams Bot interfaces
"""

import asyncio
import json
from typing import Dict, Any, Optional
from datetime import datetime

# Import existing system components
from agents.orchestrator_agent import create_orchestrator_agent
from agents.fetch_agent import create_fetch_agent
from agents.data_analyst_agent import create_data_analyst_agent
from agents.visualization_agent import create_visualization_agent
from agents.kpi_agent import create_kpi_agent
from agents.simulation_agent import create_simulation_agent
from context_manager.context_manager import ContextManager
from config import llm_config

class WorkforceManagementService:
    """
    Shared service layer that can be used by both Chainlit and Teams Bot
    Provides consistent interface to workforce management agents
    """
    
    def __init__(self):
        self.agents = self._initialize_agents()
        self.context_manager = ContextManager()
        print("🏢 Workforce Management Service initialized")
    
    def _initialize_agents(self) -> Dict[str, Any]:
        """Initialize all workforce management agents"""
        try:
            agents = {
                "orchestrator": create_orchestrator_agent(llm_config),
                "fetch": create_fetch_agent(llm_config),
                "analyst": create_data_analyst_agent(llm_config),
                "visualization": create_visualization_agent(llm_config),
                "kpi": create_kpi_agent(llm_config),
                "simulation": create_simulation_agent(llm_config)
            }
            print("✅ All workforce agents initialized")
            return agents
        except Exception as e:
            print(f"❌ Error initializing agents: {e}")
            raise
    
    async def process_query(
        self, 
        query: str, 
        interface: str = "web",
        user_context: Optional[Dict] = None
    ) -> Dict[str, Any]:
        """
        Process a workforce management query
        
        Args:
            query: User's question/request
            interface: "web" (Chainlit) or "teams" (Teams Bot)
            user_context: Additional context (user_id, session_id, etc.)
        
        Returns:
            Standardized response dictionary
        """
        try:
            # Create processing context
            context = {
                "interface": interface,
                "timestamp": datetime.now().isoformat(),
                "query": query,
                **(user_context or {})
            }
            
            # Route to appropriate handler based on query type
            response = await self._route_query(query, context)
            
            return {
                "success": True,
                "response": response,
                "context": context,
                "interface": interface
            }
            
        except Exception as e:
            print(f"❌ Error processing query: {e}")
            return {
                "success": False,
                "error": str(e),
                "response": "I encountered an error processing your request.",
                "context": user_context,
                "interface": interface
            }
    
    async def _route_query(self, query: str, context: Dict) -> str:
        """Route query to appropriate agent based on content"""
        
        query_lower = query.lower()
        
        # Determine query type and route accordingly
        if any(keyword in query_lower for keyword in ["forecast", "volume", "prediction"]):
            return await self._handle_forecast_query(query, context)
        elif any(keyword in query_lower for keyword in ["kpi", "performance", "metrics"]):
            return await self._handle_kpi_query(query, context)
        elif any(keyword in query_lower for keyword in ["chart", "visualization", "plot"]):
            return await self._handle_visualization_query(query, context)
        elif any(keyword in query_lower for keyword in ["simulation", "fte", "optimization"]):
            return await self._handle_simulation_query(query, context)
        else:
            return await self._handle_general_query(query, context)
    
    async def _handle_forecast_query(self, query: str, context: Dict) -> str:
        """Handle forecast-related queries"""
        try:
            # Use your existing fetch agent
            # This would call your actual agent logic
            result = await self._call_agent("fetch", query, context)
            
            # Format response based on interface
            if context["interface"] == "teams":
                return self._format_teams_response(result, "forecast")
            else:
                return self._format_web_response(result, "forecast")
                
        except Exception as e:
            return f"Error processing forecast query: {e}"
    
    async def _handle_kpi_query(self, query: str, context: Dict) -> str:
        """Handle KPI-related queries"""
        try:
            result = await self._call_agent("kpi", query, context)
            
            if context["interface"] == "teams":
                return self._format_teams_response(result, "kpi")
            else:
                return self._format_web_response(result, "kpi")
                
        except Exception as e:
            return f"Error processing KPI query: {e}"
    
    async def _handle_visualization_query(self, query: str, context: Dict) -> str:
        """Handle visualization requests"""
        try:
            result = await self._call_agent("visualization", query, context)
            
            if context["interface"] == "teams":
                return self._format_teams_response(result, "visualization")
            else:
                return self._format_web_response(result, "visualization")
                
        except Exception as e:
            return f"Error processing visualization query: {e}"
    
    async def _handle_simulation_query(self, query: str, context: Dict) -> str:
        """Handle workforce simulation queries"""
        try:
            result = await self._call_agent("simulation", query, context)
            
            if context["interface"] == "teams":
                return self._format_teams_response(result, "simulation")
            else:
                return self._format_web_response(result, "simulation")
                
        except Exception as e:
            return f"Error processing simulation query: {e}"
    
    async def _handle_general_query(self, query: str, context: Dict) -> str:
        """Handle general workforce management queries"""
        if context["interface"] == "teams":
            return """🏢 **Workforce Management Assistant**

I can help you with:

**📈 Forecasting:** Volume predictions, demand analysis, capacity planning
**📊 KPI Analytics:** Performance metrics, trend analysis, department insights  
**📉 Visualizations:** Interactive charts, multi-team comparisons
**⚙️ Simulations:** FTE optimization, SLA compliance analysis

Please ask me about any specific workforce management topic!"""
        else:
            return """🏢 Workforce Management Assistant

I can help you with:
• 📈 Forecasting: Volume predictions, demand analysis, capacity planning
• 📊 KPI Analytics: Performance metrics, trend analysis, department insights  
• 📉 Visualizations: Interactive charts, multi-team comparisons
• ⚙️ Simulations: FTE optimization, SLA compliance analysis

Please ask me about any specific workforce management topic!"""
    
    async def _call_agent(self, agent_type: str, query: str, context: Dict) -> Any:
        """Call the appropriate agent with the query"""
        try:
            # This is where you'd integrate with your actual agents
            # For now, returning simulated responses
            
            if agent_type == "fetch":
                return {
                    "business_unit": "LOGISTICS",
                    "substream": "DLT",
                    "team": "SUPPORT",
                    "forecast_data": [
                        {"month": "2025-06", "volume": 2845},
                        {"month": "2025-07", "volume": 2843},
                        {"month": "2025-10", "volume": 3597}
                    ]
                }
            elif agent_type == "kpi":
                return {
                    "kpi_name": "Home Loan Attrition Rate",
                    "current_value": 15.67,
                    "trend": "decreasing",
                    "department": "Operations"
                }
            elif agent_type == "visualization":
                return {
                    "chart_type": "line",
                    "data_points": 12,
                    "status": "generated"
                }
            elif agent_type == "simulation":
                return {
                    "ftes": 100,
                    "capacity_utilization": 47.3,
                    "sla_achievement": 99.2
                }
            else:
                return {"status": "processed"}
                
        except Exception as e:
            print(f"❌ Error calling agent {agent_type}: {e}")
            raise
    
    def _format_teams_response(self, result: Any, query_type: str) -> str:
        """Format response for Microsoft Teams (with rich markdown)"""
        
        if query_type == "forecast":
            return f"""📈 **Workforce Forecast Results**

**📊 Team Overview:**
• Business Unit: {result.get('business_unit', 'N/A')}
• Substream: {result.get('substream', 'N/A')}
• Team: {result.get('team', 'N/A')}

**📅 Forecast Data:**
{self._format_forecast_data_teams(result.get('forecast_data', []))}

Would you like me to create a visualization or provide detailed analysis?"""
        
        elif query_type == "kpi":
            return f"""📊 **KPI Performance Analysis**

**{result.get('kpi_name', 'KPI')} Trend:**
• Current Rate: {result.get('current_value', 'N/A')}%
• Department: {result.get('department', 'N/A')}
• Trend: {result.get('trend', 'N/A').title()}

Would you like detailed insights or a performance visualization?"""
        
        elif query_type == "visualization":
            return f"""📉 **Data Visualization Created**

✅ **Chart Generated Successfully:**
• Type: {result.get('chart_type', 'Chart')} chart
• Data points: {result.get('data_points', 'N/A')} points
• Status: {result.get('status', 'Generated')}

The chart shows trends and patterns for workforce planning."""
        
        elif query_type == "simulation":
            return f"""⚙️ **Workforce Simulation Results**

**Scenario:** {result.get('ftes', 'N/A')} FTEs

**📊 Performance:**
• Capacity Utilization: {result.get('capacity_utilization', 'N/A')}%
• SLA Achievement: {result.get('sla_achievement', 'N/A')}%

**💡 Recommendations:** Optimal staffing for current volume"""
        
        return str(result)
    
    def _format_web_response(self, result: Any, query_type: str) -> str:
        """Format response for Chainlit web interface"""
        
        if query_type == "forecast":
            return f"""📈 Workforce Forecast Results

Team Overview:
• Business Unit: {result.get('business_unit', 'N/A')}
• Substream: {result.get('substream', 'N/A')}
• Team: {result.get('team', 'N/A')}

Forecast Data:
{self._format_forecast_data_web(result.get('forecast_data', []))}

Would you like me to create a visualization or provide detailed analysis?"""
        
        elif query_type == "kpi":
            return f"""📊 KPI Performance Analysis

{result.get('kpi_name', 'KPI')} Trend:
• Current Rate: {result.get('current_value', 'N/A')}%
• Department: {result.get('department', 'N/A')}
• Trend: {result.get('trend', 'N/A').title()}

Would you like detailed insights or a performance visualization?"""
        
        # Similar formatting for other types...
        return str(result)
    
    def _format_forecast_data_teams(self, data: list) -> str:
        """Format forecast data for Teams"""
        if not data:
            return "• No forecast data available"
        
        lines = []
        for item in data[:3]:  # Show top 3
            lines.append(f"• {item['month']}: {item['volume']:,} volume")
        
        return "\n".join(lines)
    
    def _format_forecast_data_web(self, data: list) -> str:
        """Format forecast data for web"""
        if not data:
            return "• No forecast data available"
        
        lines = []
        for item in data:
            lines.append(f"• {item['month']}: {item['volume']:,} volume")
        
        return "\n".join(lines)

# Singleton instance for shared use
workforce_service = WorkforceManagementService() 