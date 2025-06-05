from autogen import ConversableAgent
from typing import Annotated
from embedding.embedding import get_gemini_embedding
from vector_database.chroma import get_chroma_client
from .promp_engineering.fetch_forecasting_agent_prompt import fetch_forecasting_agent_system_message
from config import llm_config

# Import for data store integration - will be set by app_teams.py
_vector_data_store = None
_current_session_id = None

def set_data_store_context(data_store, session_id):
    """Set the data store and session context for this function"""
    global _vector_data_store, _current_session_id
    _vector_data_store = data_store
    _current_session_id = session_id

# -- Fetch forecast function used by agent --
def fetch_forecast(args):
    """Fetch forecast data based on business type, substream, and team"""
    print(f"🔥 RAW INPUT - Processing forecast request:")
    print(f"📝 Args Type: {type(args)}")
    print(f"📦 Args Size: {len(str(args))} characters")
    print(f"🔥 RAW COMPLETE ARGS:")
    print(f"{'='*50}")
    print(str(args))
    print(f"{'='*50}")
    
    try:
        # ✅ ENHANCED ARGUMENT PARSING - Handle both dict and string inputs
        business_type = None
        substream_type = None
        team_name = None
        original_user_request = str(args)  # Start with args as fallback
        
        # NEW: Handle dictionary input from agents
        if isinstance(args, dict):
            print("🔥 RAW DICT PROCESSING - Complete breakdown:")
            for key, value in args.items():
                print(f"   🔑 [{key}]: {value}")
            business_type = args.get('business') or args.get('business_type')
            substream_type = args.get('substream') or args.get('substream_type') or args.get('stream')
            team_name = args.get('team') or args.get('team_name')
            print(f"🔥 RAW EXTRACTED: business={business_type}, substream={substream_type}, team={team_name}")
        
        # EXISTING: Handle string input (backward compatibility)
        elif isinstance(args, str):
            print("🔥 RAW STRING PROCESSING")
            original_user_request = args  # Store original for conversational agent
            
            # Convert to lowercase for easier parsing
            args_lower = args.lower()
            
            # Method 1: Try simple space-separated format first (backwards compatibility)
            parts = args.strip().split()
            if len(parts) == 3 and not any(word in args_lower for word in ['business', 'substream', 'team', 'is', 'and', '"']):
                business_type = parts[0].replace('business-', '')
                substream_type = parts[1].replace('substream-', '')
                team_name = parts[2].replace('team-', '')
                print(f"🔥 RAW SIMPLE FORMAT: business={business_type}, substream={substream_type}, team={team_name}")
            else:
                # Method 2: Parse natural language format
                import re
                
                # Extract business - multiple patterns
                business_patterns = [
                    r'business\s+is\s+["\']?([^"\'",\s]+)["\']?',
                    r'business\s*[:\-=]\s*["\']?([^"\'",\s]+)["\']?',
                    r'business\s+["\']?([^"\'",\s]+)["\']?'
                ]
                for pattern in business_patterns:
                    match = re.search(pattern, args_lower)
                    if match:
                        business_type = match.group(1)
                        break
                
                # Extract substream - multiple patterns  
                substream_patterns = [
                    r'substream\s+is\s+["\']?([^"\'",\s]+)["\']?',
                    r'substream\s*[:\-=]\s*["\']?([^"\'",\s]+)["\']?',
                    r'substream\s+["\']?([^"\'",\s]+)["\']?',
                    r'stream\s+is\s+["\']?([^"\'",\s]+)["\']?',
                    r'stream\s*[:\-=]\s*["\']?([^"\'",\s]+)["\']?'
                ]
                for pattern in substream_patterns:
                    match = re.search(pattern, args_lower)
                    if match:
                        substream_type = match.group(1)
                        break
                
                # Extract team - multiple patterns
                team_patterns = [
                    r'team\s+name\s+is\s+["\']?([^"\'",\s]+)["\']?',
                    r'team\s+is\s+["\']?([^"\'",\s]+)["\']?',
                    r'team\s*[:\-=]\s*["\']?([^"\'",\s]+)["\']?',
                    r'team\s+["\']?([^"\'",\s]+)["\']?'
                ]
                for pattern in team_patterns:
                    match = re.search(pattern, args_lower)
                    if match:
                        team_name = match.group(1)
                        break
                
                print(f"🔥 RAW NLP PARSING: business={business_type}, substream={substream_type}, team={team_name}")
        
        else:
            return f'Invalid argument type: {type(args)}. Expected string or dictionary.'
        
        # Validate we have all required parameters
        if not all([business_type, substream_type, team_name]):
            missing = []
            if not business_type:
                missing.append("business unit")
            if not substream_type:
                missing.append("substream")
            if not team_name:
                missing.append("team name")
            
            return f'I need more details to find the right forecast. Please specify: {", ".join(missing)}.\n\nExample: "Get forecast for business logistics, substream dlt, team support"'
        
        print(f"🔥 RAW FINAL PARAMS: business={business_type}, substream={substream_type}, team={team_name}")
        
        # Get ChromaDB client and collection
        client = get_chroma_client()
        collection = client.get_or_create_collection(name="forecast_data")
        
        # Get embedding for the query
        query = f"work volume forecast for {business_type} {substream_type} {team_name}"
        print("🔥 RAW QUERY STRING:", query)
        print("🔥 RAW DATABASE - Getting query embedding...")
        query_embedding = get_gemini_embedding(query)
        print(f"🔥 RAW EMBEDDING LENGTH: {len(query_embedding) if query_embedding else 'None'}")
        
        print("🔥 RAW DATABASE - Querying vector database...")
        results = collection.query(
            query_embeddings=[query_embedding],
            n_results=3,
            include=["documents", "metadatas", "distances"]
        )
        
        # 🔥 RAW VECTOR DATABASE RESULTS DUMP
        print(f"🔥 RAW VECTOR DB RESULTS - COMPLETE DUMP:")
        print(f"📝 Results Type: {type(results)}")
        print(f"🔑 Results Keys: {list(results.keys()) if isinstance(results, dict) else 'Not a dict'}")
        
        if results and isinstance(results, dict):
            for key, value in results.items():
                print(f"🔥 RAW VECTOR [{key}]:")
                if isinstance(value, list) and value:
                    print(f"   📊 Length: {len(value)}")
                    for i, item in enumerate(value[:2]):  # Show first 2 items
                        print(f"   📋 Item [{i}]: {str(item)[:300]}{'...' if len(str(item)) > 300 else ''}")
                else:
                    print(f"   📝 Value: {str(value)[:200]}{'...' if len(str(value)) > 200 else ''}")
        
        if not results or not results.get('documents') or not results['documents'][0]:
            return f'I couldn\'t find any forecast data for the {business_type} {team_name} team in {substream_type}. Would you like to try a different combination?'
        
        # ✅ PREPARE RAW RESULTS FOR PROCESSING
        raw_results = []
        for i, (doc, metadata, distance) in enumerate(zip(
            results['documents'][0], 
            results.get('metadatas', [[{}] * len(results['documents'][0])])[0],
            results['distances'][0]
        )):
            confidence = 1 - distance
            raw_result = {
                'document': doc,
                'metadata': metadata,
                'confidence': confidence,
                'rank': i + 1
            }
            raw_results.append(raw_result)
            
            # 🔥 RAW RESULT DUMP
            print(f"🔥 RAW RESULT [{i+1}]:")
            print(f"   📊 Confidence: {confidence:.3f}")
            print(f"   📊 Distance: {distance:.3f}")
            print(f"   📄 Document: {str(doc)[:400]}{'...' if len(str(doc)) > 400 else ''}")
            print(f"   🏷️ Metadata: {metadata}")
        
        # 🤖 INTELLIGENT CONVERSATIONAL PROCESSING AGENT
        print("🔥 RAW PROCESSING - Creating intelligent agent...")
        
        # Create intelligent processing agent
        processing_agent = ConversableAgent(
            name="Forecast-Processing-Agent",
            llm_config=llm_config,
            system_message=f"""
🧠 **INTELLIGENT FORECAST FORMATTER & FILTER**

You process vector search results according to user requirements. Your job:

1. **UNDERSTAND USER INTENT**: Analyze what the user specifically asked for
2. **FILTER RESULTS**: Focus on exact matches and relevant data  
3. **FORMAT OUTPUT**: Apply user's formatting preferences (table, list, summary, etc.)
4. **BE CONVERSATIONAL**: Natural language, not robotic

**📊 USER'S ORIGINAL REQUEST**: {original_user_request}

**🎯 FORMATTING RULES**:
- If user asks for "table" → Create clean markdown table format
- If user asks for "summary" → Provide brief overview with key points
- If user asks for "detailed" → Include trends and insights
- If user asks for specific timeframe → Filter to those dates only
- If user asks for specific team → Focus only on that team
- Always prioritize exact team matches over partial matches

**💡 EXAMPLES**:
User: "get logistics forecast as a table" → Return markdown table
User: "show me just Q4 numbers" → Extract Oct-Dec data only  
User: "summarize the support team forecast" → Brief overview with key points
User: "forecast data for next 6 months" → Focus on next 6 months only

**🚨 IMPORTANT**: Return ONLY the formatted content. No wrapper text like "Here's what I found" - just the actual data in the requested format.
""",
            human_input_mode="NEVER"
        )
        
        # Prepare context for processing agent
        results_context = f"""ORIGINAL USER REQUEST: {original_user_request}

TARGET: Business={business_type}, Substream={substream_type}, Team={team_name}

VECTOR SEARCH RESULTS ({len(raw_results)} matches):

"""
        
        for result in raw_results:
            results_context += f"""Match {result['rank']} (Confidence: {result['confidence']:.1%}):
{result['document']}

"""
        
        results_context += f"""
TASK: Process these results according to the user's original request. Apply any formatting requirements (table, summary, etc.) and filter for the most relevant data. Return ONLY the formatted output - no explanatory text."""
        
        # 🔥 RAW AGENT CONTEXT DUMP
        print(f"🔥 RAW AGENT CONTEXT:")
        print(f"{'='*50}")
        print(results_context)
        print(f"{'='*50}")
        
        # Get intelligent processing
        try:
            response = processing_agent.generate_reply(
                messages=[{"role": "user", "content": results_context}]
            )
            
            # 🔥 RAW AGENT RESPONSE DUMP
            print(f"🔥 RAW AGENT RESPONSE:")
            print(f"📝 Response Type: {type(response)}")
            print(f"📄 Response Content:")
            print(f"{'='*50}")
            print(str(response))
            print(f"{'='*50}")
            
            if isinstance(response, dict) and 'content' in response:
                processed_content = response['content']
            elif isinstance(response, str):
                processed_content = response
            else:
                processed_content = str(response)
            
            print(f"🔥 RAW PROCESSED CONTENT:")
            print(f"📄 Final Content: {processed_content[:400]}{'...' if len(processed_content) > 400 else ''}")
            
            # 📊 STORE IN VECTOR DATA STORE FOR VISUALIZATION ACCESS
            if _vector_data_store and _current_session_id:
                try:
                    # Store the processed result in the data store
                    entry_id = _vector_data_store.store_search_result(
                        session_id=_current_session_id,
                        query_type="forecast",
                        business=business_type,
                        substream=substream_type,
                        team=team_name,
                        result_data=processed_content,
                        metadata={
                            "original_request": original_user_request,
                            "raw_results_count": len(raw_results),
                            "confidence_scores": [r['confidence'] for r in raw_results],
                            "query": query
                        }
                    )
                    print(f"✅ Stored forecast data in vector data store: {entry_id}")
                except Exception as store_error:
                    print(f"⚠️ Failed to store in vector data store: {store_error}")
            else:
                print("⚠️ Vector data store not available - skipping storage")
            
            # Return JUST the processed content
            return processed_content
            
        except Exception as e:
            print(f"🔥 RAW PROCESSING ERROR: {str(e)}")
            # Fallback to simple processing if agent fails
            best_match = min(raw_results, key=lambda x: x['rank'])
            return f"""📊 {business_type.upper()} {substream_type.upper()} {team_name.upper()} TEAM FORECAST

{best_match['document']}

Confidence: {best_match['confidence']:.1%}"""
            
    except Exception as e:
        print(f"🔥 RAW ERROR: {str(e)}")
        return f'I encountered an issue while fetching the forecast data: {str(e)}. Would you like to try again?'

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