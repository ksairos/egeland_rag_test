
from fastapi import FastAPI

from app.core.config import settings

print(settings.DATABASE_URL)