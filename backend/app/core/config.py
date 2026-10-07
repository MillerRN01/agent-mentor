from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    app_name: str = "Agent Mentor"
    app_env: str = "development"
    ollama_base_url: str = "http://localhost:11434"
    ollama_model: str = "agent-mentor-local:latest"

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )


settings = Settings()
