from pathlib import Path
from typing import List, Optional
from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import Field


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )

    app_env: str = "development"
    company_id: str = "apexpetro"

    ollama_base_url: str = "http://localhost:11434"
    primary_model: str = "qwen2.5:7b"
    coding_model: str = "qwen2.5-coder:7b"
    router_model: str = "qwen2.5:3b"
    embedding_model: str = "bge-m3:latest"

    qdrant_url: str = "http://localhost:6333"
    qdrant_collection: str = "apexpetro_knowledge"

    database_url: str = "sqlite:///./data/runtime/workbench.db"

    company_data_path: str = "../ApexPetro_Sovereign_Dataset_v3"
    test_data_enabled: bool = False

    offline_mode: bool = True
    allow_external_network: bool = False

    host: str = "0.0.0.0"
    port: int = 8000

    log_level: str = "INFO"

    @property
    def company_data_dir(self) -> Path:
        return Path(self.company_data_path).resolve()

    @property
    def is_production(self) -> bool:
        return self.app_env == "production"

    @property
    def allowed_models(self) -> List[str]:
        return [self.primary_model, self.coding_model, self.router_model, self.embedding_model]


settings = Settings()