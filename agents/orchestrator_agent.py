from autogen import ConversableAgent
from config import llm_config
from .promp_engineering.orchestrator_agent_prompt import orchestrator_agent_system_message

def create_agent():
    orchestrator_agent = ConversableAgent(
        name="Orchestrator-Agent",
        llm_config=llm_config,
        system_message=orchestrator_agent_system_message,
        is_termination_msg=lambda x: "TERMINATE" in x.get("content", ""),
        human_input_mode="NEVER"
    )
    return orchestrator_agent 