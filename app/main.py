import logging

from fastapi import FastAPI

from app.services.agent.rag_agent import rag_agent

app = FastAPI(title="Тестовое")

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@app.get("/health")
async def health_check():
    logger.info("Health Check")
    return {"status": "ok"}

@app.post("/test")
async def test_rag_agent(question: str):
    logger.info("Testing RAG agent")
    model_response = rag_agent.invoke({"messages": [{"role": "user", "content": question}]})
    model_response = model_response["messages"][-1].content

    return {"response": model_response}
