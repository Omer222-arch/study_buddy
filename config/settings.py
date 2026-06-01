from pathlib import Path

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


def get_project_root() -> Path:
    return Path(__file__).resolve().parent.parent


class Settings(BaseSettings):
    project_root: Path = Field(default_factory=get_project_root)
    chroma_persist_directory: Path = Field(default_factory=lambda: get_project_root() / "db" / "chroma")
    chroma_collection_name: str = "studybuddy"
    embedding_model_name: str = "all-MiniLM-L6-v2"
    embedding_device: str = "cpu"
    openai_api_key: str | None = None
    tavily_api_key: str | None = None
    pinecone_api_key: str | None = None
    pinecone_environment: str | None = None

    model_config = SettingsConfigDict(
        env_file=get_project_root() / ".env",
        case_sensitive=False,
    )


settings = Settings()
