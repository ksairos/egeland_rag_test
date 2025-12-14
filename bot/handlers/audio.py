import os

from dotenv import load_dotenv
from aiogram import Router

load_dotenv()

audio_router = Router()
FASTAPI_ENDPOINT = os.environ.get("FASTAPI_URL") + "chat/audio"
