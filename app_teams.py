import chainlit as cl
from context_manager.context_manager import ContextManager
from config import llm_config
from agents import (
    fetch_forecasting_agent, 
    forecasting_data_analyst_agent,
    data_visualization_agent,
    orchestrator_agent,
    kpi_agent,
    workforce_simulation_agent
)
from agents.promp_engineering.fetch_forecasting_agent_prompt import fetch_forecasting_agent_system_message
from agents.promp_engineering.forecasting_data_analyst_agent_prompt import forecasting_data_analyst_agent_system_message
from autogen.agentchat import ConversableAgent
import asyncio
from typing import Optional, Dict
import nest_asyncio
from dataclasses import dataclass
import chromadb
from chromadb.config import Settings
from datetime import datetime
import json
from vector_database.chroma import get_chroma_client
import time
import plotly.graph_objects as go

# Apply nest_asyncio to allow nested event loops
nest_asyncio.apply()

# ========== VECTOR SEARCH RESULTS DATA STORE ==========
class VectorSearchDataStore:
    """Dedicated data store for vector search results in chronological order"""
    
    def __init__(self):
        self.search_results = {}  # session_id -> list of search results
        
    def store_search_result(self, session_id, query_type, business, substream, team, result_data, metadata=None):
        """Store vector search result with chronological ordering - ENHANCED RAW DATA LOGGING"""
        if session_id not in self.search_results:
            self.search_results[session_id] = []
            print(f"🆕 AUDIT - Created new data store session: {session_id}")
            
        current_time = datetime.now()
        search_entry = {
            "timestamp": current_time,
            "timestamp_sort": current_time.timestamp(),
            "query_type": query_type,  # "forecast", "kpi", etc.
            "business": business,
            "substream": substream, 
            "team": team,
            "result_data": result_data,
            "metadata": metadata or {},
            "entry_id": f"{query_type}_{session_id}_{current_time.strftime('%Y%m%d_%H%M%S_%f')}"
        }
        
        self.search_results[session_id].append(search_entry)
        
        # 📊 COMPREHENSIVE RAW DATA LOGGING
        print(f"📊 RAW DATA STORAGE - COMPLETE DATA DUMP:")
        print(f"   🆔 Entry ID: {search_entry['entry_id']}")
        print(f"   📅 Timestamp: {current_time.strftime('%Y-%m-%d %H:%M:%S.%f')}")
        print(f"   🔍 Query Type: {query_type}")
        print(f"   🏢 Business: {business}")
        print(f"   🌊 Substream: {substream}")
        print(f"   👥 Team: {team}")
        print(f"   📦 Data Size: {len(str(result_data))} characters")
        
        # 🔥 RAW DATA COMPLETE DUMP
        print(f"   🔥 RAW RESULT DATA (FULL):")
        print(f"      📝 Type: {type(result_data)}")
        if isinstance(result_data, dict):
            print(f"      📊 Dict Keys: {list(result_data.keys())}")
            for key, value in result_data.items():
                print(f"      🔑 [{key}]: {str(value)[:200]}{'...' if len(str(value)) > 200 else ''}")
        elif isinstance(result_data, list):
            print(f"      📋 List Length: {len(result_data)}")
            for i, item in enumerate(result_data[:3]):  # Show first 3 items
                print(f"      🔢 [{i}]: {str(item)[:200]}{'...' if len(str(item)) > 200 else ''}")
        else:
            print(f"      📄 String/Other Content:")
            print(f"      {str(result_data)[:500]}{'...' if len(str(result_data)) > 500 else ''}")
        
        # 🔥 RAW METADATA COMPLETE DUMP
        if metadata:
            print(f"   🔥 RAW METADATA (FULL):")
            print(f"      📝 Type: {type(metadata)}")
            for key, value in metadata.items():
                print(f"      🏷️ [{key}]: {str(value)[:100]}{'...' if len(str(value)) > 100 else ''}")
        
        print(f"   🗃️ Session Total: {len(self.search_results[session_id])} entries")
        
        # Keep only last 50 entries per session to prevent memory bloat
        if len(self.search_results[session_id]) > 50:
            removed_count = len(self.search_results[session_id]) - 50
            self.search_results[session_id] = self.search_results[session_id][-50:]
            print(f"🗑️ AUDIT - Cleaned up {removed_count} old entries, kept 50 most recent")
            
        print(f"✅ RAW DATA STORED - {query_type} data for {business}-{substream}-{team}")
        return search_entry["entry_id"]
    
    def get_latest_results(self, session_id, query_type=None, business=None, substream=None, team=None, limit=10):
        """Get latest search results matching criteria - ENHANCED RAW DATA LOGGING"""
        print(f"🔍 RAW DATA RETRIEVAL - COMPLETE DUMP:")
        print(f"   🆔 Session ID: {session_id}")
        print(f"   🔍 Query Type: {query_type or 'ANY'}")
        print(f"   🏢 Business: {business or 'ANY'}")
        print(f"   🌊 Substream: {substream or 'ANY'}")
        print(f"   👥 Team: {team or 'ANY'}")
        print(f"   📊 Limit: {limit}")
        
        if session_id not in self.search_results:
            print(f"❌ RAW DATA - No data store found for session: {session_id}")
            return []
            
        results = self.search_results[session_id]
        print(f"📦 RAW DATA - Total entries in session: {len(results)}")
        
        # 🔥 DUMP ALL RAW ENTRIES IN SESSION
        print(f"🔥 RAW DATA SESSION DUMP - ALL ENTRIES:")
        for i, result in enumerate(results):
            print(f"   📋 Entry [{i+1}]:")
            print(f"      🆔 ID: {result['entry_id']}")
            print(f"      📅 Time: {result['timestamp'].strftime('%H:%M:%S')}")
            print(f"      🔍 Type: {result['query_type']}")
            print(f"      🏢 Business: {result['business']}")
            print(f"      🌊 Substream: {result['substream']}")
            print(f"      👥 Team: {result['team']}")
            print(f"      📦 Data Preview: {str(result['result_data'])[:100]}...")
            print(f"      📄 Data Type: {type(result['result_data'])}")
        
        # Filter by criteria
        filtered_results = []
        for result in results:
            match = True
            if query_type and result["query_type"] != query_type:
                match = False
            if business and result["business"].lower() != business.lower():
                match = False
            if substream and result["substream"].lower() != substream.lower():
                match = False
            if team and result["team"].lower() != team.lower():
                match = False
                
            if match:
                filtered_results.append(result)
                print(f"✅ RAW DATA MATCH: {result['business']}-{result['substream']}-{result['team']} @ {result['timestamp'].strftime('%H:%M:%S')}")
        
        # Sort by timestamp (most recent first)
        filtered_results.sort(key=lambda x: x["timestamp_sort"], reverse=True)
        final_results = filtered_results[:limit]
        
        print(f"📊 RAW DATA RETRIEVAL SUMMARY:")
        print(f"   🔍 Total session entries: {len(results)}")
        print(f"   ✅ Filtered matches: {len(filtered_results)}")
        print(f"   📤 Final returned: {len(final_results)}")
        
        # 🔥 DUMP FINAL RETURNED RAW DATA
        if final_results:
            print(f"🔥 FINAL RAW DATA BEING RETURNED:")
            for i, result in enumerate(final_results):
                print(f"   📋 Result [{i+1}]:")
                print(f"      🆔 ID: {result['entry_id']}")
                print(f"      📅 Time: {result['timestamp'].strftime('%H:%M:%S')}")
                print(f"      🏢 {result['business']}-{result['substream']}-{result['team']}")
                print(f"      📦 Raw Data Type: {type(result['result_data'])}")
                print(f"      📄 Raw Data Content:")
                if isinstance(result['result_data'], dict):
                    for key, value in result['result_data'].items():
                        print(f"         🔑 [{key}]: {str(value)[:150]}{'...' if len(str(value)) > 150 else ''}")
                else:
                    print(f"         📝 {str(result['result_data'])[:300]}{'...' if len(str(result['result_data'])) > 300 else ''}")
        
        return final_results
    
    def get_latest_forecast_data(self, session_id, limit=5):
        """Get latest forecast data for visualization"""
        forecast_results = self.get_latest_results(session_id, query_type="forecast", limit=limit)
        
        if not forecast_results:
            return None
            
        # Return the most recent forecast data
        latest = forecast_results[0]
        print(f"🎯 Found latest forecast data: {latest['business']}-{latest['substream']}-{latest['team']}")
        return latest
    
    def clear_session(self, session_id):
        """Clear all search results for a session"""
        if session_id in self.search_results:
            del self.search_results[session_id]
            print(f"🗑️ Cleared vector search data store for session: {session_id}")

# Global vector search data store
vector_data_store = VectorSearchDataStore()

def get_session_vector_data_store():
    """Get the global vector data store (singleton pattern)"""
    return vector_data_store

# ========== TEAMS SESSION MANAGEMENT ==========
# Teams-specific session manager to handle persistent user sessions
class TeamsSessionManager:
    """Manages Teams user sessions with persistent state"""
    
    def __init__(self):
        self.sessions = {}  # session_id -> session_data
        
    def get_teams_session_id(self, teams_user=None):
        """Get consistent session ID for Teams user"""
        if not teams_user:
            print("⚠️ No Teams user provided, using anonymous session")
            return "teams_anonymous"
            
        try:
            # Extract Teams user ID from metadata
            if hasattr(teams_user, 'metadata') and teams_user.metadata:
                user_id = teams_user.metadata.get('id')
                if user_id:
                    print(f"🔍 Teams user dictionary id: {user_id}")
                    session_id = f"teams_{user_id}"
                    print(f"🔍 Generated Teams session ID: {session_id} from user: {teams_user}")
                    return session_id
            
            # Try identifier as fallback
            if hasattr(teams_user, 'identifier') and teams_user.identifier:
                user_id = teams_user.identifier
                if user_id and user_id != 'teams_Aindril Kar':  # Skip generic identifier
                    print(f"🔍 Using Teams user identifier: {user_id}")
                    session_id = f"teams_{user_id.replace(' ', '_')}"
                    print(f"🔍 Generated Teams session ID from identifier: {session_id}")
                    return session_id
                    
        except Exception as e:
            print(f"⚠️ Error extracting Teams user info: {e}")
        
        # Try to get from Chainlit user session as final fallback
        try:
            chainlit_user = cl.user_session.get('user')
            if chainlit_user and isinstance(chainlit_user, dict):
                user_id = (chainlit_user.get("id") or 
                          chainlit_user.get("identifier") or
                          chainlit_user.get("metadata", {}).get("id"))
                
                if user_id:
                    if isinstance(user_id, str) and ":" in user_id:
                        user_id = user_id.split(":")[-1][:16]
                    session_id = f"teams_{user_id}"
                    print(f"🔍 Generated session ID from Chainlit user: {session_id}")
                    return session_id
        except Exception as e:
            print(f"⚠️ Error extracting Chainlit user info: {e}")
        
        # Final fallback to anonymous session
        print("⚠️ No Teams user ID found, using anonymous session")
        return "teams_anonymous"
    
    def get_or_create_session(self, session_id, teams_user=None):
        """Get or create session for Teams user"""
        current_time = datetime.now()
        
        if session_id not in self.sessions:
            self.sessions[session_id] = {
                "user": teams_user,
                "created_at": current_time,
                "last_active": current_time,
                "context": {
                    "teams": [],
                    "last_query": None,
                    "current_comparison": None,
                    "visualizations": []
                },
                "agents": None,  # Will be created once per session
                "context_manager": None,  # Will be created once per session
                "chroma_client": None,  # Will be created once per session
                "is_new": True  # Flag to track if this is a brand new session
            }
            print(f"📱 Created new Teams session: {session_id}")
            return self.sessions[session_id]
        else:
            # Update last active time for existing session
            self.sessions[session_id]["last_active"] = current_time
            self.sessions[session_id]["is_new"] = False
            time_since_active = current_time - self.sessions[session_id]["last_active"]
            
            print(f"📱 Using existing Teams session: {session_id}")
            print(f"📱 Session resumed: {session_id} (Last active: {self.sessions[session_id]['last_active']})")
            print(f"🔄 Continuing existing session - no UI message sent")
            
            return self.sessions[session_id]

# Global Teams session manager
teams_session_manager = TeamsSessionManager()

# ========== SESSION-BASED RESOURCE MANAGEMENT ==========
def get_session_chroma_client(session_id):
    """Get or create ChromaDB client for session"""
    session_data = teams_session_manager.sessions.get(session_id)
    if session_data and session_data["chroma_client"] is None:
        session_data["chroma_client"] = get_chroma_client()
        print(f"💾 Created ChromaDB client for session: {session_id}")
    elif session_data:
        print(f"💾 Reusing ChromaDB client for session: {session_id}")
    
    return session_data["chroma_client"] if session_data else get_chroma_client()

def get_session_context_manager(session_id):
    """Get or create context manager for session"""
    session_data = teams_session_manager.sessions.get(session_id)
    if session_data and session_data["context_manager"] is None:
        session_data["context_manager"] = ContextManager()
        print(f"🗂️ Created context manager for session: {session_id}")
    elif session_data:
        print(f"🗂️ Reusing context manager for session: {session_id}")
    
    return session_data["context_manager"] if session_data else ContextManager()

def get_session_agents(session_id):
    """Get or create agents for session"""
    session_data = teams_session_manager.sessions.get(session_id)
    if session_data and session_data["agents"] is None:
        print(f"🤖 Creating agents for session: {session_id}")
        session_data["agents"] = create_agents()
        print(f"✅ Created {len(session_data['agents'])} agents for session: {session_id}")
    elif session_data:
        print(f"✅ Reusing {len(session_data['agents'])} agents for session: {session_id}")
    
    return session_data["agents"] if session_data else create_agents()

