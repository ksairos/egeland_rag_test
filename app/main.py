import logging
from contextlib import asynccontextmanager
from datetime import datetime

from fastapi import FastAPI, Request, HTTPException, Depends, BackgroundTasks
from langchain.agents import create_agent
from langgraph.checkpoint.postgres.aio import AsyncPostgresSaver
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.core.database import get_db
from app.models.chat_log import ChatLog
from app.models.schemas import CustomAgentState, ChatRequest, ChatResponse, UserRequestType
from app.services.agent.rag_agent import (
    model,
    retrieve_docs,
    system_prompt,
    trim_messages,
)

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    async with AsyncPostgresSaver.from_conn_string(
        settings.POSTGRES_DB_URL
    ) as checkpointer:
        await checkpointer.setup()

        rag_agent = create_agent(
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


@app.get("/health")
async def health_check():
    logger.info("Health Check")
    return {"status": "ok"}


# DI для получения агента
def get_agent(request: Request):
    if not hasattr(request.app.state, "rag_agent"):
        raise HTTPException(status_code=500, detail="Agent not initialized")
    return request.app.state.rag_agent


async def add_chat_log(
    db: AsyncSession, user_id: str, request_type: str, user_query: str, ai_response: str
):
    new_log = ChatLog(
        user_id=user_id,
        request_type=request_type,
        user_query=user_query,
        ai_response=ai_response,
        created_at=datetime.now(),  # Explicitly set time
    )

    db.add(new_log)
    await db.commit()


@app.post("/chat", response_model=ChatResponse)
async def invoke_rag_agent(
    request: ChatRequest,
    background_tasks: BackgroundTasks,
    agent=Depends(get_agent),
    db: AsyncSession = Depends(get_db),
):
    logger.info("Testing RAG agent")
    try:
        model_response = await agent.ainvoke(
            {
                "messages": [{"role": "user", "content": request.question}],
                "user_id": str(request.user_id),
            },
            {
                "configurable": {"thread_id": str(request.user_id)}
            },  # Только 1 thread на пользователя
        )
        messages = model_response.get("messages", [])

        if not messages:
            raise ValueError("No messages returned from agent")

        response_text = model_response["messages"][-1].content

        # Update chat logs
        background_tasks.add_task(
            add_chat_log,
            db,
            request.user_id,
            UserRequestType.textual,
            request.question,
            response_text
        )

        return ChatResponse(user_id=request.user_id, response=response_text)

    except Exception as e:
        logger.error(f"Error processing request: {e}")
        raise HTTPException(status_code=500, detail=str(e))
