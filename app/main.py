import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI, Request, HTTPException, Depends
from langchain.agents import create_agent
from langgraph.checkpoint.postgres.aio import AsyncPostgresSaver

from app.core.config import settings
from app.models.schemas import CustomAgentState, ChatRequest, ChatResponse
from app.services.agent.rag_agent import model, retrieve_docs, system_prompt

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):

    async with AsyncPostgresSaver.from_conn_string(settings.POSTGRES_DB_URL) as checkpointer:
        await checkpointer.setup()

        rag_agent = create_agent(
            model=model,
            tools=[retrieve_docs],
            state_schema=CustomAgentState,
            system_prompt=system_prompt,
            checkpointer=checkpointer
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


@app.post("/test", response_model=ChatResponse)
async def test_rag_agent(request: ChatRequest, agent = Depends(get_agent)): #TODO: add Telegram message schema
    logger.info("Testing RAG agent")
    try:
        model_response = await agent.ainvoke(
            {
                "messages": [{"role": "user", "content": request.question}],
                "user_id": str(request.user_id)
             },
            {"configurable": {"thread_id": str(request.user_id)}} # Только 1 thread на пользователя
        )
        messages = model_response.get("messages", [])

        if not messages:
            raise ValueError("No messages returned from agent")

        response_text = model_response["messages"][-1].content

        return ChatResponse(user_id=request.user_id, response=response_text)


    except Exception as e:
        logger.error(f"Error processing request: {e}")
        raise HTTPException(status_code=500, detail=str(e))
