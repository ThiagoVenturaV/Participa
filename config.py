import os
from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    # LLM Settings
    openai_api_key: str = ""
    google_api_key: str = ""
    groq_api_key: str = ""
    llm_provider: str = "groq"  # "groq", "openai" ou "gemini"
    llm_model: str = "llama-3.3-70b-versatile" # ex: "llama-3.3-70b-versatile", "llama-3.1-8b-instant", "gpt-4o-mini"

    # Meta WhatsApp Cloud API Settings
    whatsapp_token: str = ""
    whatsapp_phone_number_id: str = ""
    whatsapp_api_version: str = "v19.0"
    webhook_verify_token: str = "meu_token_secreto_whatsapp_123"

    # Server Settings
    port: int = 8000
    host: str = "0.0.0.0"

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore"
    )

settings = Settings()
