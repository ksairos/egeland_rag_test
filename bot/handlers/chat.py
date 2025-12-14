import io
import logging

import httpx
from aiogram import Router, F, types, Bot


chat_router = Router()
FASTAPI_URL = "http://app:8000/chat/text"


@chat_router.message(F.text)
async def invoke_text(message: types.Message):
    if message.text.startswith("/"):
        return

    try:
        async with httpx.AsyncClient() as client:
            logging.info("Sending TEXT request to server...")

            data = {"user_id": str(message.from_user.id), "question": message.text}
            response = await client.post(FASTAPI_URL, data=data, timeout=60.0)
            if response.status_code == 200:
                server_resp = response.json()
                await message.reply(f"{server_resp.get('response')}")
            else:
                await message.reply(
                    f"❌ Произошла ошибка, попробуйте позже: {response.status_code}"
                )
    except Exception as e:
        await message.reply(f"Ошибка подключения, попробуйте позже: {str(e)}")


@chat_router.message(F.photo)
async def invoke_text_photo(message: types.Message, bot: Bot):
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

            response = await client.post(FASTAPI_URL, files=files, data=data, timeout=60.0)

            logging.info(f"Server response: {response.json()}")
            if response.status_code == 200:
                server_resp = response.json()
                await message.reply(f"{server_resp.get('response')}'")
            else:
                await message.reply(
                    f"❌ Произошла ошибка, попробуйте позже: {response.status_code}"
                )
        except Exception as e:
            await message.reply(f"Ошибка подключения, попробуйте позже: {str(e)}")
