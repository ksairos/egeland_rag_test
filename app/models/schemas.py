from langchain.agents import AgentState
from pydantic import BaseModel


class CustomAgentState(AgentState):
    user_id: str

class ChatRequest(BaseModel):
    user_id: str
    question: str

class ChatResponse(BaseModel):
    user_id: str
    response: str