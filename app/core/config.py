from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    API_SECRET_KEY: str = "super-secret-key"

    OPENAI_API_KEY: str

    POSTGRES_USER: str
    POSTGRES_PASSWORD: str
    POSTGRES_DB: str
    POSTGRES_HOST: str
    POSTGRES_PORT: int

    QDRANT_HOST: str
    QDRANT_HOST_OFFLINE: str = "localhost"
    QDRANT_PORT: int
    QDRANT_COLLECTION_NAME: str

    LANGSMITH_API_KEY: str
    LANGSMITH_TRACING: bool = False

    VECTOR_STORE_PATH: str = "qdrant_data"
    # SOURCE_DOCS_PATH: str = "source_docs"

    model_config = SettingsConfigDict(
        env_file=".env", env_file_encoding="utf-8", extra="ignore"
    )

    @property
    def DATABASE_URL(self) -> str:
        """Собираем DSN для асинхронного драйвера asyncpg"""
        return f"postgresql+asyncpg://{self.POSTGRES_USER}:{self.POSTGRES_PASSWORD}@{self.POSTGRES_HOST}:{self.POSTGRES_PORT}/{self.POSTGRES_DB}"

    # Без asyncpg
    @property
    def POSTGRES_DB_URL(self) -> str:
        return f"postgresql://{self.POSTGRES_USER}:{self.POSTGRES_PASSWORD}@{self.POSTGRES_HOST}:{self.POSTGRES_PORT}/{self.POSTGRES_DB}"


settings = Settings()
