import io
import logging
import os

import httpx
from aiogram import Router, F, types, Bot
from chatgpt_md_converter import telegram_format
from dotenv import load_dotenv

load_dotenv()

image_router = Router()
FASTAPI_ENDPOINT = os.environ.get("FASTAPI_URL") + "chat/text"
API_SECRET_KEY = os.environ.get("API_SECRET_KEY")


@image_router.message(F.photo)
async def invoke_image(message: types.Message, bot: Bot):
    waiting_message = await message.reply("Секунду...")

    photo = message.photo[-1].file_id
    title = message.photo[-1].file_unique_id
    file_buffer = io.BytesIO()

    logging.info("Downloading photo...")
    await bot.download(photo, destination=file_buffer)
    file_buffer.seek(0)

    files = {"image": (f"{title}.jpg", file_buffer, "image/jpeg")}

    caption = message.caption or ""

    data = {"user_id": str(message.from_user.id), "question": caption}

    async with httpx.AsyncClient() as client:
        try:
            logging.info("Sending PHOTO request to server...")
            headers = {"access_token": API_SECRET_KEY}
            response = await client.post(
                FASTAPI_ENDPOINT, files=files, data=data, timeout=60.0, headers=headers
            )

            logging.info(f"Server response: {response.json()}")
            if response.status_code == 200:
                server_resp = response.json()
                await waiting_message.edit_text(
                    telegram_format(f"{server_resp.get('response')}")
                )
            else:
                logging.error(f"Server error: {response.json()}")
                await waiting_message.edit_text("❌ Произошла ошибка, попробуйте позже")
        except Exception as e:
            logging.error(f"Server Exception: {str(e)}")
            await waiting_message.edit_text("Ошибка подключения, попробуйте позже")
