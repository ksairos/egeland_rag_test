from datetime import datetime
from enum import Enum

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


class UserRequestType(str, Enum):
    textual = "textual"
    audio = "audio"
    image = "image"