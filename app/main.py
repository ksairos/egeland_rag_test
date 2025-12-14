import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI
from langchain.agents import create_agent
from langgraph.checkpoint.postgres import PostgresSaver
from langgraph.graph.state import CompiledStateGraph

from app.core.config import settings
from app.models.schemas import CustomAgentState
from app.services.agent.rag_agent import (
    model,
    retrieve_docs,
    system_prompt,
    trim_messages,
)
from app.routers import chat, health

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    with PostgresSaver.from_conn_string(settings.POSTGRES_DB_URL) as checkpointer:
        checkpointer.setup()

        rag_agent: CompiledStateGraph = create_agent(
            model=model,
            tools=[retrieve_docs],
            state_schema=CustomAgentState,
            system_prompt=system_prompt,
            checkpointer=checkpointer,
            middleware=[trim_messages],
        )

        app.state.rag_agent = rag_agent

        yield


app = FastAPI(title="Тестовое", lifespan=lifespan)

app.include_router(health.router)
app.include_router(chat.router)
