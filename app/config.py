import os
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    API_SECRET_KEY: str
    OPENAI_API_KEY: str
    DATABASE_URL: str

    VECTOR_STORE_PATH: str = "vector_store"
    SOURCE_DOCS_PATH: str = "source_docs"

    model_config = SettingsConfigDict(env_file=".env", env_ignore_empty=True)


settings = Settings()