# Create a separate collection for agent conversations
def get_conversation_collection(session_id="default"):
    """Get or create a separate collection for agent conversations"""
    chroma_client = get_session_chroma_client(session_id)
    
    # Sanitize session_id for ChromaDB collection naming
    # ChromaDB allows only [a-zA-Z0-9._-] and must start/end with [a-zA-Z0-9]
    sanitized_session_id = session_id.replace(":", "_").replace("@", "_").replace(" ", "_")
    # Ensure it starts and ends with alphanumeric
    if not sanitized_session_id[0].isalnum():
        sanitized_session_id = "a" + sanitized_session_id
    if not sanitized_session_id[-1].isalnum():
        sanitized_session_id = sanitized_session_id + "a"
    
    collection_name = f"agent_conversations_{sanitized_session_id}"
    
    # Ensure collection name length is within ChromaDB limits (3-512 characters)
    if len(collection_name) > 512:
        # Truncate but keep meaningful parts
        max_session_length = 512 - len("agent_conversations_")
        sanitized_session_id = sanitized_session_id[:max_session_length]
        collection_name = f"agent_conversations_{sanitized_session_id}"
    
    try:
        collection = chroma_client.get_or_create_collection(
            name=collection_name,
            metadata={
                "type": "agent_conversation",
                "session_id": session_id,  # Keep original session_id in metadata
                "sanitized_session_id": sanitized_session_id,
                "description": "Stores conversation history between agents and users",
                "hnsw:space": "cosine"  # Use same settings as forecast collection
            }
        )
        print(f"💬 Using conversation collection: {collection_name}")
        try:
            count = collection.count()
            print(f"📊 Collection contains {count} messages")
        except Exception as e:
            print(f"⚠️ Error getting collection count: {e}")
        return collection
    except Exception as e:
        print(f"❌ Error creating conversation collection: {e}")
        print(f"❌ Failed collection name: {collection_name}")
        return None

def create_agents():
    """Create and configure agents with async support and function mapping"""
    agents = []
    
    # Create agents with their respective prompts and function maps
    orchestrator = orchestrator_agent.create_agent()
    
    # Create fetch forecast agent
    fetch_forecast = fetch_forecasting_agent.create_agent()
    
    # Create data analyst agent
    data_analyst = forecasting_data_analyst_agent.create_agent()
    
    # Create visualization agent
    visualizer = data_visualization_agent.create_agent()
    
    # Create KPI agent
    kpi = kpi_agent.create_agent()
    
    # Create workforce simulation agent
    workforce_simulation = workforce_simulation_agent.create_agent()
    
    # Add agents in order (orchestrator first)
    agents = [orchestrator, fetch_forecast, data_analyst, visualizer, kpi, workforce_simulation]
    
    # Add async support to each agent
    for agent in agents:
        print(f"🤖 Created agent: {agent.name}")
        print(f"Agent config: {agent.llm_config}")
        if hasattr(agent, 'function_map'):
            print(f"Agent functions: {list(agent.function_map.keys())}")
        
        if not hasattr(agent, 'a_generate_reply'):
            print(f"Adding async support to {agent.name}")
            async def a_generate_reply(self, messages=None, sender=None, config=None):
                print(f"Async generate called for {self.name}")
                result = self.generate_reply(messages=messages, sender=sender, config=config)
                print(f"Async generate result: {result}")
                return result
            agent.a_generate_reply = a_generate_reply.__get__(agent)
    
    return agents

def set_agent_data_store_context(agents, session_id):
    """Set the vector data store context for all agents that need it"""
    data_store = get_session_vector_data_store()
    
    # Set context for fetch forecasting agent
    try:
        fetch_forecasting_agent.set_data_store_context(data_store, session_id)
        print(f"✅ Set data store context for fetch forecasting agent: {session_id}")
    except Exception as e:
        print(f"⚠️ Failed to set data store context for fetch agent: {e}")
    
    # Set context for KPI agent
    try:
        kpi_agent.set_data_store_context(data_store, session_id)
        print(f"✅ Set data store context for KPI agent: {session_id}")
    except Exception as e:
        print(f"⚠️ Failed to set data store context for KPI agent: {e}")
    
    return data_store

def get_chainlit_author_from_role(role):
    mapping = {
        "user": "You",
        "assistant": "Assistant",
        "Orchestrator-Agent": "🎯 Orchestrator",
        "Fetch-Volume-Forecast-Agent": "📊 Forecast Agent",
        "Forecasting-Data-Analyst-Agent": "📈 Data Analyst",
        "Data-Visualization-Agent": "📊 Visualization Agent",
        "KPI-Data-Agent": "📋 KPI Agent",
        "Workforce-Simulation-Agent": "🎮 Simulation Agent",
        "human": "You",
        "system": "System"
    }
    return mapping.get(role, role)

class TeamsHumanAgent(ConversableAgent):
    """Teams-optimized Human Agent that doesn't block for interactive input"""
    
    def __init__(self, session_id):
        super().__init__(
            name="human",
            human_input_mode="NEVER",  # Teams doesn't support blocking input
            llm_config=False,
            code_execution_config=False,
            max_consecutive_auto_reply=0
        )
        self._session_id = session_id
    
    async def get_human_input(self, prompt: str) -> str:
        """Return empty string for Teams mode (non-blocking)"""
        print("🔄 Teams mode: Non-blocking human input")
        return ""

