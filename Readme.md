# API Документация

## Базовая информация

**Base URL:** `http://localhost:8000` и `http://app:8000`

**Аутентификация:** Все эндпоинты чата требуют API ключ в заголовке `access_token`

## Эндпоинты

### 1. Health Check

**GET** `/health`

Проверка статуса API

**Ответ:**
```json
{
  "status": "ok"
}
```

### 2. Текст + изображение

**POST** `/chat/text`

Отправка текста, изображения или все вместе
**Headers:**
```
Content-Type: multipart/form-data
access_token: YOUR_API_KEY
```

**Параметры (Form Data):**
- `user_id` (string, обязательный) - ID пользователя
- `question` (string, опциональный) - Запрос к AI ассистенту
- `image` (file, опциональный) - Изображение

**Ответ:**
```json
{
  "user_id": "user123",
  "response": "Ответ от AI агента"
}
```

---

### 3. Аудио чат с изображением

**POST** `/chat/audio`

Отправка аудио (голосовое), изображения или все вместе

**Headers:**
```
Content-Type: multipart/form-data
access_token: YOUR_API_KEY
```

**Параметры (Form Data):**
- `user_id` (string, обязательный) - ID пользователя
- `audio` (file, опциональный) - Аудио файл
- `image` (file, опциональный) - Изображение

**Ответ:**
```json
{
  "user_id": "user123",
  "response": "Ответ от AI агента"
}
```

---

### 4. Удаление истории чата

**POST** `/chat/delete_history`

Очищает историю чата для указанного пользователя

**Headers:**
```
Content-Type: multipart/form-data
access_token: YOUR_API_KEY
```

**Параметры (Form Data):**
- `user_id` (string, обязательный) - Уникальный идентификатор пользователя

**Ответ:**
```json
{
  "detail": "Successfully cleared chat history"
}
```
---

## Особенности работы API

1. **User ID** - используется для сохранения истории чата. Один user_id = один thread

2. **Multimodal поддержка** - API поддерживает текст, изображения и аудио в любых комбинациях

3. **Форматы файлов:**
   - Изображения: PNG, JPG, JPEG (пока только JPEG)
   - Аудио: поддерживаемые OpenAI Whisper форматы (пока только .ogg для голосовых)

4. **Контекст разговора** - сохраняется автоматически по user_id в PostgreSQL

5. **Background processing** - логирование взаимодействий происходит асинхронно