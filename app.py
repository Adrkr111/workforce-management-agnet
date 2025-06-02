import chainlit as cl
from context_manager.context_manager import ContextManager
from config import llm_config
from agents import fetch_forecasting_agent, forecasting_data_analyst_agent
from autogen.agentchat.group.patterns import AutoPattern
from autogen.agentchat import initiate_group_chat

context_manager = ContextManager()

def create_forecasting_agents():
    return [
        fetch_forecasting_agent.create_agent(),
        forecasting_data_analyst_agent.create_agent()
    ]

def get_chainlit_author_from_role(role):
    mapping = {
        "user": "You",
        "assistant": "Assistant",
        "Fetch-Volume-Forecast-Agent": "Forecast Agent",
        "data-analyst-bot": "Data Analyst",
    }
    return mapping.get(role, role)

@cl.on_message
async def main(message: cl.Message):
    session_id = message.session_id if hasattr(message, "session_id") else "default"
    user_input = message.content

    # END/RESET
    if user_input.strip().lower() in ["end", "reset", "quit", "exit"]:
        context_manager.clear(session_id)
        await cl.Message(content="Session ended and context cleared. Start a new query!").send()
        return

    # Always fetch full session history
    chat_history = context_manager.get_history(session_id)
    print("context_manager",chat_history)


    # chat_history.append(user_msg)
    await cl.Message(content=user_input, author="You").send()

    # 2. Agents
    agent_list = create_forecasting_agents()
    print('*'*15,chat_history)
    print('*' * 15)
    with llm_config:
        pattern = AutoPattern(
            initial_agent=agent_list[0],
            agents=agent_list,
            user_agent=None,
            group_manager_args={
                "llm_config": llm_config,
                "is_termination_msg": lambda msg: True if "==== HUMAN INPUT REQUIRED ====" in msg else False,
            },
        )
        # Pass the FULL updated chat history to agents
        result, context, last_agent = initiate_group_chat(
            pattern=pattern,
            messages=[{'role':'user','content':user_input}] if len(chat_history)<1 else chat_history,
            max_rounds=4

        )

    # 3. Append all NEW agent responses to history and UI (only those after the last user turn)
    # Find agent replies that are new (after the latest user message you just added)
    # If result.chat_history repeats everything, filter by position or timestamp as needed


    await cl.Message(content=result.chat_history[-1]['content'], author='assistant').send()

    print(result.chat_history[-1]['content'])
    context_manager.add_message(session_id, {'role': 'user', 'content': user_input})
    context_manager.add_message(session_id, {'role':'assistant','content':result.chat_history[-1]['content']})

    # 4. Save updated chat history for the next turn