class GroupChat:
    def __init__(self, agents, user_agent, session_id="default"):
        self.agents = agents
        self.orchestrator = next(a for a in agents if a.name == "Orchestrator-Agent")
        self.user_agent = user_agent
        self.session_id = session_id
        self.messages = []
        self.message_hashes = set()
        self.last_speaker = None
        self.current_agent = None
        
        # Get session data for persistent context
        self.session_data = teams_session_manager.sessions.get(session_id, {})
        self.current_context = self.session_data.get("context", {
            "teams": [],
            "last_query": None,
            "current_comparison": None,
            "visualizations": []
        })
        
        # Initialize ChromaDB collection for this session
        self.collection = get_conversation_collection(session_id)
        
        # 📊 SET UP VECTOR DATA STORE CONTEXT FOR AGENTS
        self.vector_data_store = set_agent_data_store_context(agents, session_id)
        
        # Load existing context from ChromaDB
        self._load_existing_context()
    
    def _load_existing_context(self):
        """Load existing context from ChromaDB at initialization"""
        # 🔧 CRITICAL FIX: Check if we have a valid collection first
        if not self.collection:
            print("📚 No collection available - starting with clean context")
            return
            
        try:
            # Quick check if collection exists and has data
            test_results = self.collection.get(limit=1)
            if not test_results or not test_results.get('documents'):
                print("📚 No existing context found - starting with clean context")
                return
        except Exception as e:
            print(f"📚 Error checking collection - starting with clean context: {e}")
            return
            
        # Only proceed if we have valid data
        context = self._get_recent_context()
        if context:
            print("📚 Loaded existing context from ChromaDB")
            # Parse context to update current_context
            self._parse_context_for_teams(context)
        else:
            print("📚 No valid context found - starting with clean context")
    
    def _parse_context_for_teams(self, context):
        """Parse context string to extract team information"""
        if not context:
            return
            
        # Look for team information in the context
        lines = context.split("\n")
        for line in lines:
            line = line.lower()
            if "business:" in line and "substream:" in line and "team:" in line:
                try:
                    business = line.split("business:")[1].split()[0].strip()
                    substream = line.split("substream:")[1].split()[0].strip()
                    team = line.split("team:")[1].split()[0].strip()
                    team_info = {"business": business, "substream": substream, "team": team}
                    if team_info not in self.current_context["teams"]:
                        self.current_context["teams"].append(team_info)
                        print(f"Added team to context: {team_info}")
                except Exception as e:
                    print(f"Error parsing team info: {e}")
            
            # Look for comparison mode
            if "comparing" in line or "compare" in line:
                self.current_context["current_comparison"] = True
    
    async def _store_message_in_chromadb(self, message, author):
        """Store message in ChromaDB with metadata - ENHANCED for proper ordering"""
        if not self.collection:
            print("⚠️ No conversation collection available")
            return
            
        try:
            # Create unique ID with microsecond precision for proper ordering
            current_time = datetime.now()
            message_id = f"conv_{self.session_id}_{current_time.strftime('%Y%m%d_%H%M%S_%f')}"
            
            # Prepare metadata with enhanced ordering
            metadata = {
                "timestamp": current_time.isoformat(),
                "timestamp_sort": current_time.timestamp(),  # Numeric timestamp for sorting
                "author": author,
                "role": message.get("role", "unknown"),
                "session_id": self.session_id,
                "type": "conversation_message",
                "message_index": len(self.messages)  # Sequential index for guaranteed order
            }
            
            # Add current context to metadata
            metadata.update({
                "teams": str(self.current_context["teams"]),
                "comparison_mode": str(self.current_context["current_comparison"]),
                "last_query": str(self.current_context["last_query"])
            })
            
            # Clean content for ChromaDB
            content = message.get("content", "")
            if isinstance(content, str):
                content = content.replace('\x00', '').strip()
            
            if not content:
                print("⚠️ Skipping empty content for ChromaDB")
                return
            
            # Store message content and metadata
            self.collection.add(
                ids=[message_id],
                documents=[content],
                metadatas=[metadata]
            )
            
            print(f"💾 Stored conversation message in ChromaDB: {message_id} (Index: {metadata['message_index']})")
            
        except Exception as e:
            print(f"❌ Error storing message in ChromaDB: {e}")
            import traceback
            print(traceback.format_exc())
    
    def _get_recent_context(self, limit=10):
        """Retrieve recent conversation context from ChromaDB - ENHANCED ORDERING"""
        if not self.collection:
            print("⚠️ No conversation collection available")
            return None
            
        try:
            # Query MORE messages to ensure we get everything for proper sorting
            results = self.collection.get(
                limit=limit * 5,  # Get more messages to sort properly
                where={
                    "$and": [
                        {"session_id": {"$eq": self.session_id}},
                        {"type": {"$eq": "conversation_message"}}
                    ]
                }
            )
            
            if not results or not results['documents']:
                return None
            
            # ENHANCED: Create list of messages with multiple ordering options
            messages = []
            for doc, metadata in zip(results['documents'], results['metadatas']):
                # Use multiple ways to ensure proper ordering
                timestamp = datetime.fromisoformat(metadata['timestamp'])
                timestamp_sort = metadata.get('timestamp_sort', timestamp.timestamp())
                message_index = metadata.get('message_index', 0)
                author = metadata['author']
                role = metadata['role']
                
                # CRITICAL FIX: Include ALL important content - forecast data AND KPI requests
                # Only skip truly empty or irrelevant function calls
                if role == "function":
                    # Keep function results that contain forecast data OR KPI data
                    if any(keyword in doc.lower() for keyword in [
                        'forecast:', 'match 1', 'match 2', 'match 3', 
                        '2025-', '2026-', 'business:', 'team:', 'logistics',
                        'kpi results', 'attrition rate', 'home loan', 'department:'
                    ]):
                        # This is real data - KEEP IT
                        pass
                    else:
                        # Skip empty or irrelevant function calls
                        continue
                
                # CRITICAL: Keep all user messages and agent responses for context continuity
                # This ensures agents understand what the user is asking about
                
                # Format message with multiple ordering keys
                messages.append({
                    'timestamp': timestamp,
                    'timestamp_sort': timestamp_sort,
                    'message_index': message_index,
                    'author': author,
                    'role': role,
                    'content': doc[:500] if len(doc) > 500 else doc  # Limit length but keep more
                })
            
            # ENHANCED SORTING: Use multiple keys to ensure perfect chronological order
            # Primary: message_index (sequential), Secondary: timestamp_sort (numeric), Tertiary: timestamp (datetime)
            messages.sort(key=lambda x: (x['message_index'], x['timestamp_sort'], x['timestamp']))
            
            # Format conversation history with clear separation and better context
            formatted_history = ["=== CHRONOLOGICAL CONVERSATION CONTEXT ==="]
            formatted_history.append("(Ordered from earliest to most recent)")
            
            # Take the most recent messages (after perfect sorting)
            recent_messages = messages[-limit:] if len(messages) > limit else messages
            
            for i, msg in enumerate(recent_messages):
                timestamp_str = msg['timestamp'].strftime('%H:%M:%S')
                author = msg['author']
                content = msg['content']
                
                # Add more context about what type of request this was
                if 'kpi' in content.lower() or 'attrition' in content.lower():
                    content_indicator = "[KPI REQUEST]"
                elif 'forecast' in content.lower():
                    content_indicator = "[FORECAST REQUEST]"
                elif 'json' in content.lower():
                    content_indicator = "[FORMAT REQUEST]"
                elif any(period in content.lower() for period in ['last month', 'last 4 months', 'last year']):
                    content_indicator = "[TIME PERIOD]"
                elif 'chart' in content.lower() or 'plot' in content.lower() or 'visualize' in content.lower():
                    content_indicator = "[VISUALIZATION REQUEST]"
                else:
                    content_indicator = ""
                
                # Add sequence number for clarity
                formatted_history.append(f"[{i+1}] [{timestamp_str}] {author}: {content_indicator} {content}")
            
            context_text = "\n".join(formatted_history)
            print(f"📚 Context retrieved ({len(recent_messages)} messages) in perfect chronological order")
            print(f"📚 Context preview: {context_text[:400]}...")
            return context_text
            
        except Exception as e:
            print(f"⚠️ Error retrieving context from ChromaDB: {e}")
            import traceback
            print(f"⚠️ Context error traceback: {traceback.format_exc()}")
            return None
    
    def _hash_message(self, message, author):
        """Create a unique hash for a message"""
        content = message.get("content", "").strip()
        return f"{author}:{content}"
    
    async def send_message(self, message, author=None):
        """Send a message to the UI and store it - Teams optimized"""
        try:
            if get_chainlit_author_from_role(author) == 'You':
                # Don't show user messages on the UI
                clean_message = message.copy() if isinstance(message, dict) else {"role": "user", "content": str(message)}
            else:
                print("\n🔄 Message Handler - Starting message processing")
                print(f"Debug - Message type: {type(message)}")
                print(f"Debug - Message content type: {type(message.get('content', ''))}")
                print(f"Debug - Author: {author}")
                
                # Clean the message
                clean_message = message.copy() if isinstance(message, dict) else {"role": "user", "content": str(message)}
                print(f"Debug - Cleaned message: {clean_message}")
                
                # Handle function results with improved error handling
                if message.get("role") == "function":
                    print("🔧 Processing function result")
                    try:
                        content = message.get("content", "")
                        print(f"Debug - Function content: {content[:200]}...")  # First 200 chars
                        
                        if isinstance(content, str):
                            try:
                                # Try to parse as JSON first
                                try:
                                    data = json.loads(content)
                                    print("✅ Successfully parsed content as JSON")
                                except json.JSONDecodeError:
                                    # 🔧 TRY PYTHON DICT PARSING (for visualization agent results)
                                    try:
                                        # Check if it looks like a Python dict
                                        if content.strip().startswith('{') and content.strip().endswith('}'):
                                            # Safe evaluation for dict strings
                                            import ast
                                            data = ast.literal_eval(content)
                                            print("✅ Successfully parsed content as Python dict")
                                        else:
                                            raise ValueError("Not a dict format")
                                    except (ValueError, SyntaxError):
                                        # 🔧 SAFER APPROACH: Don't use eval() for function results
                                        # For KPI and other function results, treat as regular text
                                        print("✅ Treating content as regular text (not JSON/dict)")
                                        data = {"text_content": content}
                                
                                print("Debug - Author: ", get_chainlit_author_from_role(author))
                                if isinstance(data, dict):
                                    print(f"Debug - Data keys: {data.keys()}")
                                    
                                    # Check for visualization data
                                    if get_chainlit_author_from_role(author) == '📊 Visualization Agent':
                                        print("📊 Found visualization data")
                                        
                                        try:
                                            spec_data = data.get('spec', {})
                                            if not spec_data:
                                                raise ValueError("No spec data found in visualization result")
                                            
                                            print("🎨 Converting Plotly chart to image for Teams...")
                                            
                                            # ✅ CREATE ACTUAL PLOTLY CHART IMAGE
                                            try:
                                                import plotly.graph_objects as go
                                                import plotly.io as pio
                                                import io
                                                import base64
                                                
                                                # Create figure from spec
                                                fig = go.Figure()
                                                
                                                # Add traces from spec
                                                for trace_data in spec_data.get('data', []):
                                                    fig.add_trace(go.Scatter(
                                                        x=trace_data.get('x', []),
                                                        y=trace_data.get('y', []),
                                                        mode=trace_data.get('mode', 'lines+markers'),
                                                        name=trace_data.get('name', 'Data'),
                                                        line=trace_data.get('line', {}),
                                                        marker=trace_data.get('marker', {})
                                                    ))
                                                
                                                # Apply layout from spec
                                                layout = spec_data.get('layout', {})
                                                fig.update_layout(
                                                    title=layout.get('title', {}).get('text', 'Chart'),
                                                    xaxis_title=layout.get('xaxis', {}).get('title', 'X-axis'),
                                                    yaxis_title=layout.get('yaxis', {}).get('title', 'Y-axis'),
                                                    width=800,
                                                    height=500,
                                                    plot_bgcolor='white',
                                                    paper_bgcolor='white'
                                                )
                                                
                                                # Convert to image bytes using kaleido
                                                print("🖼️ Converting Plotly to PNG image...")
                                                img_bytes = pio.to_image(fig, format='png', width=800, height=500)
                                                
                                                # Create a file-like object
                                                img_io = io.BytesIO(img_bytes)
                                                img_io.seek(0)
                                                
                                                # Send as Chainlit Image
                                                chart_image = cl.Image(
                                                    content=img_bytes,
                                                    name="forecast_chart.png",
                                                    display="inline"
                                                )
                                                
                                                await cl.Message(
                                                    content="📊 **Forecast Chart**",
                                                    elements=[chart_image],
                                                    author=get_chainlit_author_from_role(author)
                                                ).send()
                                                
                                                print("✅ Successfully sent chart image to Teams!")
                                                return  # Don't process as regular message
                                                
                                            except Exception as plot_error:
                                                print(f"❌ Plotly image conversion failed: {plot_error}")
                                                import traceback
                                                print(f"❌ Plot traceback: {traceback.format_exc()}")
                                                
                                                # Fallback to enhanced text visualization
                                                print("⚠️ Falling back to text visualization...")
                                                # ✅ TEAMS FIX: Use simpler text-based visualization instead of base64 images
                                                # This avoids the "Unknown attachment type" error in Teams
                                                spec_layout = spec_data.get('layout', {})
                                                chart_title = spec_layout.get('title', {}).get('text', 'Data Visualization')
                                                
                                                # Extract data from the chart spec
                                                chart_data_list = spec_data.get('data', [])
                                                if chart_data_list:
                                                    chart_data = chart_data_list[0]  
                                                    x_values = chart_data.get('x', [])
                                                    y_values = chart_data.get('y', [])
                                                    
                                                    if x_values and y_values:
                                                        # Create enhanced text visualization
                                                        chart_message = f"""📈 **{chart_title}**
                                                        
🔢 **Data Summary:**
• **Total Data Points**: {len(x_values)}
• **Highest Value**: {max(y_values):,}
• **Lowest Value**: {min(y_values):,}  
• **Average**: {sum(y_values)/len(y_values):,.0f}

📊 **Data Table** (First 8 points):
```
Date          | Value
--------------|--------"""
                                                        
                                                        # Add first 8 data points
                                                        for i, (x, y) in enumerate(zip(x_values[:8], y_values[:8])):
                                                            chart_message += f"\n{str(x):12} | {y:,.0f}"
                                                        
                                                        if len(x_values) > 8:
                                                            chart_message += f"\n...           | ..."
                                                            chart_message += f"\n({len(x_values)} total points)"
                                                        
                                                        chart_message += "```\n"
                                                        
                                                        # Add simple ASCII trend visualization
                                                        if len(y_values) > 1:
                                                            trend = "📈 Upward" if y_values[-1] > y_values[0] else "📉 Downward" if y_values[-1] < y_values[0] else "➡️ Stable"
                                                            variance = (max(y_values) - min(y_values)) / (sum(y_values)/len(y_values)) * 100
                                                            
                                                            chart_message += f"\n📊 **Trend Analysis:**\n"
                                                            chart_message += f"• **Overall Trend**: {trend}\n"
                                                            chart_message += f"• **Volatility**: {variance:.1f}% variance from average\n"
                                                            
                                                            # Simple text sparkline
                                                            chart_message += f"• **Pattern**: "
                                                            normalized = [(y - min(y_values)) / (max(y_values) - min(y_values)) if max(y_values) != min(y_values) else 0 for y in y_values[:12]]
                                                            sparkline = "".join(["▁" if v < 0.2 else "▃" if v < 0.4 else "▅" if v < 0.6 else "▇" if v < 0.8 else "█" for v in normalized])
                                                            chart_message += sparkline
                                                        
                                                        # Send the enhanced text visualization
                                                        await cl.Message(
                                                            content=chart_message,
                                                            author=get_chainlit_author_from_role(author)
                                                        ).send()
                                                        
                                                        print("✅ Successfully sent chart as text visualization to Teams")
                                                        return  # Don't process as regular message
                                                
                                        except Exception as viz_error:
                                            print(f"❌ Error creating text chart: {viz_error}")
                                            import traceback
                                            print(f"❌ Viz traceback: {traceback.format_exc()}")
                                            
                                            # Send error message and fall through to regular processing
                                            error_msg = f"""⚠️ **Chart Generation Error**

{str(viz_error)}

Displaying raw data instead."""
                                            
                                            await cl.Message(
                                                content=error_msg,
                                                author=get_chainlit_author_from_role(author)
                                            ).send()
                                            
                                            # Continue to regular message processing
                                            return  # Exit early after sending error message
                        
                            except (json.JSONDecodeError, SyntaxError, ValueError) as e:
                                print(f"⚠️ Content parsing error: {e}")
                                # Continue with original content
                        
                        # If not a visualization, send as regular function result with Teams formatting
                        print("📤 Sending regular function result")
                        formatted_content = f"**{get_chainlit_author_from_role(author)}**\n\n{content}"
                        await cl.Message(
                            content=formatted_content,
                            author=get_chainlit_author_from_role(author)
                        ).send()
                        
                    except Exception as e:
                        print(f"❌ Error handling function result: {e}")
                        import traceback
                        print(f"Debug - Traceback: {traceback.format_exc()}")
                        # Send error message with Teams formatting
                        error_content = f"⚠️ **Error processing result**: {str(e)}"
                        await cl.Message(
                            content=error_content,
                            author=get_chainlit_author_from_role(author)
                        ).send()
                else:
                    # Regular message with Teams formatting
                    print("📤 Sending regular message")
                    formatted_content = f"**{get_chainlit_author_from_role(author)}**\n\n{clean_message['content']}"
                    await cl.Message(
                        content=formatted_content,
                        author=get_chainlit_author_from_role(author or clean_message["role"])
                    ).send()
            
            # Store message and hash
            self.messages.append(clean_message)
            
            # Store in ChromaDB
            await self._store_message_in_chromadb(clean_message, author)
            
        except Exception as e:
            print(f"❌ Error in send_message: {str(e)}")
            import traceback
            print(f"Debug - Traceback: {traceback.format_exc()}")
            await cl.Message(f"⚠️ Error sending message: {str(e)}").send()
    
    async def _execute_function(self, agent, function_call):
        """Execute a function and return its result"""
        try:
            if not hasattr(agent, "function_map"):
                print("Debug - No function map found on agent")
                return None
                
            func_name = function_call.get("name")
            if not func_name in agent.function_map:
                print(f"Debug - Function {func_name} not found in function map")
                return None
                
            func = agent.function_map[func_name]
            args = function_call.get("arguments", "")
            
            print(f"⚙️ Executing function {func_name} with args: {args}")
            result = func(args)
            print(f"Debug - Function result: {result}")
            
            # Format the result in a more readable way
            if isinstance(result, dict):
                if 'results' in result:
                    return {
                        "role": "function",
                        "name": func_name,
                        "content": str(result['results'])
                    }
                elif 'error' in result:
                    return {
                        "role": "function",
                        "name": func_name,
                        "content": f"Error: {result['error']}"
                    }
            
            return {
                "role": "function",
                "name": func_name,
                "content": str(result)
            }
        except Exception as e:
            print(f"❌ Error executing function: {e}")
            import traceback
            print(traceback.format_exc())
            return None
    
    async def run_chat(self, initial_message):
        """Modified to use orchestrator-based routing - Teams optimized"""
        try:
            # Always start with the orchestrator
            self.current_agent = self.orchestrator
            
            # Format initial message correctly
            initial_msg = {"role": "user", "content": initial_message}
            await self.send_message(initial_msg, "You")
            
            # Send initial message to orchestrator
            response = await self._get_agent_reply(
                self.orchestrator,
                [initial_msg]
            )
            
            if response:
                # Send orchestrator's response to UI
                await self.send_message(response, self.orchestrator.name)
                
                # Check for agent delegation patterns (same as original)
                content = response.get("content", "").lower()
                
                # IMPROVED: Only delegate on explicit instruction format, not casual mentions
                explicit_delegation = False
                
                if ("fetch-volume-forecast-agent:" in content.lower() or 
                    "[fetch-volume-forecast-agent]" in content.lower() or
                    content.lower().startswith("fetch-volume-forecast-agent")):
                    explicit_delegation = True
                    # Delegate to Fetch-Volume-Forecast-Agent
                    fetch_agent = next(a for a in self.agents if a.name == "Fetch-Volume-Forecast-Agent")
                    self.current_agent = fetch_agent
                    fetch_response = await self._get_agent_reply(
                        fetch_agent,
                        self.messages
                    )
                    if fetch_response:
                        await self.send_message(fetch_response, fetch_agent.name)
                        
                elif ("data-visualization-agent:" in content.lower() or 
                      "[data-visualization-agent]" in content.lower() or
                      content.lower().startswith("data-visualization-agent")):
                    explicit_delegation = True
                    
                    # 🎯 CRITICAL FIX: Check for explicit data in orchestrator's delegation message FIRST
                    print("🎨 AUDIT - INTERCEPTING VISUALIZATION DELEGATION:")
                    print("   🔍 Checking for explicit data in delegation message...")
                    
                    # Extract the orchestrator's delegation content
                    delegation_content = response.get("content", "").lower()
                    print(f"🎯 DELEGATION CONTENT: {delegation_content}")
                    
                    # 📊 PATTERN 1: Check for explicit KPI data in delegation message
                    kpi_pattern_found = False
                    if any(kpi_word in delegation_content for kpi_word in ["kpi", "attrition", "rate", "percentage", "%"]):
                        print("🔍 AUDIT - Found KPI-related keywords in delegation")
                        
                        # Extract KPI data from the delegation message
                        import re
                        # Look for patterns like "January 2025 (9.92%)", "February 2025 (6.81%)", etc.
                        # ENHANCED: Also look for "January 2025: 9.92%" or "9.92%" anywhere
                        kpi_pattern = r'(\w+ \d{4})\s*[\(:]*([0-9.]+)%?[\)]*'
                        kpi_matches = re.findall(kpi_pattern, response.get("content", ""))  # Use original response content, not lowercase
                        
                        print(f"🔍 AUDIT - Testing KPI pattern on: '{response.get('content', '')[:200]}...'")
                        print(f"🔍 AUDIT - KPI matches found: {kpi_matches}")
                        
                        if kpi_matches:
                            print(f"✅ AUDIT - Found {len(kpi_matches)} KPI data points in delegation:")
                            
                            # Create visualization data from extracted KPI points
                            kpi_chart_data = []
                            for month_year, value in kpi_matches:
                                kpi_chart_data.append({
                                    "date": month_year,
                                    "value": float(value),
                                    "metric": "Home Loan Attrition Rate"
                                })
                                print(f"   📊 {month_year}: {value}%")
                            
                            if len(kpi_chart_data) >= 2:  # Need at least 2 points for a chart
                                kpi_pattern_found = True
                                
                                # Create visualization JSON for KPI data
                                viz_data = {
                                    "data_type": "kpi",
                                    "kpi_data": kpi_chart_data,
                                    "title": "Home Loan Attrition Rate - Monthly Trend",
                                    "departments": ["Home Loan"]
                                }
                                
                                import json
                                json_data = json.dumps(viz_data)
                                
                                print(f"📊 AUDIT - KPI VISUALIZATION DATA CREATED FROM DELEGATION:")
                                print(f"   📦 JSON size: {len(json_data)} characters")
                                print(f"   📊 Data points: {len(kpi_chart_data)}")
                                print(f"   📋 Preview: {json_data[:200]}...")
                                
                                # Call visualization function directly with delegation data
                                viz_agent = next(a for a in self.agents if a.name == "Data-Visualization-Agent")
                                
                                if hasattr(viz_agent, "function_map") and "create_visualization" in viz_agent.function_map:
                                    print(f"🎨 AUDIT - CALLING VISUALIZATION WITH DELEGATION DATA")
                                    
                                    viz_func = viz_agent.function_map["create_visualization"]
                                    viz_result = viz_func(json_data)
                                    
                                    print(f"✅ AUDIT - DELEGATION DATA VISUALIZATION RESULT:")
                                    print(f"   📊 Result type: {type(viz_result)}")
                                    print(f"   📋 Result preview: {str(viz_result)[:200]}...")
                                    
                                    viz_response = {
                                        "role": "function",
                                        "name": "create_visualization",
                                        "content": str(viz_result)
                                    }
                                    
                                    await self.send_message(viz_response, viz_agent.name)
                                    print("✅ AUDIT - Successfully created visualization from delegation data!")
                                    return  # Exit after handling delegation data
                                else:
                                    print("❌ AUDIT - Visualization function not found in function_map")
                            else:
                                print(f"⚠️ AUDIT - Not enough KPI data points: {len(kpi_chart_data)}")
                        else:
                            print("⚠️ AUDIT - No KPI matches found with regex pattern")
                    
                    # 📊 PATTERN 2: Check for explicit forecast data in delegation message
                    if not kpi_pattern_found:
                        # Look for forecast patterns like "2025-01: 450, 2025-02: 520"
                        forecast_pattern = r'(\d{4}-\d{2})[:\s]*([0-9,]+)'
                        forecast_matches = re.findall(forecast_pattern, delegation_content)
                        
                        if forecast_matches:
                            print(f"✅ AUDIT - Found {len(forecast_matches)} forecast data points in delegation")
                            
                            forecast_chart_data = []
                            for date, value in forecast_matches:
                                # Clean up value (remove commas)
                                clean_value = value.replace(',', '')
                                if clean_value.isdigit():
                                    forecast_chart_data.append({
                                        "date": date,
                                        "value": int(clean_value)
                                    })
                            
                            if len(forecast_chart_data) >= 2:
                                viz_data = {
                                    "data_type": "forecast",
                                    "forecast_data": forecast_chart_data,
                                    "title": "Forecast Data from Delegation"
                                }
                                
                                import json
                                json_data = json.dumps(viz_data)
                                
                                # Call visualization function
                                viz_agent = next(a for a in self.agents if a.name == "Data-Visualization-Agent")
                                
                                if hasattr(viz_agent, "function_map") and "create_visualization" in viz_agent.function_map:
                                    viz_func = viz_agent.function_map["create_visualization"]
                                    viz_result = viz_func(json_data)
                                    
                                    viz_response = {
                                        "role": "function",
                                        "name": "create_visualization",
                                        "content": str(viz_result)
                                    }
                                    
                                    await self.send_message(viz_response, viz_agent.name)
                                    print("✅ AUDIT - Successfully created forecast visualization from delegation data!")
                                    return
                    
                    # 🔄 FALLBACK: If no explicit data found in delegation, use vector data store logic
                    if not kpi_pattern_found:
                        print("🔍 AUDIT - No explicit data in delegation, falling back to vector data store logic")
                        
                    # Delegate to Data-Visualization-Agent with INTELLIGENT QUERY
                    print("🎨 AUDIT - INTERCEPTING VISUALIZATION DELEGATION:")
                    print("   🧠 Using intelligent vector data store query with enhanced audit logging")
                    
                    # 🧠 PARSE USER INTENT FROM RECENT MESSAGES
                    user_intent = self._parse_visualization_intent(self.messages[-5:])  # Check last 5 messages
                    
                    print(f"🧠 AUDIT - PARSED USER INTENT:")
                    print(f"   🔄 Comparison Mode: {user_intent.get('comparison_mode', False)}")
                    print(f"   🏢 Business: {user_intent.get('business', 'NOT_SPECIFIED')}")
                    print(f"   🌊 Substream: {user_intent.get('substream', 'NOT_SPECIFIED')}")
                    print(f"   👥 Team: {user_intent.get('team', 'NOT_SPECIFIED')}")
                    print(f"   📊 Datasets: {user_intent.get('datasets', [])}")
                    
                    # 🔄 COMPARISON MODE HANDLING
                    if user_intent.get("comparison_mode"):
                        print("🔄 AUDIT - COMPARISON MODE ACTIVATED")
                        
                        datasets = []
                        dataset_criteria_list = user_intent.get("datasets", [])
                        
                        # If no specific datasets specified, get last 2 different entries
                        if not dataset_criteria_list:
                            print("🔍 AUDIT - No specific datasets, using recent different entries")
                            all_recent = self.vector_data_store.get_latest_results(
                                session_id=self.session_id,
                                query_type="forecast",
                                limit=10
                            )
                            
                            # Group by unique combinations and take 2 most recent
                            unique_combos = {}
                            for result in all_recent:
                                combo_key = f"{result['business']}-{result['substream']}-{result['team']}"
                                if combo_key not in unique_combos:
                                    unique_combos[combo_key] = result
                            
                            if len(unique_combos) >= 2:
                                dataset_criteria_list = [
                                    {"business": r['business'], "substream": r['substream'], "team": r['team']}
                                    for r in list(unique_combos.values())[:2]
                                ]
                                print(f"🔍 AUDIT - Auto-selected datasets: {dataset_criteria_list}")
                        
                        # Retrieve each dataset
                        for i, criteria in enumerate(dataset_criteria_list):
                            print(f"🔍 AUDIT - Retrieving dataset {i+1}: {criteria}")
                            matching_data = self.vector_data_store.get_latest_results(
                                session_id=self.session_id,
                                query_type="forecast",
                                business=criteria.get('business'),
                                substream=criteria.get('substream'),
                                team=criteria.get('team'),
                                limit=1
                            )
                            
                            if matching_data:
                                result = matching_data[0]
                                label = f"{result['business']}-{result['substream']}-{result['team']}"
                                datasets.append({
                                    "label": label,
                                    "data": result['result_data'],
                                    "metadata": {
                                        "business": result['business'],
                                        "substream": result['substream'],
                                        "team": result['team'],
                                        "timestamp": result['timestamp'].strftime('%H:%M:%S')
                                    }
                                })
                                print(f"✅ AUDIT - Added dataset {i+1}: {label}")
                            else:
                                print(f"❌ AUDIT - No data found for dataset {i+1}: {criteria}")
                        
                        if len(datasets) >= 2:
                            print(f"🎯 AUDIT - COMPARISON DATA READY: {len(datasets)} datasets")
                            
                            # Parse each dataset and create comparison visualization
                            comparison_data = []
                            for dataset in datasets:
                                print(f"🔄 AUDIT - Parsing dataset: {dataset['label']}")
                                parsed_points = self._parse_vector_search_data(dataset['data'])
                                if parsed_points:
                                    comparison_data.append({
                                        "label": dataset['label'],
                                        "points": parsed_points,
                                        "metadata": dataset['metadata']
                                    })
                                    print(f"✅ AUDIT - Parsed {len(parsed_points)} points for {dataset['label']}")
                            
                            if len(comparison_data) >= 2:
                                # Create comparison visualization JSON
                                viz_data = {
                                    "comparison_mode": True,
                                    "datasets": comparison_data,
                                    "chart_type": "multi_series_comparison"
                                }
                                
                                import json
                                json_data = json.dumps(viz_data)
                                
                                print(f"📊 AUDIT - COMPARISON VISUALIZATION DATA CREATED:")
                                print(f"   📦 JSON size: {len(json_data)} characters")
                                print(f"   📊 Datasets: {len(comparison_data)}")
                                print(f"   📋 Labels: {[d['label'] for d in comparison_data]}")
                                
                                # Call visualization function
                                viz_agent = next(a for a in self.agents if a.name == "Data-Visualization-Agent")
                                
                                if hasattr(viz_agent, "function_map") and "create_visualization" in viz_agent.function_map:
                                    print(f"🎨 AUDIT - CALLING COMPARISON VISUALIZATION FUNCTION")
                                    
                                    viz_func = viz_agent.function_map["create_visualization"]
                                    viz_result = viz_func(json_data)
                                    
                                    print(f"✅ AUDIT - COMPARISON VISUALIZATION RESULT:")
                                    print(f"   📊 Result type: {type(viz_result)}")
                                    print(f"   📋 Result preview: {str(viz_result)[:200]}...")
                                    
                                    viz_response = {
                                        "role": "function",
                                        "name": "create_visualization", 
                                        "content": str(viz_result)
                                    }
                                    
                                    await self.send_message(viz_response, viz_agent.name)
                                    print("✅ AUDIT - Successfully created comparison visualization!")
                                    return  # Exit after handling comparison
                            else:
                                print("❌ AUDIT - Insufficient parsed comparison data")
                        else:
                            print(f"❌ AUDIT - Insufficient datasets for comparison: {len(datasets)}")
                    
                    # 🎯 SINGLE DATASET MODE (EXISTING LOGIC)
                    else:
                        print("🎯 AUDIT - SINGLE DATASET MODE")
                        
                        # 🔍 ENHANCED: Try different data types based on context
                        matching_data = None
                        data_type = "unknown"
                        
                        # First try forecast data
                        forecast_data = self.vector_data_store.get_latest_results(
                            session_id=self.session_id,
                            query_type="forecast",
                            business=user_intent.get('business'),
                            substream=user_intent.get('substream'),
                            team=user_intent.get('team'),
                            limit=5
                        )
                        
                        # Then try KPI data
                        kpi_data = self.vector_data_store.get_latest_results(
                            session_id=self.session_id,
                            query_type="kpi",
                            limit=5
                        )
                        
                        print(f"🔍 AUDIT - DATA SEARCH RESULTS:")
                        print(f"   📊 Forecast data: {len(forecast_data)} entries")
                        print(f"   📋 KPI data: {len(kpi_data)} entries")
                        
                        # 📊 DETAILED LOGGING: Show what's available in vector data store
                        if forecast_data:
                            print(f"\n📊 AUDIT - AVAILABLE FORECAST DATA:")
                            for i, entry in enumerate(forecast_data[:3], 1):  # Show first 3 entries
                                print(f"   [{i}] {entry['business']}-{entry['substream']}-{entry['team']}")
                                print(f"       📅 Timestamp: {entry['timestamp'].strftime('%Y-%m-%d %H:%M:%S')}")
                                print(f"       📦 Data size: {len(str(entry['result_data']))} chars")
                                print(f"       📋 Data preview: '{str(entry['result_data'])[:100]}...'")
                                print(f"       🆔 Entry ID: {entry['entry_id']}")
                            if len(forecast_data) > 3:
                                print(f"   ... and {len(forecast_data) - 3} more forecast entries")
                        
                        if kpi_data:
                            print(f"\n📋 AUDIT - AVAILABLE KPI DATA:")
                            for i, entry in enumerate(kpi_data[:3], 1):  # Show first 3 entries
                                print(f"   [{i}] {entry.get('business', 'multiple')} departments")
                                print(f"       📅 Timestamp: {entry['timestamp'].strftime('%Y-%m-%d %H:%M:%S')}")
                                print(f"       📦 Data size: {len(str(entry['result_data']))} chars")
                                print(f"       📋 Data preview: '{str(entry['result_data'])[:100]}...'")
                                print(f"       🆔 Entry ID: {entry['entry_id']}")
                            if len(kpi_data) > 3:
                                print(f"   ... and {len(kpi_data) - 3} more KPI entries")
                        
                        # Prioritize data based on recency and relevance
                        if forecast_data:
                            matching_data = forecast_data
                            data_type = "forecast"
                            print("✅ AUDIT - Using forecast data for visualization")
                        elif kpi_data:
                            matching_data = kpi_data
                            data_type = "kpi"
                            print("✅ AUDIT - Using KPI data for visualization")
                        
                        if not matching_data:
                            print("❌ AUDIT - NO MATCHING DATA FOUND:")
                            print("   📊 Vector data store query returned empty results for both forecast and KPI data")
                            
                            viz_agent = next(a for a in self.agents if a.name == "Data-Visualization-Agent")
                            
                            # Create helpful error message based on user intent
                            intent_str = ""
                            if any(user_intent.get(k) for k in ['business', 'substream', 'team']):
                                criteria = []
                                if user_intent.get('business'): criteria.append(f"business={user_intent['business']}")
                                if user_intent.get('substream'): criteria.append(f"substream={user_intent['substream']}")
                                if user_intent.get('team'): criteria.append(f"team={user_intent['team']}")
                                intent_str = f" matching {', '.join(criteria)}" if criteria else ""
                            
                            error_response = {
                                "role": "assistant",
                                "content": f"❌ **Data Not Found**: I couldn't find any forecast or KPI data{intent_str} to visualize. Please first fetch some data using commands like:\n\n• `Fetch-Volume-Forecast-Agent: Get forecast for business-logistics substream-dlt team-support`\n• `KPI-Data-Agent: Get home loan attrition rate last month`\n\nThen I can create a visualization for you."
                            }
                            await self.send_message(error_response, viz_agent.name)
                            return  # Exit early
                        
                        # 🎯 FOUND MATCHING DATA - CREATE SINGLE VISUALIZATION (EXISTING LOGIC)
                        selected_data = matching_data[0]  # Use most recent matching data
                        print(f"✅ AUDIT - FOUND MATCHING DATA:")
                        print(f"   🔧 Data Type: {data_type}")
                        if data_type == "forecast":
                            print(f"   🏆 Selected: {selected_data['business']}-{selected_data['substream']}-{selected_data['team']}")
                        else:
                            print(f"   🏆 Selected: {data_type} data from {selected_data.get('business', 'multiple')} departments")
                        print(f"   📅 Timestamp: {selected_data['timestamp'].strftime('%Y-%m-%d %H:%M:%S')}")
                        print(f"   🆔 Entry ID: {selected_data['entry_id']}")
                        print(f"   📦 Data size: {len(str(selected_data['result_data']))} characters")
                        
                        # 🔍 COMPREHENSIVE DATA STORE CONTENT LOGGING
                        print(f"\n📊 AUDIT - COMPLETE DATA STORE CONTENT:")
                        print(f"   📋 Raw Result Data Type: {type(selected_data['result_data'])}")
                        print(f"   📏 Character Count: {len(str(selected_data['result_data']))}")
                        print(f"   🔤 First 200 chars: '{str(selected_data['result_data'])[:200]}'")
                        print(f"   🔤 Last 100 chars: '{str(selected_data['result_data'])[-100:]}'")
                        
                        # Show line-by-line breakdown
                        if isinstance(selected_data['result_data'], str):
                            lines = selected_data['result_data'].split('\n')
                            print(f"   📄 Total lines: {len(lines)}")
                            print(f"   📝 Line-by-line preview:")
                            for i, line in enumerate(lines[:10], 1):  # Show first 10 lines
                                if line.strip():  # Only show non-empty lines
                                    print(f"      [{i:2d}] '{line}'")
                            if len(lines) > 10:
                                print(f"      ... and {len(lines) - 10} more lines")
                        
                        # Show metadata
                        print(f"   🏷️ Metadata: {selected_data.get('metadata', {})}")
                        print(f"   🕐 Storage timestamp: {selected_data['timestamp']}")
                        print(f"   🔍 Query type: {selected_data['query_type']}")
                        
                        # 🔧 ENHANCED: Data type-specific parsing
                        try:
                            result_data = selected_data['result_data']
                            
                            print(f"🔍 AUDIT - RAW DATA ANALYSIS:")
                            print(f"   📊 Data type: {type(result_data)}")
                            print(f"   📏 Data length: {len(str(result_data))}")
                            print(f"   📋 First 300 chars: {str(result_data)[:300]}...")
                            
                            # 📊 DATA TYPE-SPECIFIC PARSING
                            if data_type == "forecast":
                                print(f"🔄 AUDIT - STARTING FORECAST DATA PARSING:")
                                data_points = self._parse_vector_search_data(result_data)
                                
                                if data_points:
                                    # Create JSON for forecast visualization
                                    viz_data = {
                                        "data_type": "forecast",
                                        "business": selected_data['business'],
                                        "substream": selected_data['substream'],
                                        "team": selected_data['team'],
                                        "forecast_data": data_points
                                    }
                                else:
                                    print("⚠️ AUDIT - NO FORECAST DATA POINTS EXTRACTED")
                                    
                            elif data_type == "kpi":
                                print(f"🔄 AUDIT - STARTING KPI DATA PARSING:")
                                
                                # Handle KPI data format
                                if isinstance(result_data, dict) and 'kpi_results' in result_data:
                                    kpi_results = result_data['kpi_results']
                                    print(f"📊 Found {len(kpi_results)} KPI results")
                                    
                                    # Convert KPI results to chart-friendly format
                                    chart_data = []
                                    for kpi in kpi_results:
                                        chart_data.append({
                                            "metric": kpi['kpi'],
                                            "value": kpi['value'],
                                            "department": kpi['department'],
                                            "date": kpi['date']
                                        })
                                    
                                    viz_data = {
                                        "data_type": "kpi",
                                        "kpi_data": chart_data,
                                        "departments": list(set([kpi['department'] for kpi in kpi_results])),
                                        "title": "KPI Performance Dashboard"
                                    }
                                    data_points = chart_data  # For success check
                                else:
                                    print("⚠️ AUDIT - KPI data format not recognized")
                                    data_points = []
                            else:
                                print(f"⚠️ AUDIT - Unknown data type: {data_type}")
                                data_points = []
                            
                            print(f"📊 AUDIT - PARSING RESULTS:")
                            print(f"   🎯 Total data points extracted: {len(data_points) if data_points else 0}")
                            
                            if data_points:
                                # Log sample of extracted data points
                                sample_size = min(3, len(data_points))
                                print(f"   📋 Sample extracted points:")
                                for i in range(sample_size):
                                    point = data_points[i]
                                    if data_type == "forecast":
                                        print(f"      [{i+1}] {point.get('date', 'NO_DATE')} = {point.get('value', 'NO_VALUE')}")
                                    elif data_type == "kpi":
                                        print(f"      [{i+1}] {point.get('metric', 'NO_METRIC')}: {point.get('value', 'NO_VALUE')}% ({point.get('department', 'NO_DEPT')})")
                                
                                if len(data_points) > sample_size:
                                    print(f"      ... and {len(data_points) - sample_size} more points")
                                
                                import json
                                json_data = json.dumps(viz_data)
                                
                                print(f"📊 AUDIT - VISUALIZATION DATA CREATED:")
                                print(f"   📦 JSON size: {len(json_data)} characters")
                                print(f"   📋 JSON preview: {json_data[:200]}...")
                                
                                # Call visualization function - TRY BOTH APPROACHES
                                viz_agent = next(a for a in self.agents if a.name == "Data-Visualization-Agent")
                                
                                if hasattr(viz_agent, "function_map") and "create_visualization" in viz_agent.function_map:
                                    print(f"🎨 AUDIT - CALLING VISUALIZATION FUNCTION:")
                                    
                                    # Try enhanced Plotly visualization first
                                    viz_func = viz_agent.function_map["create_visualization"]
                                    viz_result = viz_func(json_data)
                                    
                                    print(f"✅ AUDIT - VISUALIZATION FUNCTION RESULT:")
                                    print(f"   📊 Result type: {type(viz_result)}")
                                    print(f"   📋 Result preview: {str(viz_result)[:200]}...")
                                    
                                    # Check if visualization was successful
                                    viz_successful = False
                                    if isinstance(viz_result, dict) and 'spec' in viz_result:
                                        spec = viz_result['spec']
                                        if isinstance(spec, dict) and 'data' in spec:
                                            data_traces = spec['data']
                                            if data_traces and len(data_traces) > 0:
                                                trace = data_traces[0]
                                                # Check if we have real data or fallback data
                                                x_data = trace.get('x', [])
                                                y_data = trace.get('y', [])
                                                if len(x_data) > 1 and len(y_data) > 1 and not (x_data == ['Data'] and y_data == [1]):
                                                    viz_successful = True
                                                    print("✅ AUDIT - Plotly visualization successful with real data")
                                    
                                    if not viz_successful:
                                        print("⚠️ AUDIT - Plotly failed, trying pandas approach...")
                                        
                                        # Try pandas visualization
                                        if "create_visualization_with_pandas" in viz_agent.function_map:
                                            pandas_viz_func = viz_agent.function_map["create_visualization_with_pandas"]
                                            viz_result = pandas_viz_func(json_data)
                                            
                                            if isinstance(viz_result, dict) and 'png_base64' in viz_result:
                                                print("✅ AUDIT - Pandas visualization successful")
                                                
                                                # Handle PNG result differently
                                                png_data = viz_result['png_base64']
                                                title = viz_result.get('title', 'Forecast Visualization')
                                                
                                                # Send PNG image directly to Teams
                                                try:
                                                    import base64
                                                    png_bytes = base64.b64decode(png_data)
                                                    
                                                    # Save temporarily and send as image
                                                    import tempfile
                                                    import os
                                                    
                                                    with tempfile.NamedTemporaryFile(suffix='.png', delete=False) as tmp_file:
                                                        tmp_file.write(png_bytes)
                                                        tmp_file_path = tmp_file.name
                                                    
                                                    # Send to Teams
                                                    response_message = f"📊 **{title}**\n\n✅ Successfully created visualization with {viz_result.get('data_points', 'multiple')} data points using pandas DataFrame approach."
                                                    
                                                    await cl.Message(
                                                        content=response_message,
                                                        elements=[cl.Image(path=tmp_file_path, name="forecast_chart", display="inline")]
                                                    ).send()
                                                    
                                                    # Clean up
                                                    os.unlink(tmp_file_path)
                                                    
                                                    print("✅ AUDIT - Successfully sent pandas PNG chart to Teams!")
                                                    return  # Skip the regular function response handling
                                                    
                                                except Exception as e:
                                                    print(f"❌ AUDIT - Failed to send pandas PNG: {e}")
                                    
                                    # Create function response message for Plotly or fallback
                                    viz_response = {
                                        "role": "function",
                                        "name": "create_visualization",
                                        "content": str(viz_result)
                                    }
                                    
                                    await self.send_message(viz_response, viz_agent.name)
                                    print("✅ AUDIT - Successfully created visualization from vector data store!")
                            else:
                                print("⚠️ AUDIT - NO DATA POINTS EXTRACTED:")
                                print("   📊 Generic parsing returned empty results")
                                print("   🔍 Check data format and parsing logic")
                                
                                viz_agent = next(a for a in self.agents if a.name == "Data-Visualization-Agent")
                                error_response = {
                                    "role": "assistant",
                                    "content": "⚠️ **Data Format Error**: Could not extract data points from the forecast data. Please fetch fresh forecast data and try again."
                                }
                                await self.send_message(error_response, viz_agent.name)
                        except Exception as viz_error:
                            print(f"❌ AUDIT - VISUALIZATION ERROR:")
                            print(f"   🚨 Error: {str(viz_error)}")
                            import traceback
                            print(f"   📋 Traceback: {traceback.format_exc()}")
                            
                            viz_agent = next(a for a in self.agents if a.name == "Data-Visualization-Agent")
                            error_response = {
                                "role": "assistant",
                                "content": f"❌ **Visualization Error**: {str(viz_error)}\n\nPlease try fetching fresh forecast data and requesting visualization again."
                            }
                            await self.send_message(error_response, viz_agent.name)
                elif ("forecasting-data-analyst-agent:" in content.lower() or 
                      "[forecasting-data-analyst-agent]" in content.lower() or
                      content.lower().startswith("forecasting-data-analyst-agent")):
                    explicit_delegation = True
                    # Delegate to Forecasting-Data-Analyst-Agent
                    analyst_agent = next(a for a in self.agents if a.name == "Forecasting-Data-Analyst-Agent")
                    self.current_agent = analyst_agent
                    analyst_response = await self._get_agent_reply(
                        analyst_agent,
                        self.messages
                    )
                    if analyst_response:
                        await self.send_message(analyst_response, analyst_agent.name)
                elif ("kpi-data-agent:" in content.lower() or 
                      "[kpi-data-agent]" in content.lower() or
                      content.lower().startswith("kpi-data-agent")):
                    explicit_delegation = True
                    # Delegate to KPI-Data-Agent
                    kpi_agent = next(a for a in self.agents if a.name == "KPI-Data-Agent")
                    self.current_agent = kpi_agent
                    kpi_response = await self._get_agent_reply(
                        kpi_agent,
                        self.messages
                    )
                    if kpi_response:
                        await self.send_message(kpi_response, kpi_agent.name)
                elif ("workforce-simulation-agent:" in content.lower() or 
                      "[workforce-simulation-agent]" in content.lower() or
                      content.lower().startswith("workforce-simulation-agent")):
                    explicit_delegation = True
                    # Delegate to Workforce-Simulation-Agent
                    workforce_simulation_agent = next(a for a in self.agents if a.name == "Workforce-Simulation-Agent")
                    self.current_agent = workforce_simulation_agent
                    workforce_simulation_response = await self._get_agent_reply(
                        workforce_simulation_agent,
                        self.messages
                    )
                    if workforce_simulation_response:
                        await self.send_message(workforce_simulation_response, workforce_simulation_agent.name)
                
                # Add logging to show when delegation didn't happen
                if not explicit_delegation:
                    print(f"ℹ️ No explicit delegation found in orchestrator response - staying with orchestrator")
            
            # Teams mode: No interactive loop (single message/response)
            print("✅ Teams mode: Single message/response completed")
                
        except Exception as e:
            print(f"❌ Error in run_chat: {e}")
            import traceback
            print(traceback.format_exc())
            await cl.Message(
                content=f"⚠️ I encountered an error: {str(e)}. Please try again."
            ).send()
    
    async def _get_agent_reply(self, agent, messages, last_agent=None):
        """Get a reply from an agent - identical to original logic"""
        try:
            print(f"\n🔍 Getting reply from agent: {agent.name}")
            
            # Get recent context from ChromaDB
            context = self._get_recent_context()
            if context:
                print(f"📚 Adding conversation context from ChromaDB")
                # ENHANCED: Agent-specific context formatting with comprehensive instructions
                agent_specific_context = f"""You are part of an intelligent, context-aware workforce management system. Here is the complete conversation history in perfect chronological order:

{context}

**🎯 YOUR ROLE AS {agent.name}:**

{self._get_agent_specific_instructions(agent.name)}

**📚 CONTEXT UNDERSTANDING:**
- The conversation above shows the EXACT sequence of interactions
- Numbers in [1], [2], [3] show chronological order (1 = earliest, highest = most recent)
- [KPI REQUEST], [FORECAST REQUEST], [VISUALIZATION REQUEST] indicators show what type of requests were made
- ALWAYS use real data from the conversation - NEVER generate fake examples

**🧠 INTELLIGENT OPERATION:**
- Understand user intent from the complete conversation flow
- Connect current requests to previous context
- Use only real data found in conversation history
- Be conversational and helpful, not robotic
- Ask for clarification only when genuinely needed

**🚨 CRITICAL RULES:**
1. **REAL DATA ONLY**: Never generate dummy/example data
2. **CONTEXT AWARE**: Understand the full conversation flow
3. **USER FOCUSED**: Respond to what user actually wants
4. **INTELLIGENT**: Use your expertise, don't just follow templates
5. **CONVERSATIONAL**: Maintain natural dialogue flow

Current user request: Respond appropriately based on your role and the conversation context above."""
                
                context_msg = {
                    "role": "system",
                    "content": agent_specific_context
                }
                messages = [context_msg] + messages
            
            print(f"Debug - Messages being processed: {[msg.get('role', 'unknown') + ': ' + str(msg.get('content', ''))[:100] + '...' for msg in messages]}")
            
            # Clean messages while preserving function calls
            clean_messages = []
            for msg in messages:
                # Handle string messages
                if isinstance(msg, str):
                    clean_msg = {
                        "role": "user",
                        "content": msg
                    }
                else:
                    # Handle dict messages
                    clean_msg = {
                        "role": msg.get("role", "assistant"),
                        "content": msg.get("content", "")
                    }
                    if msg.get("function_call"):
                        clean_msg["function_call"] = msg["function_call"]
                    if msg.get("name"):  # For function response messages
                        clean_msg["name"] = msg["name"]
                        clean_msg["role"] = "function"  # Ensure proper role for function messages
                clean_messages.append(clean_msg)
            
            # ADDED: More detailed debug for final message content
            print(f"Debug - Final clean messages for {agent.name}:")
            for i, msg in enumerate(clean_messages):
                print(f"  [{i}] {msg.get('role', 'unknown')}: {str(msg.get('content', ''))[:150]}...")
            
            if hasattr(agent, 'a_generate_reply'):
                print("Debug - Using async generate")
                reply = await agent.a_generate_reply(
                    messages=clean_messages,
                    sender=last_agent or self.user_agent
                )
            else:
                print("Debug - Using sync generate")
                reply = agent.generate_reply(
                    messages=clean_messages,
                    sender=last_agent or self.user_agent
                )
            
            print(f"💬 Raw agent reply: {reply}")
            
            # IMPROVED: Better handling of empty or generic responses
            if isinstance(reply, dict):
                content = reply.get("content", "")
                # Check for problematic generic responses
                if content in ["Hello! How can I help you today?", "Hello! How can I assist you today?"]:
                    print("⚠️ Detected generic response - forcing a better response")
                    # Force a better response based on recent context
                    if "what all can you do" in str(messages[-1].get("content", "")).lower():
                        reply["content"] = """I am an Orchestrator Agent designed to help you manage and analyze data, forecasts, and workforce planning. I coordinate a team of specialized AI agents to fulfill your requests.

Here's what I can help you with:

1. **Retrieve Forecast Data**: I can fetch volume forecast data for various business units, substreams, and teams. Just tell me what you need!
2. **Analyze Data**: Once we have data, I can ask the Forecasting-Data-Analyst-Agent to analyze it for insights, trends, and interpretations.
3. **Visualize Data**: I can request the Data-Visualization-Agent to create charts, graphs, and other visual representations of your data.
4. **Get KPI Data**: I can fetch specific Key Performance Indicator (KPI) data, like attrition rates, for different departments or metrics.
5. **Run Workforce Simulations**: The Workforce-Simulation-Agent can perform simulations for capacity planning, workforce optimization, FTE requirements, and analyze staffing needs to prevent SLA breaches.

Just tell me what you'd like to do! For example, you could ask:
* "Get forecast for business-retail substream-online team-alpha"
* "Analyze this forecast"
* "Show me a chart of this data"
* "What's the home-loan attrition rate?"
* "Run a simulation to see if we can handle a 20% increase in demand." """
            
            # Handle function calls in the reply (enhanced for AutoGen 2.x tool_calls)
            if isinstance(reply, dict):
                # NEW: Handle AutoGen 2.x tool_calls format
                if reply.get("tool_calls"):
                    tool_calls = reply["tool_calls"]
                    print(f"⚙️ {agent.name} making {len(tool_calls)} tool call(s)")
                    
                    tool_results = []
                    for tool_call in tool_calls:
                        tool_id = tool_call.get("id", "unknown")
                        function_info = tool_call.get("function", {})
                        func_name = function_info.get("name")
                        args_str = function_info.get("arguments", "{}")
                        
                        print(f"🔧 Executing tool: {func_name} with args: {args_str}")
                        
                        # Get the registered function from the agent
                        if hasattr(agent, '_function_map') and func_name in agent._function_map:
                            func = agent._function_map[func_name]
                            try:
                                # Parse arguments
                                import json
                                args_dict = json.loads(args_str) if args_str else {}
                                
                                # Execute function with proper arguments
                                if len(args_dict) == 1:
                                    # Single argument - pass the value directly
                                    arg_value = list(args_dict.values())[0]
                                    result = func(arg_value)
                                else:
                                    # Multiple arguments - pass as kwargs
                                    result = func(**args_dict)
                                
                                print(f"✅ Tool execution result: {str(result)[:200]}...")
                                
                                # Format result
                                if isinstance(result, dict):
                                    if 'results' in result:
                                        tool_result = str(result['results'])
                                    elif 'error' in result:
                                        tool_result = f"Error: {result['error']}"
                                    else:
                                        tool_result = str(result)
                                else:
                                    tool_result = str(result)
                                    
                                tool_results.append({
                                    "tool_call_id": tool_id,
                                    "role": "tool",
                                    "name": func_name,
                                    "content": tool_result
                                })
                                
                            except Exception as e:
                                print(f"❌ Tool execution error: {e}")
                                tool_results.append({
                                    "tool_call_id": tool_id,
                                    "role": "tool", 
                                    "name": func_name,
                                    "content": f"Error executing tool: {str(e)}"
                                })
                        else:
                            print(f"⚠️ Tool function {func_name} not found in agent._function_map")
                            tool_results.append({
                                "tool_call_id": tool_id,
                                "role": "tool",
                                "name": func_name,
                                "content": f"Error: Function {func_name} not available"
                            })
                    
                    # Now get a follow-up response from the agent incorporating the tool results
                    if tool_results:
                        # Add tool call and results to message history
                        updated_messages = clean_messages + [
                            {
                                "role": "assistant",
                                "content": reply.get("content", ""),
                                "tool_calls": tool_calls
                            }
                        ] + tool_results
                        
                        print(f"🔄 Getting follow-up response from {agent.name} after tool execution")
                        
                        # Get agent's response incorporating tool results
                        if hasattr(agent, 'a_generate_reply'):
                            follow_up_reply = await agent.a_generate_reply(
                                messages=updated_messages,
                                sender=last_agent or self.user_agent
                            )
                        else:
                            follow_up_reply = agent.generate_reply(
                                messages=updated_messages,
                                sender=last_agent or self.user_agent
                            )
                        
                        print(f"✅ Follow-up reply from {agent.name}: {str(follow_up_reply)[:200]}...")
                        
                        # Return the follow-up response
                        if isinstance(follow_up_reply, dict):
                            return {
                                "role": "assistant",
                                "content": follow_up_reply.get("content", "")
                            }
                        else:
                            return {
                                "role": "assistant", 
                                "content": str(follow_up_reply)
                            }
                
                # EXISTING: Handle old-style function_call for backward compatibility
                if reply.get("function_call"):
                    function_call = reply["function_call"]
                    if hasattr(agent, "function_map"):
                        func_name = function_call.get("name")
                        if func_name in agent.function_map:
                            func = agent.function_map[func_name]
                            args = function_call.get("arguments", "")
                            print(f"⚙️ {agent.name} executing function {func_name} with args: {args}")
                            result = func(args)
                            print(f"Debug - Function result from {agent.name}: {result}")
                            
                            # Format and return the result
                            if isinstance(result, dict):
                                if 'results' in result:
                                    return {
                                        "role": "function",
                                        "name": func_name,
                                        "content": str(result['results'])
                                    }
                                elif 'error' in result:
                                    return {
                                        "role": "function",
                                        "name": func_name,
                                        "content": f"Error: {result['error']}"
                                    }
                            return {
                                "role": "function",
                                "name": func_name,
                                "content": str(result)
                            }
                
                # Check for function call in content
                content = reply.get("content", "")
                if isinstance(content, str) and "function_call" in content:
                    try:
                        # Try to parse JSON from content
                        import json
                        # Find the JSON object in the content
                        start = content.find("{")
                        end = content.rfind("}") + 1
                        if start >= 0 and end > start:
                            json_str = content[start:end]
                            json_obj = json.loads(json_str)
                            if "function_call" in json_obj:
                                function_call = json_obj["function_call"]
                                if hasattr(agent, "function_map"):
                                    func_name = function_call.get("name")
                                    if func_name in agent.function_map:
                                        func = agent.function_map[func_name]
                                        args = function_call.get("arguments", "")
                                        print(f"⚙️ {agent.name} executing function {func_name} with args: {args}")
                                        result = func(args)
                                        print(f"Debug - Function result from {agent.name}: {result}")
                                        
                                        # Format and return the result
                                        if isinstance(result, dict):
                                            if 'results' in result:
                                                return {
                                                    "role": "function",
                                                    "name": func_name,
                                                    "content": str(result['results'])
                                                }
                                            elif 'error' in result:
                                                return {
                                                    "role": "function",
                                                    "name": func_name,
                                                    "content": f"Error: {result['error']}"
                                                }
                                        return {
                                            "role": "function",
                                            "name": func_name,
                                            "content": str(result)
                                        }
                    except json.JSONDecodeError:
                        pass
            
            # Return original reply if no function call found
            if reply is None:
                return {
                    "role": "assistant",
                    "content": "🤖 Ready for your next question!"
                }

            return {
                "role": "assistant",
                "content": reply.get("content", "") if isinstance(reply, dict) else str(reply)
            }
            
        except Exception as e:
            print(f"❌ Error in _get_agent_reply: {e}")
            import traceback
            print(traceback.format_exc())
            return {
                "role": "assistant",
                "content": f"⚠️ Error processing request: {str(e)}"
            }

    def _get_agent_specific_instructions(self, agent_name):
        """Get agent-specific instructions based on their role"""
        instructions = {
            "Orchestrator-Agent": """
🎯 **INTELLIGENT CONVERSATION MANAGER**
- You are the primary entry point and intelligent conversation router
- Handle general queries yourself (data transformation, simple questions, clarifications)
- Delegate ONLY when specialized functions or expertise is needed
- Understand user intent from conversation context
- NEVER loop or repeatedly delegate the same request
- Be conversational and helpful, not robotic
            """,
            
            "Fetch-Volume-Forecast-Agent": """
📊 **INTELLIGENT DATA RETRIEVAL SPECIALIST**
- Execute fetch_forecast function when delegated forecast retrieval tasks
- Analyze and filter vector search results intelligently
- Present only relevant data that matches user requirements
- NEVER generate dummy data - use only real search results
- Ask for clarification if user request is unclear
- Provide conversational guidance to help users get the right data
            """,
            
            "KPI-Data-Agent": """
📋 **INTELLIGENT PERFORMANCE METRICS SPECIALIST**
- Execute fetch_kpi function when delegated KPI retrieval tasks
- Analyze and filter vector search results intelligently
- Focus on business-relevant KPIs that match user requirements
- NEVER generate dummy data - use only real search results
- Provide business context for KPI interpretation
- Explain significance of metrics for business performance
            """,
            
            "Forecasting-Data-Analyst-Agent": """
📈 **BANKING & FINTECH INTELLIGENCE EXPERT**
- NEVER call functions - work exclusively from conversation context
- Extract real data from conversation history for analysis
- Apply deep banking/fintech domain expertise
- Provide value-driven insights with business impact
- Adapt analysis depth to user requests (quick insights vs detailed analysis)
- Focus on strategic recommendations and financial implications
            """,
            
            "Data-Visualization-Agent": """
📊 **INTELLIGENT CHART CREATION EXPERT**
- Extract data from recent conversation context
- Intelligently determine best visualization type for the data
- Call create_visualization function with real data from context
- Self-identify data patterns (time series, categories, comparisons)
- NEVER generate dummy data - only visualize real context data
- Explain visualization choices and suggest alternatives
            """,
            
            "Workforce-Simulation-Agent": """
🎮 **WORKFORCE OPTIMIZATION SPECIALIST**
- Handle FTE calculations, SLA breach analysis, capacity planning
- Provide detailed simulation analysis with mathematical reasoning
- Use real data from conversation context for simulations
- Focus on workforce management optimization
- Provide actionable recommendations for staffing decisions
- Consider financial impact and risk assessment
            """
        }
        
        return instructions.get(agent_name, f"""
🤖 **INTELLIGENT AGENT**
- Work collaboratively as part of the intelligent workforce management system
- Use conversation context to understand user intent
- Provide expert assistance in your domain
- Never generate fake data - use only real information
        """)

    def _parse_visualization_intent(self, messages):
        """Parse user intent from recent messages for visualization delegation - ENHANCED WITH COMPARISON MODE"""
        import re  # 🔧 CRITICAL FIX: Import at function start for availability throughout
        intent = {"comparison_mode": False, "datasets": []}
        
        # Look for explicit criteria in recent messages
        for msg in reversed(messages):  # Start with most recent
            if msg.get("content"):
                content = msg["content"].lower()
                
                # 🔄 DETECT COMPARISON REQUESTS
                comparison_keywords = [
                    "compare", "comparison", "vs", "versus", "both", 
                    "side by side", "together", "against", "difference",
                    "delta", "chart with", "plot both", "show both"
                ]
                
                if any(keyword in content for keyword in comparison_keywords):
                    intent["comparison_mode"] = True
                    print(f"🔄 AUDIT - COMPARISON MODE DETECTED in: '{content}'")
                    
                    # 🎯 EXTRACT COMPARISON ENTITIES
                    patterns = [
                        r'compare\s+(\w+)\s+(?:and|vs|versus|with)\s+(\w+)',
                        r'(\w+)\s+vs\s+(\w+)',
                        r'both\s+(\w+)\s+and\s+(\w+)',
                        r'(\w+)\s+and\s+(\w+)\s+teams?',
                        r'show\s+(\w+)\s+and\s+(\w+)'
                    ]
                    
                    for pattern in patterns:
                        matches = re.findall(pattern, content)
                        if matches:
                            entity1, entity2 = matches[0]
                            print(f"🎯 AUDIT - Extracted comparison entities: '{entity1}' vs '{entity2}'")
                            intent["datasets"] = [
                                {"team": entity1},
                                {"team": entity2}
                            ]
                            break
                    
                    # If no specific entities found, look for recent context
                    if not intent["datasets"]:
                        print("🔍 AUDIT - No specific entities found, will use recent data for comparison")
                
                # Look for explicit format first (for single dataset)
                if not intent["comparison_mode"]:
                    business_match = re.search(r'business\s*[:\-=]\s*["\']?([^"\'",\s]+)["\']?', content)
                    if business_match and not intent.get('business'):
                        intent['business'] = business_match.group(1)
                    
                    substream_match = re.search(r'substream\s*[:\-=]\s*["\']?([^"\'",\s]+)["\']?', content)
                    if substream_match and not intent.get('substream'):
                        intent['substream'] = substream_match.group(1)
                    
                    team_match = re.search(r'team\s*[:\-=]\s*["\']?([^"\'",\s]+)["\']?', content)
                    if team_match and not intent.get('team'):
                        intent['team'] = team_match.group(1)
                    
                    # Pattern 2: Common known entities
                    if 'logistics' in content and not intent.get('business'):
                        intent['business'] = 'logistics'
                    
                    if 'dlt' in content and not intent.get('substream'):
                        intent['substream'] = 'dlt'
                    
                    if 'support' in content and not intent.get('team'):
                        intent['team'] = 'support'
        
        # 🎯 FALLBACK: Check vector data store for recent data if no specific intent found
        if not intent["comparison_mode"] and not any(intent.get(k) for k in ['business', 'substream', 'team']):
            try:
                recent_results = self.vector_data_store.get_latest_results(
                    session_id=self.session_id,
                    query_type="forecast",
                    limit=1
                )
                if recent_results:
                    latest = recent_results[0]
                    intent.update({
                        'business': latest['business'],
                        'substream': latest['substream'],
                        'team': latest['team']
                    })
                    print(f"🔄 AUDIT - Using fallback intent from latest data: {intent}")
            except Exception as e:
                print(f"⚠️ AUDIT - Error getting fallback intent: {e}")
        
        print(f"🧠 AUDIT - FINAL PARSED INTENT: {intent}")
        return intent

    def _parse_vector_search_data(self, data):
        """
        🧠 INTELLIGENT GENERIC DATA PARSER FOR VECTOR SEARCH RESULTS
        Handles multiple formats: Python dict, JSON, markdown table, raw text
        """
        try:
            print(f"🔍 Parsing data of type: {type(data)}")
            
            # 1. Try to parse as JSON/dict first (most common for vector results)
            if isinstance(data, dict):
                return self._parse_dict_data(data)
            elif isinstance(data, list):
                return self._parse_list_data(data)
            elif isinstance(data, str):
                return self._parse_string_data(data)
            else:
                print(f"⚠️ Unsupported data type: {type(data)}")
                return []
                
        except Exception as e:
            print(f"❌ Error in generic data parsing: {e}")
            import traceback
            print(traceback.format_exc())
            return []

    def _parse_string_data(self, data):
        """Parse string data - try multiple formats"""
        try:
            # Try JSON parsing first
            import json
            try:
                parsed_json = json.loads(data)
                print("✅ Parsed string as JSON")
                if isinstance(parsed_json, dict):
                    return self._parse_dict_data(parsed_json)
                elif isinstance(parsed_json, list):
                    return self._parse_list_data(parsed_json)
            except json.JSONDecodeError:
                pass
            
            # Try Python eval (safely) for dict format
            try:
                if data.strip().startswith('{') and data.strip().endswith('}'):
                    # Check for dangerous content before eval
                    if not any(dangerous in data.lower() for dangerous in ['import', 'exec', '__', 'open', 'file']):
                        parsed_dict = eval(data)
                        if isinstance(parsed_dict, dict):
                            print("✅ Parsed string as Python dict")
                            return self._parse_dict_data(parsed_dict)
            except (SyntaxError, ValueError):
                pass
            
            # Try markdown table parsing
            if '|' in data and 'date' in data.lower():
                print("🔍 Attempting markdown table parsing")
                return self._parse_markdown_table(data)
            
            # Try to extract JSON from text
            import re
            json_match = re.search(r'\{.*\}', data, re.DOTALL)
            if json_match:
                try:
                    json_data = json.loads(json_match.group())
                    print("✅ Extracted JSON from text")
                    return self._parse_dict_data(json_data)
                except json.JSONDecodeError:
                    pass
            
            # Last resort: look for forecast patterns in text
            return self._parse_forecast_text(data)
            
        except Exception as e:
            print(f"❌ Error parsing string data: {e}")
            return []

    def _parse_dict_data(self, data):
        """Parse dictionary/JSON data intelligently"""
        try:
            data_points = []
            
            # 🔍 PATTERN 1: Direct forecast data format
            if 'forecast_data' in data:
                forecast_data = data['forecast_data']
                if isinstance(forecast_data, list):
                    for item in forecast_data:
                        if isinstance(item, dict) and 'date' in item and 'value' in item:
                            data_points.append({"date": item['date'], "value": item['value']})
                    print(f"✅ Found forecast_data array with {len(data_points)} points")
                    return data_points
            
            # 🔍 PATTERN 2: Results array format
            if 'results' in data:
                results = data['results']
                if isinstance(results, list):
                    for item in results:
                        if isinstance(item, dict):
                            # Look for date and value fields
                            date_field = None
                            value_field = None
                            
                            for key in item.keys():
                                if 'date' in key.lower():
                                    date_field = key
                                elif any(keyword in key.lower() for keyword in ['value', 'forecast', 'volume', 'count']):
                                    value_field = key
                            
                            if date_field and value_field:
                                try:
                                    value = int(float(item[value_field]))
                                    data_points.append({"date": item[date_field], "value": value})
                                except (ValueError, KeyError):
                                    continue
                    
                    if data_points:
                        print(f"✅ Found results array with {len(data_points)} points")
                        return data_points
            
            # 🔍 PATTERN 3: Direct dictionary with dates as keys
            date_value_pairs = []
            for key, value in data.items():
                # Check if key looks like a date
                if isinstance(key, str) and any(pattern in key for pattern in ['2024', '2025', '2026', '-01-', '-02-', '-03-']):
                    try:
                        numeric_value = int(float(value))
                        date_value_pairs.append({"date": key, "value": numeric_value})
                    except (ValueError, TypeError):
                        continue
            
            if date_value_pairs:
                print(f"✅ Found date-value pairs with {len(date_value_pairs)} points")
                return date_value_pairs
            
            # 🔍 PATTERN 4: Nested data structures
            for key, value in data.items():
                if isinstance(value, (list, dict)):
                    nested_points = self._parse_vector_search_data(value)
                    if nested_points:
                        print(f"✅ Found nested data in '{key}' with {len(nested_points)} points")
                        return nested_points
            
            print("⚠️ No recognizable forecast data patterns found in dict")
            return []
            
        except Exception as e:
            print(f"❌ Error parsing dict data: {e}")
            return []

    def _parse_list_data(self, data):
        """Parse list data"""
        try:
            data_points = []
            
            for item in data:
                if isinstance(item, dict):
                    # Look for forecast data patterns
                    if 'date' in item and 'value' in item:
                        data_points.append({"date": item['date'], "value": item['value']})
                    elif 'date' in item and 'forecast' in item:
                        try:
                            value = int(float(item['forecast']))
                            data_points.append({"date": item['date'], "value": value})
                        except (ValueError, TypeError):
                            continue
                    else:
                        # Try to find date and numeric fields
                        date_field = None
                        value_field = None
                        
                        for key in item.keys():
                            if 'date' in key.lower():
                                date_field = key
                            elif isinstance(item[key], (int, float)):
                                value_field = key
                        
                        if date_field and value_field:
                            try:
                                value = int(float(item[value_field]))
                                data_points.append({"date": item[date_field], "value": value})
                            except (ValueError, KeyError):
                                continue
                elif isinstance(item, list) and len(item) >= 2:
                    # Handle [[date, value], [date, value]] format
                    try:
                        date = str(item[0])
                        value = int(float(item[1]))
                        data_points.append({"date": date, "value": value})
                    except (ValueError, IndexError):
                        continue
            
            if data_points:
                print(f"✅ Found list data with {len(data_points)} points")
                return data_points
            
            print("⚠️ No recognizable forecast data patterns found in list")
            return []
            
        except Exception as e:
            print(f"❌ Error parsing list data: {e}")
            return []

    def _parse_markdown_table(self, data):
        """Parse markdown table format (legacy support)"""
        try:
            data_points = []
            lines = data.split('\n')
            
            print(f"🔍 DEBUG - Parsing markdown table with {len(lines)} lines")
            
            for line in lines:
                if '|' in line and line.strip() and not line.startswith('|:'):
                    cols = [col.strip() for col in line.split('|') if col.strip()]
                    print(f"🔍 DEBUG - Parsed columns: {cols}")
                    
                    # Try different column arrangements
                    if len(cols) >= 2:
                        # Find date and value columns
                        date_col = None
                        value_col = None
                        
                        for i, col in enumerate(cols):
                            if any(date_pattern in col.lower() for date_pattern in ['date', '2024', '2025', '2026']):
                                date_col = i
                            elif col.isdigit() or (col.replace('.', '').isdigit() and '.' in col):
                                value_col = i
                        
                        if date_col is not None and value_col is not None and cols[date_col] not in ['Date', 'date']:
                            try:
                                date = cols[date_col]
                                forecast_value = int(float(cols[value_col]))
                                data_point = {"date": date, "value": forecast_value}
                                data_points.append(data_point)
                                print(f"✅ DEBUG - Added data point: {data_point}")
                            except (ValueError, IndexError) as e:
                                print(f"⚠️ DEBUG - Failed to parse line: {e}")
                                continue
            
            print(f"✅ Markdown table parsed: {len(data_points)} points")
            return data_points
            
        except Exception as e:
            print(f"❌ Error parsing markdown table: {e}")
            return []

    def _parse_forecast_text(self, data):
        """Extract forecast data from plain text - ENHANCED with audit logging and FIXED parsing"""
        try:
            import re
            data_points = []
            
            print(f"🔍 AUDIT - Starting text parsing for {len(data)} characters")
            print(f"🔍 AUDIT - Sample data: {data[:200]}...")
            
            # 🔧 ENHANCED: Parse markdown-style forecast format
            # Look for patterns like: *   **2025-06-01:** 2845
            markdown_pattern = r'\*\s*\*\*(\d{4}-\d{2}-\d{2}):\*\*\s*(\d+)'
            markdown_matches = re.findall(markdown_pattern, data)
            
            if markdown_matches:
                print(f"✅ AUDIT - Found {len(markdown_matches)} markdown-style entries")
                for match in markdown_matches:
                    try:
                        date = match[0]
                        value = int(match[1])
                        # 🔧 CRITICAL FIX: Only take values > 1000 to avoid extracting years
                        if value > 1000:  # Real forecast values are typically > 1000
                            data_points.append({"date": date, "value": value})
                            print(f"📊 AUDIT - Extracted: {date} = {value}")
                        else:
                            print(f"⚠️ AUDIT - Skipped small value (likely year): {value}")
                    except (ValueError, IndexError) as e:
                        print(f"⚠️ AUDIT - Failed to parse markdown entry: {e}")
                        continue
                
                if data_points:
                    print(f"✅ AUDIT - Markdown parsing successful: {len(data_points)} points")
                    return data_points
            
            # 🔍 Fallback: Look for date-value patterns in text
            print("🔍 AUDIT - Trying fallback date-value patterns...")
            patterns = [
                r'\*\s*\*\*([A-Za-z]+\s+\d{4})\*\*:\s*(\d{3,})',  # **Month YYYY**: value
                r'(\d{4}-\d{2}-\d{2})[:\s]+(\d{3,})',  # Date: value (3+ digits to avoid years)
                r'(\d{4}/\d{2}/\d{2})[:\s]+(\d{3,})',  # Date/value format
                r'([A-Za-z]{3,}\s+\d{4})[:\s]+(\d{3,})',  # Month Year: value (extended for full month names)
            ]
            
            pattern_names = [
                "**Month YYYY**: value",
                "YYYY-MM-DD: value", 
                "YYYY/MM/DD: value",
                "Month YYYY: value"
            ]
            
            for i, (pattern, pattern_name) in enumerate(zip(patterns, pattern_names)):
                print(f"🔍 AUDIT - Testing Pattern {i+1}: {pattern_name}")
                print(f"    🔤 Regex: {pattern}")
                matches = re.findall(pattern, data)
                print(f"    📊 Raw matches found: {len(matches)}")
                
                if matches:
                    print(f"    📋 Sample matches (first 3):")
                    for j, match in enumerate(matches[:3], 1):
                        print(f"        [{j}] {match}")
                
                valid_extractions = 0
                for match in matches:
                    try:
                        date = match[0]
                        value = int(match[1])
                        if value > 1000:  # Filter out years/small numbers
                            data_points.append({"date": date, "value": value})
                            print(f"    ✅ AUDIT - Pattern {i+1} extracted: {date} = {value}")
                            valid_extractions += 1
                        else:
                            print(f"    ⚠️ AUDIT - Pattern {i+1} skipped small value: {value}")
                    except (ValueError, IndexError) as e:
                        print(f"    ❌ AUDIT - Pattern {i+1} failed to parse: {e}")
                        continue
                
                print(f"    📊 Valid extractions from this pattern: {valid_extractions}")
                print(f"    📈 Total data points so far: {len(data_points)}")
                
                # If we found data with this pattern, report success
                if valid_extractions > 0:
                    print(f"🎯 AUDIT - SUCCESS with Pattern {i+1}: {pattern_name}")
            
            print(f"\n📊 AUDIT - PATTERN TESTING SUMMARY:")
            print(f"   🔍 Patterns tested: {len(patterns)}")
            print(f"   📈 Total data points extracted: {len(data_points)}")
            if data_points:
                print(f"   🏆 Sample extracted data:")
                for i, point in enumerate(data_points[:3], 1):
                    print(f"      [{i}] {point['date']}: {point['value']}")
                if len(data_points) > 3:
                    print(f"      ... and {len(data_points) - 3} more points")
            
            return data_points
            
        except Exception as e:
            print(f"❌ AUDIT - Error parsing forecast text: {e}")
            import traceback
            print(f"❌ AUDIT - Traceback: {traceback.format_exc()}")
            return []

