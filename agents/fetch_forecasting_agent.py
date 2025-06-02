from autogen import ConversableAgent
from typing import Annotated
from embedding.embedding import get_gemini_embedding
from vector_database.chroma import get_chroma_client
from .promp_engineering.fetch_forecasting_agent_prompt import fetch_forecasting_agent_system_message
from config import llm_config
# -- Fetch forecast function used by agent --
def fetch_forecast(args: str):
    """Fetch forecast data based on business type, substream, and team"""
    print(f"Debug - Processing forecast request with args: {args}")
    try:
        # Parse the arguments
        parts = args.strip().split()
        if len(parts) != 3:
            return {'error': 'Please provide all three parameters: business-type substream-type team-name'}
            
        business_type = parts[0].replace('business-', '')
        substream_type = parts[1].replace('substream-', '')
        team_name = parts[2].replace('team-', '')
        
        print(f"Debug - Parsed parameters: business={business_type}, substream={substream_type}, team={team_name}")
        
        # Get ChromaDB client and collection
        client = get_chroma_client()
        collection = client.get_or_create_collection(name="forecast_data")
        
        # Get embedding for the query
        query = f"work volume forecast for {business_type} {substream_type} {team_name}"
        print("Debug - Getting query embedding...")
        query_embedding = get_gemini_embedding(query)
        
        print("Debug - Querying vector database...")
        results = collection.query(
            query_embeddings=[query_embedding],
            n_results=5,
            include=["documents", "metadatas", "distances"]
        )
        
        if not results or not results.get('documents') or not results['documents'][0]:
            return {'error': f'I couldn\'t find any forecast data for the {business_type} {team_name} team in {substream_type}. Would you like to try a different combination?'}
        
        # Format the results professionally and conversationally
        output = f"""
I've found some relevant workforce forecasts for you:

📊 Team Overview:
• Business Unit: {business_type.upper()}
• Substream: {substream_type.upper()}
• Team: {team_name.capitalize()}

Here are the most relevant forecasts I found:

"""
        for i, (doc, distance) in enumerate(zip(results['documents'][0], results['distances'][0]), 1):
            similarity = 1 - distance  # Convert distance to similarity score
            output += f"Match {i} (Confidence: {similarity:.2%}):\n{doc}\n\n"
        
        output += """
I can help you understand this data better. Would you like me to:

📈 Provide a detailed business impact analysis?
🎯 Focus on specific time periods?
🔄 Compare these numbers with other teams?

Let me know what would be most valuable for your needs.
==== DATA RETRIEVED ===="""
        
        return {'results': output}
            
    except Exception as e:
        print(f"Error: {str(e)}")
        return {'error': f'I encountered an issue while fetching the forecast data: {str(e)}. Would you like to try again?'}

def create_agent():
    fetch_volume_forecast_agent = ConversableAgent(
        name="Fetch-Volume-Forecast-Agent",
        llm_config=llm_config,
        system_message=fetch_forecasting_agent_system_message,
        is_termination_msg=lambda x: "TERMINATE" in x.get("content", ""),
        human_input_mode="NEVER",
        function_map={
            "fetch_forecast": fetch_forecast
        }
    )
    # data_analyst_bot = ConversableAgent(
    #     name="data-analyst-bot",
    #     system_message=data_analyst_system_message,
    # )
    # human = ConversableAgent(name="human", human_input_mode="ALWAYS")
    return fetch_volume_forecast_agent