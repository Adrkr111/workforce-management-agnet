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

# Initialize ChromaDB using existing client
chroma_client = get_chroma_client()

# Create a separate collection for agent conversations
def get_conversation_collection(session_id="default"):
    """Get or create a separate collection for agent conversations"""
    collection_name = f"agent_conversations_{session_id}"
    try:
        collection = chroma_client.get_or_create_collection(
            name=collection_name,
            metadata={
                "type": "agent_conversation",
                "session_id": session_id,
                "description": "Stores conversation history between agents and users",
                "hnsw:space": "cosine"  # Use same settings as forecast collection
            }
        )
        print(f"\nUsing conversation collection: {collection_name}")
        try:
            count = collection.count()
            print(f"Collection contains {count} messages")
        except Exception as e:
            print(f"Error getting collection count: {e}")
        return collection
    except Exception as e:
        print(f"Error creating conversation collection: {e}")
        return None

context_manager = ContextManager()

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
        print(f"Created agent: {agent.name}")
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

def get_chainlit_author_from_role(role):
    mapping = {
        "user": "You",
        "assistant": "Assistant",
        "Orchestrator-Agent": "Orchestrator",
        "Fetch-Volume-Forecast-Agent": "Forecast Agent",
        "Forecasting-Data-Analyst-Agent": "Data Analyst",
        "Data-Visualization-Agent": "Visualization Agent",
        "KPI-Data-Agent": "KPI Agent",
        "Workforce-Simulation-Agent": "Simulation Agent",
        "human": "You",
        "system": "System"
    }
    return mapping.get(role, role)

