"""
Bot service configuration settings.
"""

import os
from pathlib import Path

from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Application settings."""

    # OpenAI Configuration
    openai_api_key: str = os.getenv("OPENAI_API_KEY", "")
    openai_model: str = os.getenv("OPENAI_MODEL", "gpt-4")
    openai_max_tokens: int = int(os.getenv("OPENAI_MAX_TOKENS", "1000"))
    openai_temperature: float = float(os.getenv("OPENAI_TEMPERATURE", "0.7"))

    # Database Configuration (PostgreSQL from Railway)
    database_url: str = os.getenv("DATABASE_URL", "")

    # RabbitMQ Configuration
    rabbitmq_url: str = os.getenv("RABBITMQ_URL", "")

    # Application Configuration
    port: int = int(os.getenv("BOT_SERVICE_PORT", "3002"))
    environment: str = os.getenv("ENVIRONMENT", "development")
    log_level: str = os.getenv("BOT_SERVICE_LOG_LEVEL", "INFO")

    # Queue Configuration
    queue_poll_interval: int = int(os.getenv("QUEUE_POLL_INTERVAL", "200"))
    telegram_message_queue: str = os.getenv("TELEGRAM_MESSAGE_QUEUE", "telegram_received_messages")
    bot_response_queue: str = os.getenv("BOT_RESPONSE_QUEUE", "telegram_bot_responses")
    queue_visibility_timeout: int = int(os.getenv("QUEUE_VISIBILITY_TIMEOUT", "30"))
    queue_max_retries: int = int(os.getenv("QUEUE_MAX_RETRIES", "3"))

    # Job Factory Configuration
    job_batch_size: int = int(os.getenv("BOT_SERVICE_JOB_BATCH_SIZE", "10"))

    # Telegram Configuration
    telegram_bot_token: str = os.getenv("TELEGRAM_BOT_TOKEN", "")
    telegram_webhook_secret: str = os.getenv("TELEGRAM_WEBHOOK_SECRET", "")
    telegram_webhook_url: str = os.getenv("TELEGRAM_WEBHOOK_URL", "")

    class Config:
        # Look for .env file in project root (3 levels up from this file)
        env_file = str(Path(__file__).parent.parent.parent.parent.parent / ".env")
        env_file_encoding = "utf-8"

    def validate_required_settings(self) -> None:
        """Validate that all required settings are present."""
        required_fields = [
            ("openai_api_key", "OPENAI_API_KEY"),
            ("database_url", "DATABASE_URL"),
            ("rabbitmq_url", "RABBITMQ_URL"),
            ("telegram_bot_token", "TELEGRAM_BOT_TOKEN"),
            ("telegram_webhook_secret", "TELEGRAM_WEBHOOK_SECRET"),
        ]

        missing_fields = []
        for field_name, env_var in required_fields:
            if not getattr(self, field_name):
                missing_fields.append(env_var)

        if missing_fields:
            raise ValueError(
                f"Missing required environment variables: {', '.join(missing_fields)}"
            )


# Global settings instance
settings = Settings()
