import chainlit as cl
from context_manager.context_manager import ContextManager
from config import llm_config
from agents import fetch_forecasting_agent, forecasting_data_analyst_agent
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
    """Create and configure agents with async support"""
    agents = []
    for create_fn in [fetch_forecasting_agent.create_agent, forecasting_data_analyst_agent.create_agent]:
        agent = create_fn()
        print(f"Created agent: {agent.name}")
        print(f"Agent config: {agent.llm_config}")
        
        # Ensure the agent has async capabilities
        if not hasattr(agent, 'a_generate_reply'):
            print(f"Adding async support to {agent.name}")
            async def a_generate_reply(self, messages=None, sender=None, config=None):
                print(f"Async generate called for {self.name}")
                result = self.generate_reply(messages=messages, sender=sender, config=config)
                print(f"Async generate result: {result}")
                return result
            agent.a_generate_reply = a_generate_reply.__get__(agent)
        agents.append(agent)
    return agents

def get_chainlit_author_from_role(role):
    mapping = {
        "user": "You",
        "assistant": "Assistant",
        "Fetch-Volume-Forecast-Agent": "Forecast Agent",
        "Forecasting-Data-Analyst-Agent": "Data Analyst",
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
            # Wait for user input without displaying the prompt again
            response = await cl.AskUserMessage(content="Your response:").send()
            
            print(f"Debug - Raw response received: {response}")
            
            if response is None:
                print("Debug - No response received from user")
                return ""
            
            # Extract content based on response type
            content = None
            if isinstance(response, dict):
                # First try output field (Chainlit's new format)
                content = response.get('output')
                if content is None:
                    # Fallback to content field (older format)
                    content = response.get('content')
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
        self.user_agent = user_agent
        self.session_id = session_id
        self.messages = []
        self.message_hashes = set()
        self.last_speaker = None
        self.current_agent = None
        self.current_context = {
            "teams": [],
            "last_query": None,
            "current_comparison": None
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
        if not message or not message.get("content"):
            return
            
        # Update context based on message content
        content = message.get("content", "").lower()
        
        # Track team information when found
        if "business:" in content and "substream:" in content and "team:" in content:
            try:
                team_info = {
                    "business": content.split("business:")[1].split("\n")[0].strip(),
                    "substream": content.split("substream:")[1].split("\n")[0].strip(),
                    "team": content.split("team:")[1].split("\n")[0].strip()
                }
                if team_info not in self.current_context["teams"]:
                    self.current_context["teams"].append(team_info)
                    print(f"Added new team to context: {team_info}")
            except Exception as e:
                print(f"Error extracting team info: {e}")
        
        # Track comparison requests
        if "compare" in content:
            self.current_context["current_comparison"] = True
            print("Comparison mode activated")
        
        # Store last query if it's from user
        if message.get("role") == "user":
            self.current_context["last_query"] = content
            print(f"Updated last query: {content}")
        
        # Clean the message
        clean_message = {
            "role": message.get("role", "assistant"),
            "content": message["content"].strip()
        }
        
        # Add context information for agents
        if author and author.startswith("Fetch-Volume-Forecast"):
            context_info = f"\nCurrent context - Teams: {self.current_context['teams']}"
            if self.current_context["current_comparison"]:
                context_info += "\nComparison mode: Active"
            if self.current_context["last_query"]:
                context_info += f"\nLast query: {self.current_context['last_query']}"
            clean_message["content"] += context_info
        
        # Store in ChromaDB
        self._store_in_chroma(clean_message, author)
        
        msg_hash = self._hash_message(clean_message, author)
        
        # Skip if we've seen this message before
        if msg_hash in self.message_hashes:
            print(f"Debug - Skipping duplicate message: {msg_hash}")
            return
            
        print(f"Debug - Sending message: {clean_message} from {author}")
        print(f"Debug - Current context: {self.current_context}")
        
        # Only send to UI if:
        # 1. Not a system message
        # 2. Not from the same speaker as last message
        # 3. From the current active agent or is a user message that needs to be displayed
        if (author != "System" and 
            author != self.last_speaker and 
            (author == getattr(self.current_agent, 'name', None) or 
             (clean_message["role"] == "user" and not clean_message["content"].startswith("Your response:")))):
            
            # Remove "HUMAN INPUT REQUIRED" and context info from UI display
            display_content = clean_message["content"]
            if "==== HUMAN INPUT REQUIRED ====" in display_content:
                display_content = display_content.replace("==== HUMAN INPUT REQUIRED ====", "").strip()
            if "Current context -" in display_content:
                display_content = display_content.split("\nCurrent context -")[0].strip()
            
            await cl.Message(
                content=display_content,
                author=get_chainlit_author_from_role(author or clean_message["role"])
            ).send()
            self.last_speaker = author
        
        # Store message and hash
        self.messages.append(clean_message)
        self.message_hashes.add(msg_hash)
    
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
        """Run the group chat"""
        print("Debug - Starting group chat")
        
        # Initialize with clean initial message
        initial_msg = {"role": "user", "content": initial_message}
        # Store in ChromaDB and display to UI
        await self.send_message(initial_msg, "You")
        self.messages = [initial_msg]
        
        current_agent_idx = 0
        max_rounds = 10
        current_round = 0
        last_agent = None
        
        while current_round < max_rounds:
            self.current_agent = self.agents[current_agent_idx]
            print(f"\nDebug - Round {current_round + 1}, Agent: {self.current_agent.name}")
            
            # Get reply from current agent
            reply = await self._get_agent_reply(self.current_agent, self.messages.copy(), last_agent)
            if not reply:
                print(f"Debug - No reply from {self.current_agent.name}")
                break
            
            print(f"Debug - Agent reply received: {reply}")
            
            # Handle function calls if present
            if reply.get("function_call"):
                print(f"Debug - Function call detected: {reply['function_call']}")
                function_result = await self._execute_function(self.current_agent, reply["function_call"])
                
                if function_result:
                    print(f"Debug - Function executed successfully: {function_result}")
                    # Send function result and wait for agent's interpretation
                    self.messages.append(function_result)
                    interpretation = await self._get_agent_reply(self.current_agent, self.messages.copy(), last_agent)
                    if interpretation:
                        await self.send_message(interpretation, self.current_agent.name)
                    continue
                else:
                    print("Debug - Function execution failed")
            
            # For non-function messages, send the reply
            await self.send_message(reply, self.current_agent.name)
            last_agent = self.current_agent
            
            # Check if human input is needed
            if "==== HUMAN INPUT REQUIRED ====" in reply["content"]:
                print("Debug - Human input needed")
                human_reply = await self._get_human_reply(reply)
                
                if human_reply:
                    print(f"Debug - Human reply received: '{human_reply}'")
                    # Send the human reply to UI and store it
                    await self.send_message(human_reply, "You")
                    self.messages.append(human_reply)
                    continue
                else:
                    print("Debug - No valid human reply received")
                    break
            
            # Move to next agent only if current agent doesn't need to continue
            if not reply.get("content", "").endswith("==== DATA RETRIEVED ===="):
                current_agent_idx = (current_agent_idx + 1) % len(self.agents)
                if current_agent_idx == 0:
                    current_round += 1
                    print(f"Debug - Completed round {current_round}")
                self.current_agent = None  # Reset current agent when switching
    
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
            
            # Handle different reply formats
            if isinstance(reply, tuple) and len(reply) == 2:
                success, content = reply
                if success and content:
                    if isinstance(content, dict):
                        return {
                            "role": "assistant",
                            "content": content.get("content", ""),
                            "function_call": content.get("function_call")
                        }
                    return {"role": "assistant", "content": str(content)}
            elif isinstance(reply, dict):
                # Check for function call in content
                if reply.get("content"):
                    content = reply["content"]
                    if "{" in content and "}" in content:
                        try:
                            # Find the JSON object in the content
                            import json
                            import re
                            
                            # Find all JSON-like structures
                            json_matches = re.findall(r'\{[^{}]*\}', content)
                            for json_str in json_matches:
                                try:
                                    json_obj = json.loads(json_str)
                                    if json_obj.get("function_call") or (json_obj.get("name") == "fetch_forecast" and json_obj.get("arguments")):
                                        # Found a valid function call
                                        function_call = json_obj.get("function_call", json_obj)
                                        # Clean the content by removing the JSON
                                        clean_content = re.sub(r'\{[^{}]*\}', '', content).strip()
                                        return {
                                            "role": "assistant",
                                            "content": clean_content,
                                            "function_call": {
                                                "name": function_call.get("name"),
                                                "arguments": function_call.get("arguments")
                                            }
                                        }
                                except json.JSONDecodeError:
                                    continue
                        except Exception as e:
                            print(f"Error parsing function call: {e}")
                
                # If no function call found in content, return as is
                return {
                    "role": "assistant",
                    "content": reply.get("content", str(reply)),
                    "function_call": reply.get("function_call")
                }
            elif isinstance(reply, str):
                return {"role": "assistant", "content": reply}
            
            print("Debug - No valid reply format found")
            return None
            
        except Exception as e:
            print(f"Error in _get_agent_reply: {e}")
            import traceback
            print(traceback.format_exc())
            return None
    
    async def _get_human_reply(self, agent_message):
        """Get reply from human"""
        try:
            print("Debug - Getting human reply")
            response = await self.user_agent.get_human_input(agent_message["content"])
            
            if response and response.strip():
                print(f"Debug - Got human response: '{response}'")
                return {"role": "user", "content": response}
            
            print("Debug - No valid human response received")
            return None
            
        except Exception as e:
            print(f"Error in _get_human_reply: {e}")
            import traceback
            print(traceback.format_exc())
            return None

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