@cl.on_chat_start
async def on_chat_start():
    """Initialize Teams chat session"""
    # Get Teams user info
    teams_user = cl.user_session.get("user")
    print(f"📱 Teams user: {teams_user}")
    
    # Get Teams session ID
    session_id = teams_session_manager.get_teams_session_id(teams_user)
    
    # Create or get session data
    session_data = teams_session_manager.get_or_create_session(session_id, teams_user)
    
    # Store session info in Chainlit session
    cl.user_session.set('teams_session_id', session_id)
    cl.user_session.set('teams_session_data', session_data)
    
    # Only send welcome message for NEW sessions (check the is_new flag)
    if session_data.get('is_new', False):
        welcome_msg = f"""🚀 **AI-Analyst**

📱 Welcome to Teams integration!
🆔 Session ID: `{session_id}`

**Available Operations:**
• 📊 **Forecast data**: "Get forecast for retail team"
• 📋 **KPI metrics**: "Show KPI for last month"  
• 📈 **Visualizations**: "Create chart for Q1 data"
• 🎮 **Simulations**: "Run workforce simulation"

**Quick Commands:**
• Type `help` for detailed commands
• Type `reset` to clear session context
• Type `status` to see current session info

Ready to assist with your workforce management needs! 🎯
"""
        await cl.Message(content=welcome_msg).send()
        print(f"📨 Sent welcome message for new session: {session_id}")
        
        # Mark session as no longer new after sending welcome message
        session_data['is_new'] = False
    else:
        # For existing sessions, just log the continuation (no UI message)
        print(f"📱 Session resumed: {session_id} (Last active: {session_data.get('last_active', 'Unknown')})")
        print(f"🔄 Continuing existing session - no UI message sent")

