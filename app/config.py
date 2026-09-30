from functools import lru_cache
from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    app_name: str = "PocketSmart AI"
    secret_key: str = "dev-secret-change-me"
    gemini_api_key: str = ""
    gemini_model: str = "gemini-3.8-flash"
    database_url: str = "sqlite:///./data/pocketsmart.db"
    use_mock_data: bool = True
    cors_origins: str = "http://127.0.0.1:8000,http://localhost:8000"
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

    @property
    def origins(self) -> list[str]:
        return [x.strip() for x in self.cors_origins.split(",") if x.strip()]

@lru_cache
def get_settings() -> Settings:
    return Settings()