class ChainlitHumanAgent(ConversableAgent):
    def __init__(self):
        super().__init__(
            name="human",
            human_input_mode="ALWAYS",
            llm_config=False,
            code_execution_config=False,
            max_consecutive_auto_reply=0
        )
        self._session_id = None
    
    async def get_human_input(self, prompt: str) -> str:
        """Get human input through the UI"""
        if not self._session_id:
            raise RuntimeError("No active session")
        
        try:
            # Wait for user input without displaying the prompt
            response = await cl.AskUserMessage(content="").send()
            
            print(f"Debug - Raw response received: {response}")
            
            if response is None:
                print("Debug - No response received from user")
                return ""
            
            # Extract content based on response type
            content = None
            if isinstance(response, dict):
                content = response.get('output') or response.get('content')
            elif hasattr(response, 'output'):
                content = response.output
            elif hasattr(response, 'content'):
                content = response.content
            elif isinstance(response, str):
                content = response
            
            # Ensure we have a string
            if content is not None:
                content = str(content).strip()
                print(f"Debug - Extracted content: '{content}'")
                return content
            
            print("Debug - Could not extract content from response")
            return ""
            
        except Exception as e:
            print(f"Error in get_human_input: {e}")
            import traceback
            print(traceback.format_exc())
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
        self.current_context = {
            "teams": [],
            "last_query": None,
            "current_comparison": None,
            "visualizations": []
        }
        
        # Initialize ChromaDB collection for this session
        self.collection = get_conversation_collection(session_id)
        
        # Load existing context from ChromaDB
        self._load_existing_context()
    
    def _load_existing_context(self):
        """Load existing context from ChromaDB at initialization"""
        context = self._get_recent_context()
        if context:
            print("\nLoaded existing context from ChromaDB")
            # Parse context to update current_context
            self._parse_context_for_teams(context)
    
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
    
    def _store_in_chroma(self, message, author):
        """Store message in ChromaDB with metadata"""
        if not self.collection:
            print("Warning: No conversation collection available")
            return
            
        try:
            # Create unique ID for the message
            message_id = f"conv_{self.session_id}_{datetime.now().strftime('%Y%m%d_%H%M%S_%f')}"
            
            # Prepare metadata
            metadata = {
                "timestamp": datetime.now().isoformat(),
                "author": author,
                "role": message.get("role", "unknown"),
                "session_id": self.session_id,
                "type": "conversation_message"
            }
            
            # Add current context to metadata
            metadata.update({
                "teams": str(self.current_context["teams"]),
                "comparison_mode": str(self.current_context["current_comparison"]),
                "last_query": str(self.current_context["last_query"])
            })
            
            # Store message content and metadata
            self.collection.add(
                ids=[message_id],
                documents=[message.get("content", "")],
                metadatas=[metadata]
            )
            
            print(f"Debug - Stored conversation message in ChromaDB: {message_id}")
            
        except Exception as e:
            print(f"Error storing message in ChromaDB: {e}")
            import traceback
            print(traceback.format_exc())
    
    def _get_recent_context(self, limit=20):
        """Retrieve recent conversation context from ChromaDB"""
        if not self.collection:
            print("Warning: No conversation collection available")
            return None
            
        try:
            # Query the most recent messages with proper where clause format
            results = self.collection.get(
                limit=limit,
                where={
                    "$and": [
                        {"session_id": {"$eq": self.session_id}},
                        {"type": {"$eq": "conversation_message"}}
                    ]
                }
            )
            
            if not results or not results['documents']:
                return None
            
            # Format conversation history with clear separation
            formatted_history = ["=== Previous Conversation History ==="]
            for doc, metadata in zip(results['documents'], results['metadatas']):
                timestamp = datetime.fromisoformat(metadata['timestamp']).strftime('%Y-%m-%d %H:%M:%S')
                author = metadata['author']
                role = metadata['role']
                formatted_history.append(f"[{timestamp}] {author} ({role}): {doc}")
            
            return "\n".join(formatted_history)
            
        except Exception as e:
            print(f"Error retrieving context from ChromaDB: {e}")
            return None
    
    def _hash_message(self, message, author):
        """Create a unique hash for a message"""
        content = message.get("content", "").strip()
        return f"{author}:{content}"
    
    async def send_message(self, message, author=None):
        """Send a message to the UI and store it"""
        try:
            if get_chainlit_author_from_role(author)=='You':
                #i dont want to show the user messages on the ui so i will not send them
                clean_message = message.copy() if isinstance(message, dict) else {"role": "user", "content": str(message)}
                
            else:
                print("\nDebug - Message Handler - Starting message processing")
                print(f"Debug - Message type: {type(message)}")
                print(f"Debug - Message content type: {type(message.get('content', ''))}")
                print(f"Debug - Author: {author}")
                
                # Clean the message
                clean_message = message.copy() if isinstance(message, dict) else {"role": "user", "content": str(message)}
                print(f"Debug - Cleaned message: {clean_message}")
                
                # Handle function results
                if message.get("role") == "function":
                    print("Debug - Processing function result")
                    try:
                        content = message.get("content", "")
                        print(f"Debug - Function content: {content[:200]}...")  # First 200 chars
                        
                        if isinstance(content, str):
                            try:
                                # Try to parse as JSON
                                try:
                                    data = json.loads(content)
                                except:
                                    data=eval(content)
                                print("Debug - Successfully parsed content as JSON")
                                print("Debug - Author: ",get_chainlit_author_from_role(author))
                                if isinstance(data, dict):
                                    print(f"Debug - Data keys: {data.keys()}")
                                    
                                    # Check for visualization data
                                    if get_chainlit_author_from_role(author)=='Visualization Agent':
                                        print("Debug - Found visualization data")
                                        spec_data=data['spec']
                                        fig = go.Figure(spec_data["data"], spec_data["layout"])
                                        temp=cl.Plotly(name="Data Visualization Charts", figure=fig)
                                        elements = [
                                            temp
                                        ]
                                        await cl.Message(
                                            content="Here's the visualization:",
                                            elements=elements,
                                            author=get_chainlit_author_from_role(author)
                                        ).send()
                                        return
                    
                                    
                            except json.JSONDecodeError as e:
                                print(f"Debug - JSON parsing error: {e}")
                                pass
                        
                        # If not a visualization, send as regular function result
                        print("Debug - Sending regular function result")
                        await cl.Message(
                            content=content,
                            author=get_chainlit_author_from_role(author)
                        ).send()
                        
                    except Exception as e:
                        print(f"Debug - Error handling function result: {e}")
                        import traceback
                        print(f"Debug - Traceback: {traceback.format_exc()}")
                        await cl.Message(
                            content=message.get("content"),
                            author=get_chainlit_author_from_role(author)
                        ).send()
                else:
                    # Regular message
                    print("Debug - Sending regular message")
                    await cl.Message(
                        content=clean_message["content"],
                        author=get_chainlit_author_from_role(author or clean_message["role"])
                    ).send()
            
            # Store message and hash
            self.messages.append(clean_message)
            
            # Store in ChromaDB
            await self._store_message_in_chromadb(clean_message, author)
            
        except Exception as e:
            print(f"Debug - Error in send_message: {str(e)}")
            import traceback
            print(f"Debug - Traceback: {traceback.format_exc()}")
            await cl.Message(f"Error sending message: {str(e)}").send()
    
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
            
            print(f"Debug - Executing function {func_name} with args: {args}")
            result = func(args)
            print(f"Debug - Function result: {result}")
            
            # Format the result in a more readable way
            if isinstance(result, dict):
                if 'results' in result:
                    return {
                        "role": "function",
                        "name": func_name,
                        "content": result['results']
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
            print(f"Error executing function: {e}")
            import traceback
            print(traceback.format_exc())
            return None
    
    async def run_chat(self, initial_message):
        """Modified to use orchestrator-based routing"""
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
                
                # Check for agent delegation patterns
                content = response.get("content", "").lower()
                if "fetch-volume-forecast-agent" in content or "[fetch-volume-forecast-agent]" in content or "fetch-volume-forecast-agent:" in content:
                    # Delegate to Fetch-Volume-Forecast-Agent
                    fetch_agent = next(a for a in self.agents if a.name == "Fetch-Volume-Forecast-Agent")
                    self.current_agent = fetch_agent
                    fetch_response = await self._get_agent_reply(
                        fetch_agent,
                        self.messages
                    )
                    if fetch_response:
                        await self.send_message(fetch_response, fetch_agent.name)
                elif "data-visualization-agent" in content or "[data-visualization-agent]" in content or "data-visualization-agent:" in content:
                    # Delegate to Data-Visualization-Agent
                    viz_agent = next(a for a in self.agents if a.name == "Data-Visualization-Agent")
                    self.current_agent = viz_agent
                    viz_response = await self._get_agent_reply(
                        viz_agent,
                        self.messages
                    )
                    if viz_response:
                        await self.send_message(viz_response, viz_agent.name)
                elif "forecasting-data-analyst-agent" in content or "[forecasting-data-analyst-agent]" in content or "forecasting-data-analyst-agent:" in content:
                    # Delegate to Forecasting-Data-Analyst-Agent
                    analyst_agent = next(a for a in self.agents if a.name == "Forecasting-Data-Analyst-Agent")
                    self.current_agent = analyst_agent
                    analyst_response = await self._get_agent_reply(
                        analyst_agent,
                        self.messages
                    )
                    if analyst_response:
                        await self.send_message(analyst_response, analyst_agent.name)
                elif "kpi-data-agent" in content or "[kpi-data-agent]" in content or "kpi-data-agent:" in content:
                    # Delegate to KPI-Data-Agent
                    kpi_agent = next(a for a in self.agents if a.name == "KPI-Data-Agent")
                    self.current_agent = kpi_agent
                    kpi_response = await self._get_agent_reply(
                        kpi_agent,
                        self.messages
                    )
                    if kpi_response:
                        await self.send_message(kpi_response, kpi_agent.name)
                elif "workforce-simulation-agent" in content or "[workforce-simulation-agent]" in content or "workforce-simulation-agent:" in content:
                    # Delegate to Workforce-Simulation-Agent
                    workforce_simulation_agent = next(a for a in self.agents if a.name == "Workforce-Simulation-Agent")
                    self.current_agent = workforce_simulation_agent
                    workforce_simulation_response = await self._get_agent_reply(
                        workforce_simulation_agent,
                        self.messages
                    )
                    if workforce_simulation_response:
                        await self.send_message(workforce_simulation_response, workforce_simulation_agent.name)
            
            # Process orchestrator's response and delegate to appropriate agents
            while True:
                if not response or "TERMINATE" in response.get("content", ""):
                    break
                    
                # Check if response contains visualization spec
                if "spec" in response.get("content", ""):
                    try:
                        data = json.loads(response["content"])
                        if isinstance(data, dict):
                            if "type" in data and data["type"] == "vega-lite" and "spec" in data:
                                # Send Vega-Lite visualization to UI
                                elements = [
                                    cl.Vega(data["spec"])
                                ]
                                await cl.Message(
                                    content="Here's the visualization you requested:",
                                    elements=elements
                                ).send()
                    except:
                        pass
                
                # Get next message from user
                user_message = await self._get_human_reply(response)
                if not user_message:
                    break
            
                # Store user message
                await self.send_message(user_message, "You")
                
                # Route through orchestrator again
                response = await self._get_agent_reply(
                    self.orchestrator,
                    self.messages
                )
                
                if response:
                    # Send orchestrator's response to UI
                    await self.send_message(response, self.orchestrator.name)
                    
                    # Check for agent delegation again
                    content = response.get("content", "").lower()
                    if "fetch-volume-forecast-agent" in content or "[fetch-volume-forecast-agent]" in content or "fetch-volume-forecast-agent:" in content:
                        # Delegate to Fetch-Volume-Forecast-Agent
                        fetch_agent = next(a for a in self.agents if a.name == "Fetch-Volume-Forecast-Agent")
                        self.current_agent = fetch_agent
                        fetch_response = await self._get_agent_reply(
                            fetch_agent,
                            self.messages
                        )
                        if fetch_response:
                            await self.send_message(fetch_response, fetch_agent.name)
                    elif "data-visualization-agent" in content or "[data-visualization-agent]" in content or "data-visualization-agent:" in content:
                        # Delegate to Data-Visualization-Agent
                        viz_agent = next(a for a in self.agents if a.name == "Data-Visualization-Agent")
                        self.current_agent = viz_agent
                        viz_response = await self._get_agent_reply(
                            viz_agent,
                            self.messages
                        )
                        if viz_response:
                            await self.send_message(viz_response, viz_agent.name)
                    elif "forecasting-data-analyst-agent" in content or "[forecasting-data-analyst-agent]" in content or "forecasting-data-analyst-agent:" in content:
                        # Delegate to Forecasting-Data-Analyst-Agent
                        analyst_agent = next(a for a in self.agents if a.name == "Forecasting-Data-Analyst-Agent")
                        self.current_agent = analyst_agent
                        analyst_response = await self._get_agent_reply(
                            analyst_agent,
                            self.messages
                        )
                        if analyst_response:
                            await self.send_message(analyst_response, analyst_agent.name)
                    elif "kpi-data-agent" in content or "[kpi-data-agent]" in content or "kpi-data-agent:" in content:
                        # Delegate to KPI-Data-Agent
                        kpi_agent = next(a for a in self.agents if a.name == "KPI-Data-Agent")
                        self.current_agent = kpi_agent
                        kpi_response = await self._get_agent_reply(
                            kpi_agent,
                            self.messages
                        )
                        if kpi_response:
                            await self.send_message(kpi_response, kpi_agent.name)
                    elif "workforce-simulation-agent" in content or "[workforce-simulation-agent]" in content or "workforce-simulation-agent:" in content:
                        # Delegate to Workforce-Simulation-Agent
                        workforce_simulation_agent = next(a for a in self.agents if a.name == "Workforce-Simulation-Agent")
                        self.current_agent = workforce_simulation_agent
                        workforce_simulation_response = await self._get_agent_reply(
                            workforce_simulation_agent,
                            self.messages
                        )
                        if workforce_simulation_response:
                            await self.send_message(workforce_simulation_response, workforce_simulation_agent.name)
                
        except Exception as e:
            print(f"Error in run_chat: {e}")
            import traceback
            print(traceback.format_exc())
            await cl.Message(
                content=f"I encountered an error: {str(e)}. Please try again."
            ).send()
    
    async def _get_agent_reply(self, agent, messages, last_agent=None):
        """Get a reply from an agent"""
        try:
            print(f"\nDebug - Getting reply from agent: {agent.name}")
            
            # Get recent context from ChromaDB
            context = self._get_recent_context()
            if context:
                print(f"Debug - Adding conversation context from ChromaDB")
                context_msg = {
                    "role": "system",
                    "content": f"Previous conversation context:\n{context}\n\nCurrent teams in context: {self.current_context['teams']}\nComparison mode: {'Active' if self.current_context['current_comparison'] else 'Inactive'}\nLast query: {self.current_context['last_query']}"
                }
                messages = [context_msg] + messages
            
            print(f"Debug - Messages being processed: {messages}")
            
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
            
            print(f"Debug - Raw agent reply: {reply}")
            
            # Handle function calls in the reply
            if isinstance(reply, dict):
                # First check for direct function_call
                if reply.get("function_call"):
                    function_call = reply["function_call"]
                    if hasattr(agent, "function_map"):
                        func_name = function_call.get("name")
                        if func_name in agent.function_map:
                            func = agent.function_map[func_name]
                            args = function_call.get("arguments", "")
                            print(f"Debug - {agent.name} executing function {func_name} with args: {args}")
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
                                        print(f"Debug - {agent.name} executing function {func_name} with args: {args}")
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
                    "content": "Maximum number of consecutive auto-replies reached. Please provide input to continue."
                }

            return {
                "role": "assistant",
                "content": reply.get("content", "") if isinstance(reply, dict) else str(reply)
            }
            
        except Exception as e:
            print(f"Error in _get_agent_reply: {e}")
            import traceback
            print(traceback.format_exc())
            return None
    
    async def _get_human_reply(self, agent_message):
        """Get reply from human"""
        try:
            print("Debug - Getting human reply")
            response = await self.user_agent.get_human_input("")  # Remove prompt text
            
            if response and response.strip():
                print(f"Debug - Got human response: '{response}'")
                # Return simple string content, not nested structure
                return {"role": "user", "content": response.strip()}
            
            print("Debug - No valid human response received")
            return None
            
        except Exception as e:
            print(f"Error in _get_human_reply: {e}")
            import traceback
            print(traceback.format_exc())
            return None

    async def _store_message_in_chromadb(self, message, author):
        """Store message in ChromaDB with metadata"""
        if not self.collection:
            print("Warning: No conversation collection available")
            return
            
        try:
            # Create unique ID for the message
            message_id = f"conv_{self.session_id}_{datetime.now().strftime('%Y%m%d_%H%M%S_%f')}"
            
            # Prepare metadata
            metadata = {
                "timestamp": datetime.now().isoformat(),
                "author": author,
                "role": message.get("role", "unknown"),
                "session_id": self.session_id,
                "type": "conversation_message"
            }
            
            # Add current context to metadata
            metadata.update({
                "teams": str(self.current_context["teams"]),
                "comparison_mode": str(self.current_context["current_comparison"]),
                "last_query": str(self.current_context["last_query"])
            })
            
            # Store message content and metadata
            self.collection.add(
                ids=[message_id],
                documents=[message.get("content", "")],
                metadatas=[metadata]
            )
            
            print(f"Debug - Stored conversation message in ChromaDB: {message_id}")
            
        except Exception as e:
            print(f"Error storing message in ChromaDB: {e}")
            import traceback
            print(traceback.format_exc())

