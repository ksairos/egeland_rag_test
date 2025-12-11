import logging

from fastapi import FastAPI


app = FastAPI(title="Тестовое")

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@app.get("/health")
async def health_check():
    logger.info("Health Check")
    return {"status": "ok"}
