import logging
from contextlib import asynccontextmanager
from datetime import datetime
from typing import Optional

from fastapi import (
    FastAPI,
    Request,
    HTTPException,
    Depends,
    BackgroundTasks,
    UploadFile,
    File,
    Form,
)
from langchain.agents import create_agent
from langchain_core.messages import HumanMessage
from langgraph.checkpoint.postgres import PostgresSaver
from langgraph.checkpoint.postgres.aio import AsyncPostgresSaver
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.core.database import get_db
from app.models.chat_log import ChatLog
from app.models.schemas import (
    CustomAgentState,
    ChatRequest,
    ChatResponse,
    UserRequestType,
)
from app.services.agent.image import encode_image
from app.services.agent.rag_agent import (
    model,
    retrieve_docs,
    system_prompt,
    trim_messages,
)
from app.services.db_service import log_interaction

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    with PostgresSaver.from_conn_string(settings.POSTGRES_DB_URL) as checkpointer:
        checkpointer.setup()

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


@app.post("/chat/audio", response_model=ChatResponse)
async def invoke_audio_agent(
    request: ChatRequest,
    background_tasks: BackgroundTasks,
    agent=Depends(get_agent),
    db: AsyncSession = Depends(get_db),
):
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
            log_interaction,
            db,
            request.user_id,
            UserRequestType.text,
            request.question,
            response_text,
        )

        return ChatResponse(user_id=request.user_id, response=response_text)

    except Exception as e:
        logger.error(f"Error processing request: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/chat/text")
async def invoke_text_agent(
    background_tasks: BackgroundTasks,
    user_id: str = Form(...),
    question: str | None = Form(default=None),
    image: UploadFile | None = File(default=None),
    agent=Depends(get_agent),
    db: AsyncSession = Depends(get_db),
):
    try:
        if question and image:
            logger.info(f"Processing question '{question}' and image {image.filename}")
            content = await image.read()
            image_base64 = encode_image(content)
            messages = {
                "messages": {
                    "role": "user",
                    "content": [
                        {
                            "type": "text",
                            "text": question,
                        },
                        {
                            "type": "image_url",
                            "image_url": {
                                "url": f"data:image/jpeg;base64,{image_base64}"
                            },
                        },
                    ],
                }
            }
            request_type = UserRequestType.text_image

        elif image:
            logger.info(f"Processing image {image.filename} without question")
            content = await image.read()
            image_base64 = encode_image(content)
            messages = {
                "messages": {
                    "role": "user",
                    "content": [
                        {
                            "type": "text",
                            "text": "Ответь на запрос пользователя, в зависимости от картинки",
                        },
                        {
                            "type": "image_url",
                            "image_url": {
                                "url": f"data:image/jpeg;base64,{image_base64}"
                            },
                        },
                    ],
                }
            }
            request_type = UserRequestType.text_image

        else:
            logger.info(f"Processing question '{question}' without images")
            messages = {"messages": {"role": "user", "content": question}}
            request_type = UserRequestType.text

        if not messages:
            logger.error("No messages returned from agent")
            raise ValueError("No messages returned from agent")

        logger.info(f"Sending messages to the agent: {messages}")
        model_response = agent.invoke(
            messages, {"configurable": {"thread_id": str(user_id)}}
        )

        response_text = model_response["messages"][-1].content

        # Update chat logs
        background_tasks.add_task(
            log_interaction, db, user_id, request_type, question, response_text
        )

        return ChatResponse(user_id=user_id, response=response_text)

    except Exception as e:
        logger.error(f"Error processing request: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/delete_history")
async def delete_history(user_id: str):
    pass