@cl.on_chat_start
async def on_chat_start():
    """Initialize the chat session"""
    # Get a stable session ID from Chainlit
    session_id = cl.user_session.get('id')
    print(f"\nStarting new chat session: {session_id}")
    
    # Store the session ID in user session for reuse
    cl.user_session.set('stable_session_id', session_id)

@cl.on_message
async def main(message: cl.Message):
    # Get the stable session ID
    session_id = cl.user_session.get('stable_session_id')
    if not session_id:
        session_id = cl.user_session.get('id')
        cl.user_session.set('stable_session_id', session_id)
    
    print(f"\nProcessing message with session ID: {session_id}")
    user_input = message.content

    # END/RESET
    if user_input.strip().lower() in ["end", "reset", "quit", "exit"]:
        context_manager.clear(session_id)
        await cl.Message(content="Session ended and context cleared. Start a new query!").send()
        return

    # Create agents and user agent
    print("\nCreating agents...")
    agents = create_agents()
    user_agent = ChainlitHumanAgent()
    user_agent._session_id = session_id
    
    # Create and run group chat with session ID
    print(f"\nStarting group chat for session: {session_id}")
    group_chat = GroupChat(agents, user_agent, session_id)
    
    try:
        await group_chat.run_chat(user_input)
    except Exception as e:
        print(f"Error in group chat: {e}")
        import traceback
        print(traceback.format_exc())
        await cl.Message(content=f"An error occurred: {str(e)}").send()