@cl.on_message
async def main(message: cl.Message):
    """Main message handler - Teams optimized"""
    try:
        # 🔥 RAW MESSAGE INPUT LOGGING
        print(f"\n🔥 RAW USER MESSAGE - COMPLETE INPUT DUMP:")
        print(f"📝 Message Type: {type(message)}")
        print(f"📦 Message Content Length: {len(message.content) if message.content else 0}")
        print(f"🔥 RAW COMPLETE MESSAGE:")
        print(f"{'='*60}")
        print(f"CONTENT: {message.content}")
        if hasattr(message, 'elements') and message.elements:
            print(f"ELEMENTS: {message.elements}")
        if hasattr(message, 'metadata') and message.metadata:
            print(f"METADATA: {message.metadata}")
        print(f"{'='*60}")
        
        # Get Teams session info
        session_id = cl.user_session.get('teams_session_id')
        teams_user = cl.user_session.get("user")
        
        print(f"🔥 RAW SESSION INFO:")
        print(f"   🆔 Session ID: {session_id}")
        print(f"   👤 Teams User: {teams_user}")
        
        if not session_id:
            # Create session if not exists
            session_id = teams_session_manager.get_teams_session_id(teams_user)
            session_data = teams_session_manager.get_or_create_session(session_id, teams_user)
            cl.user_session.set('teams_session_id', session_id)
            cl.user_session.set('teams_session_data', session_data)
            print(f"🔥 RAW SESSION CREATED: {session_id}")
        
        print(f"📨 Processing Teams message for session: {session_id}")
        user_input = message.content.strip()
        
        print(f"🔥 RAW USER INPUT (STRIPPED): '{user_input}'")
        print(f"🔥 RAW INPUT LENGTH: {len(user_input)} characters")
        
        # Handle special commands
        if user_input.lower() in ["end", "reset", "quit", "exit"]:
            print(f"🔥 RAW SPECIAL COMMAND: {user_input.lower()}")
            context_manager = get_session_context_manager(session_id)
            context_manager.clear(session_id)
            
            # 🔧 CRITICAL FIX: Also clear ChromaDB collection for complete reset
            try:
                chroma_client = get_session_chroma_client(session_id)
                collection_name = f"agent_conversations_{session_id.replace(':', '_').replace('@', '_').replace(' ', '_')}"
                
                # Sanitize collection name like in get_conversation_collection
                sanitized_session_id = session_id.replace(":", "_").replace("@", "_").replace(" ", "_")
                if not sanitized_session_id[0].isalnum():
                    sanitized_session_id = "a" + sanitized_session_id
                if not sanitized_session_id[-1].isalnum():
                    sanitized_session_id = sanitized_session_id + "a"
                collection_name = f"agent_conversations_{sanitized_session_id}"
                
                # Delete the entire collection to truly reset
                try:
                    chroma_client.delete_collection(name=collection_name)
                    print(f"🗑️ Deleted ChromaDB collection: {collection_name}")
                except Exception as delete_error:
                    print(f"⚠️ Could not delete collection {collection_name}: {delete_error}")
                    # If deletion fails, try to clear all documents in the collection
                    try:
                        collection = chroma_client.get_collection(name=collection_name)
                        all_ids = collection.get()['ids']
                        if all_ids:
                            collection.delete(ids=all_ids)
                            print(f"🧹 Cleared all documents from collection: {collection_name}")
                    except Exception as clear_error:
                        print(f"⚠️ Could not clear collection documents: {clear_error}")
                        
            except Exception as e:
                print(f"⚠️ Error clearing ChromaDB: {e}")
            
            # 📊 CLEAR VECTOR DATA STORE
            try:
                vector_data_store = get_session_vector_data_store()
                vector_data_store.clear_session(session_id)
                print(f"🗑️ Cleared vector data store for session: {session_id}")
            except Exception as e:
                print(f"⚠️ Error clearing vector data store: {e}")
            
            # 🤖 CRITICAL FIX: Clear agent conversation memory
            try:
                session_data = teams_session_manager.sessions.get(session_id, {})
                if session_data.get("agents"):
                    print(f"🧠 Clearing agent conversation memory...")
                    for agent in session_data["agents"]:
                        # Clear autogen agent's internal conversation history
                        if hasattr(agent, '_oai_messages'):
                            agent._oai_messages.clear()
                            print(f"  ✅ Cleared {agent.name} conversation history")
                        if hasattr(agent, 'chat_messages'):
                            agent.chat_messages.clear()
                            print(f"  ✅ Cleared {agent.name} chat messages")
                        if hasattr(agent, '_conversation_cache'):
                            agent._conversation_cache.clear()
                            print(f"  ✅ Cleared {agent.name} conversation cache")
                        
                        # 🔧 ENHANCED: Clear additional agent memory attributes
                        if hasattr(agent, '_messages'):
                            agent._messages.clear()
                            print(f"  ✅ Cleared {agent.name} _messages")
                        if hasattr(agent, 'message_history'):
                            agent.message_history.clear()
                            print(f"  ✅ Cleared {agent.name} message_history")
                        if hasattr(agent, '_last_message'):
                            agent._last_message = None
                            print(f"  ✅ Cleared {agent.name} _last_message")
                        if hasattr(agent, '_context'):
                            agent._context = {}
                            print(f"  ✅ Cleared {agent.name} _context")
                        if hasattr(agent, '_previous_responses'):
                            agent._previous_responses.clear()
                            print(f"  ✅ Cleared {agent.name} _previous_responses")
                    
                    # Force recreation of agents on next request
                    session_data["agents"] = None
                    print(f"🔄 Agents will be recreated fresh on next request")
                else:
                    print(f"ℹ️ No agents to clear for session: {session_id}")
                    
                # 🔧 CRITICAL: Also clear the session context data completely
                session_data["context"] = {
                    "teams": [],
                    "last_query": None,
                    "current_comparison": None,
                    "visualizations": []
                }
                print(f"🧹 Reset session context data")
                
                # 🔧 CRITICAL: Clear the entire session data (except user info)
                user_info = session_data.get('user')
                created_at = session_data.get('created_at')
                session_data.clear()
                session_data.update({
                    "user": user_info,
                    "created_at": created_at,
                    "last_active": datetime.now(),
                    "context": {
                        "teams": [],
                        "last_query": None,
                        "current_comparison": None,
                        "visualizations": []
                    },
                    "agents": None,
                    "context_manager": None,
                    "chroma_client": None,
                    "is_new": False
                })
                print(f"🧹 Complete session data reset (preserved user and creation time)")
                
            except Exception as e:
                print(f"⚠️ Error clearing agent memory: {e}")
                import traceback
                print(f"⚠️ Agent clear traceback: {traceback.format_exc()}")
            
            await cl.Message(content="🔄 **Session reset!** Context and data stores cleared. Ready for new queries.").send()
            return
        
        elif user_input.lower() == "help":
            print(f"🔥 RAW HELP COMMAND")
            help_msg = """
📚 **Workforce Management Commands**

**Forecast Operations:**
• `forecast for [business] [team]` - Get workforce forecasts
• `show forecast trends` - Display forecast visualizations

**KPI Operations:**  
• `kpi for [metric] last [period]` - Get KPI data
• `show kpi dashboard` - Display KPI overview

**Data Analysis:**
• `analyze [data type]` - Get data insights
• `compare [team1] vs [team2]` - Team comparisons

**Visualizations:**
• `create chart for [data]` - Generate charts
• `dashboard for [period]` - Create dashboards

**Session Management:**
• `status` - Show session information
• `reset` - Clear session context

**Example:** "Get forecast for retail marketing team for next quarter"
"""
            await cl.Message(content=help_msg).send()
            return
            
        elif user_input.lower() == "status":
            print(f"🔥 RAW STATUS COMMAND")
            session_data = cl.user_session.get('teams_session_data', {})
            user_info = session_data.get('user', {})
            
            # Get vector data store status
            vector_data_store = get_session_vector_data_store()
            forecast_results = vector_data_store.get_latest_results(session_id, query_type="forecast", limit=5)
            
            status_msg = f"""
📊 **Session Status**

🆔 **Session ID**: `{session_id}`
👤 **User**: {user_info.get('name', 'Unknown')}
📅 **Created**: {session_data.get('created_at', 'Unknown')}
🕐 **Last Active**: {session_data.get('last_active', 'Unknown')}

🎯 **Context Alignment**:
• **Context Manager**: {len(session_data.get('context', {}).get('teams', []))} teams in context
• **Vector Data Store**: {len(forecast_results)} forecast results stored
• **Last Query**: {session_data.get('context', {}).get('last_query', 'None')[:50]}...

📊 **Recent Vector Search Results**:
"""
            
            if forecast_results:
                for i, result in enumerate(forecast_results[:3], 1):
                    timestamp = result['timestamp'].strftime('%H:%M:%S')
                    status_msg += f"• [{i}] [{timestamp}] {result['business']}-{result['substream']}-{result['team']}\n"
            else:
                status_msg += "• No forecast data stored yet\n"

            status_msg += f"""
✅ **System Status**: All agents operational
🤖 **Agents**: {'Ready' if session_data.get('agents') else 'Will be created'}
🔗 **Data Store Alignment**: ✅ Context Manager + Vector Store using session `{session_id}`
"""
            await cl.Message(content=status_msg).send()
            return
        
        print(f"🔥 RAW PROCESSING - Regular user query detected")
        
        # Get or create agents for this session (prevents re-instantiation)
        agents = get_session_agents(session_id)
        
        print(f"🔥 RAW AGENTS: {[agent.name for agent in agents] if agents else 'None'}")
        
        # 📊 ENSURE DATA STORE CONTEXT IS ALIGNED WITH SESSION
        # This is critical - both context manager and vector data store must use same session ID
        try:
            vector_data_store = get_session_vector_data_store()
            fetch_forecasting_agent.set_data_store_context(vector_data_store, session_id)
            print(f"✅ Aligned vector data store with session: {session_id}")
        except Exception as e:
            print(f"⚠️ Failed to align data store context: {e}")
        
        # Create Teams user agent
        user_agent = TeamsHumanAgent(session_id)
        
        # Create group chat with session agents
        group_chat = GroupChat(agents, user_agent, session_id)
        
        print(f"🔥 RAW ORCHESTRATION - Starting group chat with user input:")
        print(f"   📝 Input: {user_input}")
        print(f"   🎭 Agents: {len(agents)} agents available")
        print(f"   🆔 Session: {session_id}")
        
        # Run the chat
        await group_chat.run_chat(user_input)
        
    except Exception as e:
        print(f"❌ Error in Teams main handler: {e}")
        import traceback
        print(traceback.format_exc())
        await cl.Message(content=f"⚠️ **System error:** {str(e)}").send()