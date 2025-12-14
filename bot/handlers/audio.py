import io
import logging
import os

import httpx
from chatgpt_md_converter import telegram_format
from dotenv import load_dotenv
from aiogram import Router, F, types, Bot

load_dotenv()

audio_router = Router()
FASTAPI_ENDPOINT = os.environ.get("FASTAPI_URL") + "chat/audio"

@audio_router.message(F.voice)
async def invoke_audio(message: types.Message, bot: Bot):
    await message.reply("Пожалуйста, подождите...")

    audio = message.voice.file_id
    title = message.voice.file_unique_id

    file_buffer = io.BytesIO()

    logging.info("Downloading voice message...")
    await bot.download(audio, destination=file_buffer)
    file_buffer.seek(0)

    files = {"audio": (f"{title}.ogg", file_buffer, "audio/ogg")}
    data = {"user_id": str(message.from_user.id)}

    async with httpx.AsyncClient() as client:
        logging.info("Sending AUDIO request to server...")
        response = await client.post(FASTAPI_ENDPOINT, files=files, data=data, timeout=60.0)
        if response.status_code == 200:
            server_resp = response.json()
            await message.reply(telegram_format(f"{server_resp.get('response')}"))
        else:
            logging.error(f"Server response: {response.json()}")
            await message.reply(
                f"❌ Произошла ошибка, попробуйте позже"
            )

