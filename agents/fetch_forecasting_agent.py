from autogen import ConversableAgent
from typing import Annotated
from embedding.embedding import get_gemini_embedding
from vector_database.chroma import get_chroma_client
from .promp_engineering.fetch_forecasting_agent_prompt import fetch_forecasting_agent_system_message
from config import llm_config
# -- Fetch forecast function used by agent --
def fetch_forecast(query_text: Annotated[str, "user input query, must contain business type , substream type and teams type in it "]):
    client = get_chroma_client()
    collection = client.get_or_create_collection(name="forecast_data")
    query_embedding = get_gemini_embedding(query_text)
    results = collection.query(
        query_embeddings=[query_embedding],
        n_results=3,
        include=["documents", "metadatas", "distances"]
    )
    return {'results': results['documents'][0]}

def create_agent():
    with llm_config:
        fetch_volume_forecast_agent = ConversableAgent(
            name="Fetch-Volume-Forecast-Agent",
            human_input_mode="NEVER",
            system_message=fetch_forecasting_agent_system_message,
            functions=[fetch_forecast],

        )
    # data_analyst_bot = ConversableAgent(
    #     name="data-analyst-bot",
    #     system_message=data_analyst_system_message,
    # )
    # human = ConversableAgent(name="human", human_input_mode="ALWAYS")
    return fetch_volume_forecast_agent