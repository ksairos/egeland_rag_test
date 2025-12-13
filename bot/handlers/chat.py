import io
import json
import logging

import httpx
from aiogram import Router, F, types, Bot

from app.models.schemas import ChatRequest
from app.services.agent.image import encode_image

chat_router = Router()
FASTAPI_URL = "http://localhost:8000/chat/text"


@chat_router.message(F.text)
async def invoke_text(message: types.Message):
    if message.text.startswith("/"):
        return
    await message.answer(message.text)


@chat_router.message(F.photo)
async def invoke_text_photo(message: types.Message, bot: Bot):
    photo = message.photo[-1].file_id
    title = message.photo[-1].file_unique_id
    file_buffer = io.BytesIO()

    logging.info(f"Downloading photo: {photo}")
    await bot.download(photo, destination=file_buffer)
    file_buffer.seek(0)

    files = {"files": (f"{title}.jpg", file_buffer, "image/jpeg")}

    caption = message.caption or ""

    data = {"user_id": str(message.from_user.id), "question": caption}

    async with httpx.AsyncClient() as client:
        try:
            logging.info(
                f"Sending request to server: \n\nDATA: {data}\n\nFILES: {files}"
            )
            # 'data' handles form fields, 'files' handles file uploads
            response = await client.post(FASTAPI_URL, files=files, data=data)

            logging.info(f"Server response: {response.json()}")
            if response.status_code == 200:
                server_resp = response.json()
                await message.reply(
                    f"✅ Uploaded!\nServer saw caption: '{server_resp.get('response')}'"
                )
            else:
                await message.reply(f"❌ Server Error: {response.status_code}")

        except Exception as e:
            await message.reply(f"Connection failed: {str(e)}")

    if message.caption:
        pass

    # await message.answer(f"Photo received! Size: {width}x{height}")
