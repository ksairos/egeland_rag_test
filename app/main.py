import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI, HTTPException, status, Security, Depends
from fastapi.security import APIKeyHeader
from langgraph.checkpoint.postgres import PostgresSaver

from app.core.config import settings
from app.services.agent.rag_agent import build_rag_agent
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
        app.state.rag_agent = build_rag_agent(checkpointer)
        yield


app = FastAPI(title="Тестовое", lifespan=lifespan)

app.include_router(health.router)
app.include_router(chat.router, dependencies=[Depends(verify_api_key)])
