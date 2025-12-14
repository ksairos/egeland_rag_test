# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Development Commands

### Running the Application
- **Development (local)**: `uv sync && uvicorn app.main:app --reload --host 0.0.0.0 --port 8000`
- **Docker services**: `docker compose up -d` (starts PostgreSQL and Qdrant)
- **Full Docker stack**: `docker compose up --build`
- **Bot only**: `python -m bot.bot`
- **Combined (bot + API)**: `./start.sh`

### Testing
- **Run tests**: `pytest`
- **Run specific test**: `pytest tests/test_main.py`

### Database
- **Run migrations**: `alembic upgrade head`
- **Create migration**: `alembic revision --autogenerate -m "description"`

### Dependencies
- **Install dependencies**: `uv sync`
- **Add dependency**: `uv add package_name`

## Architecture Overview

### Project Structure
- **`app/`**: FastAPI web application
  - `main.py`: Main FastAPI app with RAG agent endpoint
  - `core/`: Configuration and database setup
  - `models/`: SQLAlchemy models and Pydantic schemas
  - `services/`: Business logic including RAG agent implementation
- **`bot/`**: Telegram bot using aiogram
  - `bot.py`: Main bot runner
  - `handlers/`: Message handlers for chat and audio
- **`data_pipeline/`**: Vector ingestion pipeline for Qdrant
- **`migrations/`**: Alembic database migrations

### Core Components

**RAG System (`app/services/agent/rag_agent.py`)**:
- Uses OpenAI GPT-4o-mini with LangGraph for agent orchestration
- Hybrid retrieval with dense (OpenAI embeddings) + sparse (BM25) vectors
- Qdrant vector database for document storage
- PostgreSQL checkpoint system for conversation persistence

**Dual Interface**:
- FastAPI REST API (`/chat/text` endpoint)
- Telegram bot with audio/image support via aiogram

**Infrastructure**:
- Docker Compose with PostgreSQL, Qdrant, and application services
- Environment-based configuration via Pydantic Settings
- Async/await throughout using asyncpg and async SQLAlchemy

### Key Dependencies
- **LangChain/LangGraph**: Agent framework with tool calling
- **Qdrant**: Vector database with hybrid search
- **FastAPI**: Async web framework
- **aiogram**: Telegram Bot API framework
- **SQLAlchemy + Alembic**: Database ORM and migrations
- **uv**: Python package manager

### Configuration
Environment variables required (see `.env`):
- `OPENAI_API_KEY`, `BOT_TOKEN`
- PostgreSQL: `POSTGRES_*` variables
- Qdrant: `QDRANT_*` variables
- Optional: `LANGSMITH_*` for tracing