import logging
import os

import httpx
from aiogram import Router, F, types
from aiogram.filters import CommandStart, Command
from aiogram.types import Message
from chatgpt_md_converter import telegram_format
from dotenv import load_dotenv

load_dotenv()

user_router = Router()
FASTAPI_ENDPOINT = os.environ.get("FASTAPI_URL") + "delete_history"


@user_router.message(CommandStart())
async def user_start(message: Message):
    """Команда /start"""
    await message.answer(telegram_format("✨ Давай вместе изучать корейский язык!"))


@user_router.message(Command("clear_history"))
async def clear_history(message: Message):
    """Удаляем историю"""
    async with httpx.AsyncClient() as client:
        logging.info("Removing chat history...")
        data = {"user_id": str(message.from_user.id)}
        response = await client.post(FASTAPI_ENDPOINT, data=data, timeout=60.0)
        if response.status_code == 200:
            logging.info("Successfully removed chat history.")
            await message.answer("История очищена")
        else:
            logging.error(f"Server response: {response.json()}")
            await message.answer("❌ Произошла ошибка, попробуйте позже")
