import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI, HTTPException, status, Security, Depends
from fastapi.security import APIKeyHeader
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

api_key_header = APIKeyHeader(name="access_token", auto_error=False)


async def verify_api_key(api_key: str = Security(api_key_header)):
    if api_key == settings.API_SECRET_KEY:
        return api_key
    raise HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Invalid or missing API Key",
    )


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
app.include_router(chat.router, dependencies=[Depends(verify_api_key)])
