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

    # Database Configuration
    database_url: str = ""
    db_host: str = os.getenv("DB_HOST", "localhost")
    db_port: int = int(os.getenv("DB_PORT", "5432"))
    db_name: str = os.getenv("DB_NAME", "expensio")
    db_user: str = os.getenv("DB_USER", "expensio_user")
    db_password: str = os.getenv("DB_PASSWORD", "expensio_password")

    # RabbitMQ Configuration
    rabbitmq_url: str = ""
    rabbitmq_host: str = os.getenv("RABBITMQ_HOST", "localhost")
    rabbitmq_port: int = int(os.getenv("RABBITMQ_PORT", "5672"))
    rabbitmq_user: str = os.getenv("RABBITMQ_USER", "expensio_user")
    rabbitmq_password: str = os.getenv("RABBITMQ_PASSWORD", "expensio_password")
    rabbitmq_vhost: str = os.getenv("RABBITMQ_VHOST", "/")

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

    def model_post_init(self, __context=None) -> None:
        """Construct URLs from individual components after model initialization."""
        # Construct database URL if not provided directly
        if not self.database_url:
            self.database_url = os.getenv(
                "DATABASE_URL",
                f"postgresql://{self.db_user}:{self.db_password}@{self.db_host}:{self.db_port}/{self.db_name}"
            )
        
        # Construct RabbitMQ URL if not provided directly
        if not self.rabbitmq_url:
            self.rabbitmq_url = os.getenv(
                "RABBITMQ_URL",
                f"amqp://{self.rabbitmq_user}:{self.rabbitmq_password}@{self.rabbitmq_host}:{self.rabbitmq_port}{self.rabbitmq_vhost}"
            )

    class Config:
        # Look for .env file in project root (3 levels up from this file)
        env_file = str(Path(__file__).parent.parent.parent.parent.parent / ".env")
        env_file_encoding = "utf-8"
        extra = "ignore"

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
