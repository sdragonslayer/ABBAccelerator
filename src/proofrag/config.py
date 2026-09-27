from __future__ import annotations

from functools import lru_cache
from pathlib import Path
from typing import Literal

from pydantic import Field, model_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Runtime configuration loaded from environment variables and ``.env``."""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_prefix="PROOFRAG_",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    app_name: str = "ProofRAG Maintenance Intelligence"
    environment: Literal["development", "test", "production"] = "development"
    host: str = "127.0.0.1"
    port: int = Field(default=8000, ge=1, le=65535)
    data_dir: Path = Path("data")
    database_path: Path = Path("data/proofrag.db")
    max_upload_mb: int = Field(default=30, ge=1, le=250)
    enable_ocr: bool = False

    default_top_k: int = Field(default=6, ge=1, le=20)
    bm25_weight: float = Field(default=0.60, ge=0, le=1)
    vector_weight: float = Field(default=0.40, ge=0, le=1)
    min_query_coverage: float = Field(default=0.34, ge=0, le=1)
    min_absolute_similarity: float = Field(default=0.08, ge=0, le=1)
    embedding_dimensions: int = Field(default=384, ge=64, le=4096)

    answer_provider: Literal["extractive", "openai-compatible"] = "extractive"
    llm_base_url: str = "https://api.openai.com/v1"
    llm_api_key: str = ""
    llm_model: str = ""
    llm_timeout_seconds: float = Field(default=45, ge=1, le=180)

    @model_validator(mode="after")
    def validate_weights_and_provider(self) -> Settings:
        if self.bm25_weight + self.vector_weight <= 0:
            raise ValueError("At least one retrieval weight must be greater than zero")
        if self.answer_provider == "openai-compatible" and (
            not self.llm_api_key or not self.llm_model
        ):
            raise ValueError("LLM_API_KEY and LLM_MODEL are required for openai-compatible answers")
        return self

    @property
    def upload_dir(self) -> Path:
        return self.data_dir / "uploads"

    @property
    def static_dir(self) -> Path:
        return Path(__file__).resolve().parent / "static"

    def ensure_directories(self) -> None:
        self.data_dir.mkdir(parents=True, exist_ok=True)
        self.upload_dir.mkdir(parents=True, exist_ok=True)
        self.database_path.parent.mkdir(parents=True, exist_ok=True)


@lru_cache(maxsize=1)
def get_settings() -> Settings:
    return Settings()
