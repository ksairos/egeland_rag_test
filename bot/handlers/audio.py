import logging
import os

from dotenv import load_dotenv
import httpx
from aiogram import Router, F, types

load_dotenv()

audio_router = Router()
FASTAPI_ENDPOINT = os.environ.get("FASTAPI_URL") + "chat/audio"