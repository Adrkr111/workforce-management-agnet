from autogen import ConversableAgent
from .promp_engineering.forecasting_data_analyst_agent_prompt import forecasting_data_analyst_agent_system_message
from config import llm_config

def create_agent():
    forecasting_data_analyst_agent = ConversableAgent(
        name="Forecasting-Data-Analyst-Agent",
        llm_config=llm_config,
        system_message=forecasting_data_analyst_agent_system_message,
        is_termination_msg=lambda x: "TERMINATE" in x.get("content", ""),
        human_input_mode="NEVER"
    )
    return forecasting_data_analyst_agent