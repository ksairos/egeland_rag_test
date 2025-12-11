from sqlalchemy.ext.asyncio import AsyncSession
from app.models.chat_log import ChatLog


async def log_interaction(
    db: AsyncSession,
    user_id: str,
    user_query: str,
    ai_response: str,
    request_type: str = "text",
):
    """
    Записывает диалог в бд
    """
    new_log = ChatLog(
        user_id=user_id,
        user_query=user_query,
        ai_response=ai_response,
        request_type=request_type,
    )

    db.add(new_log)
    await db.commit()
    await db.refresh(new_log)
    return new_log
