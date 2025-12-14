import logging
from fastapi import (
    APIRouter,
    Request,
    HTTPException,
    Depends,
    BackgroundTasks,
    UploadFile,
    File,
    Form,
)
from langchain_core.messages import RemoveMessage, AIMessage
from langgraph.graph.state import CompiledStateGraph
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.models.schemas import (
    ChatResponse,
    UserRequestType,
)
from app.services.agent.audio import transcribe_audio
from app.services.agent.image import encode_image
from app.services.agent.rag_agent import system_prompt
from app.services.db_service import log_interaction

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/chat")


# DI для получения агента
def get_agent(request: Request) -> CompiledStateGraph:
    if not hasattr(request.app.state, "rag_agent"):
        raise HTTPException(status_code=500, detail="Agent not initialized")
    return request.app.state.rag_agent


@router.post("/text", response_model=ChatResponse)
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
            # IMPORTANT: Чтобы сократить количество токенов, желательно не сохранять base64 в истории.
            # IMPORTANT: Вместо этого добавить агента, описывающего фото, и сохранять только его ответ
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
            # IMPORTANT: Чтобы сократить количество токенов, желательно не сохранять base64 в истории.
            # IMPORTANT: Вместо этого добавить агента, описывающего фото, и сохранять только его ответ
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
            log_interaction,
            db,
            user_id,
            question,
            response_text,
            request_type,
        )

        return ChatResponse(user_id=user_id, response=response_text)

    except Exception as e:
        logger.error(f"Error processing request: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/audio", response_model=ChatResponse)
async def invoke_audio_agent(
    background_tasks: BackgroundTasks,
    user_id: str = Form(...),
    audio: UploadFile | None = File(default=None),
    image: UploadFile | None = File(default=None),
    agent=Depends(get_agent),
    db: AsyncSession = Depends(get_db),
):
    transcript = "изображение"
    try:
        if audio and image:
            # IMPORTANT: Чтобы сократить количество токенов, желательно не сохранять base64 в истории.
            # IMPORTANT: Вместо этого добавить агента, описывающего фото, и сохранять только его ответ
            logger.info(
                f"Processing audio '{audio.filename}' and image {image.filename}"
            )

            content = await image.read()
            image_base64 = encode_image(content)

            transcript = await transcribe_audio(audio)

            messages = {
                "messages": {
                    "role": "user",
                    "content": [
                        {
                            "type": "text",
                            "text": transcript,
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
            # IMPORTANT: Чтобы сократить количество токенов, желательно не сохранять base64 в истории.
            # IMPORTANT: Вместо этого добавить агента, описывающего фото, и сохранять только его ответ
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
            transcript = await transcribe_audio(audio)
            logger.info(f"Processing question '{transcript}' without images")
            messages = {"messages": {"role": "user", "content": transcript}}
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
            log_interaction,
            db,
            user_id,
            transcript,
            response_text,
            request_type,
        )

        return ChatResponse(user_id=user_id, response=response_text)

    except Exception as e:
        logger.error(f"Error processing request: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/delete_history")
async def delete_history(
    user_id: str = Form(...), agent: CompiledStateGraph = Depends(get_agent)
):
    try:
        config = {"configurable": {"thread_id": str(user_id)}}
        state = agent.get_state(config)

        delete_instructions = [
            RemoveMessage(id=msg.id) for msg in state.values.get("messages", [])
        ]
        restore_system_prompt = AIMessage(content=system_prompt)

        agent.update_state(
            config,
            {"messages": delete_instructions + [restore_system_prompt]},
        )

        return {"detail": "Successfully cleared chat history"}

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
