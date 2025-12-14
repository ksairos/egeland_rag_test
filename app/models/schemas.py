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
    text = "text"

    text_image = "text_image"
    image = "image"

    audio_image = "audio_image"
    audio = "audio"
