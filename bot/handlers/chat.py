import logging
import os

import httpx
from aiogram import Router, F, types
from chatgpt_md_converter import telegram_format
from dotenv import load_dotenv

load_dotenv()

chat_router = Router()
FASTAPI_ENDPOINT = os.environ.get("FASTAPI_URL") + "chat/text"
API_SECRET_KEY = os.environ.get("API_SECRET_KEY")


@chat_router.message(F.text)
async def invoke_text(message: types.Message):
    if message.text.startswith("/"):
        return

    try:
        async with httpx.AsyncClient() as client:
            logging.info("Sending TEXT request to server...")

            data = {"user_id": str(message.from_user.id), "question": message.text}
            headers = {"access_token": API_SECRET_KEY}
            response = await client.post(
                FASTAPI_ENDPOINT, data=data, timeout=60.0, headers=headers
            )
            if response.status_code == 200:
                server_resp = response.json()
                await message.reply(telegram_format(f"{server_resp.get('response')}"))
            else:
                logging.error(f"Server response: {response.json()}")
                await message.reply("❌ Произошла ошибка, попробуйте позже")
    except Exception as e:
        logging.error(f"Exception: {str(e)}")
        await message.reply("Ошибка подключения, попробуйте позже")
