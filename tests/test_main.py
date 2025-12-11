from app.models.chat_log import ChatLog


# Проверка /health
async def test_health_check(ac):
    response = await ac.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "ok"


# Unit-тест модели (без записи в БД, просто проверка создания объекта)
def test_chat_log_model_creation():
    log = ChatLog(user_id="test_user_1", user_query="Hello", ai_response="Hi there")
    assert log.user_id == "test_user_1"
    assert log.user_query == "Hello"
    assert log.ai_response == "Hi there"
