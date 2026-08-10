from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    llm_base_url: str = "http://localhost:11434"
    llm_model: str = "qwen3:4b"
    llm_timeout: float = 120.0
    llm_temperature: float = 0.8

    model_config = SettingsConfigDict(
        env_file=".env", env_file_encoding="utf-8", extra="ignore"
    )


settings = Settings()
