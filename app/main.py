
from fastapi import FastAPI

from app.core.config import settings

app = FastAPI(
    title="Тестовое"
)

@app.get("/health")
async def health_check():
    return {"status": "ok"}

print(settings.model_dump())
