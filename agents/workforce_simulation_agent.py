from autogen import ConversableAgent
from config import llm_config
from .promp_engineering.workforce_simulation_agent_prompt import workforce_simulation_agent_system_message

def create_agent():
    """
    Creates a Workforce Optimization Simulation Agent for capacity planning and SLA analysis.
    
    This agent:
    - Analyzes workforce capacity vs demand
    - Detects SLA breach risks  
    - Calculates optimal FTE requirements
    - Provides month-by-month simulation breakdown
    - Shows detailed mathematical calculations
    - Gives strategic workforce planning recommendations
    """
    workforce_simulation_agent = ConversableAgent(
        name="Workforce-Simulation-Agent",
        llm_config=llm_config,
        system_message=workforce_simulation_agent_system_message,
        is_termination_msg=lambda x: "TERMINATE" in x.get("content", ""),
        human_input_mode="NEVER",
        function_map={}  # This is a prompt-based agent with no functions
    )
    return workforce_simulation_agent 