import logging

from langchain.agents import AgentState
from langgraph.graph.state import CompiledStateGraph
from langchain.agents.middleware import before_model
from langgraph.graph.message import REMOVE_ALL_MESSAGES
from langchain_core.messages import RemoveMessage
from langgraph.runtime import Runtime
from typing import Any
from langchain_core.messages import AIMessage

from app.core.prompts import SYSTEM_PROMPT


def delete_all_messages(user_id: str, agent: CompiledStateGraph):
    config = {"configurable": {"thread_id": str(user_id)}}
    state = agent.get_state(config)

    delete_instructions = [
        RemoveMessage(id=msg.id) for msg in state.values.get("messages", [])
    ]
    restore_system_prompt = AIMessage(content=SYSTEM_PROMPT)

    agent.update_state(
        config,
        {"messages": delete_instructions + [restore_system_prompt]},
    )


@before_model
def trim_messages(
    state: AgentState,
    runtime: Runtime,
    num_to_keep: int = 3,  # TODO: Change to 10
) -> dict[str, Any] | None:
    messages = state["messages"]

    try:
        if len(messages) <= num_to_keep:
            return None

        first_msg = messages[0]
        while num_to_keep < len(messages) and messages[-num_to_keep].type == "tool":
            num_to_keep += 1

        recent_messages = [first_msg] + messages[-num_to_keep - 1 :]

        return {"messages": [RemoveMessage(id=REMOVE_ALL_MESSAGES), *recent_messages]}

    except Exception as e:
        logging.error(f"Error truncating messages: {e}")
        return {"messages": messages}
