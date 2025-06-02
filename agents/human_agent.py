from autogen import ConversableAgent
from config import llm_config

def create_agent():
    with llm_config:
        human_agent = ConversableAgent(name="human-agent", human_input_mode="ALWAYS")
    return human_agent