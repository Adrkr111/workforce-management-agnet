from autogen import ConversableAgent
from .promp_engineering.forecasting_data_analyst_agent_prompt import forecasting_data_analyst_agent_system_message
from config import llm_config

def create_agent():
    with llm_config:
        forecasting_data_analyst_agent = ConversableAgent(
            name="Forecasting-Data-Analyst-Agent",
            system_message=forecasting_data_analyst_agent_system_message,
            human_input_mode="NEVER"
        )
    return forecasting_data_analyst_agent