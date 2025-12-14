import logging
import os

import httpx
from aiogram import Router, F, types
from dotenv import load_dotenv

load_dotenv()

chat_router = Router()
FASTAPI_ENDPOINT = os.environ.get("FASTAPI_URL") + "chat/text"


@chat_router.message(F.text)
async def invoke_text(message: types.Message):
    if message.text.startswith("/"):
        return

    try:
        async with httpx.AsyncClient() as client:
            logging.info("Sending TEXT request to server...")

            data = {"user_id": str(message.from_user.id), "question": message.text}
            response = await client.post(FASTAPI_ENDPOINT, data=data, timeout=60.0)
            if response.status_code == 200:
                server_resp = response.json()
                await message.reply(f"{server_resp.get('response')}")
            else:
                await message.reply(
                    f"❌ Произошла ошибка, попробуйте позже: {response.status_code}"
                )
    except Exception as e:
        await message.reply(f"Ошибка подключения, попробуйте позже: {str(e)}")