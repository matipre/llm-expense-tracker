"""
Bot service configuration settings.
"""
import os
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Application settings."""
    
    # OpenAI Configuration
    openai_api_key: str = os.getenv("OPENAI_API_KEY", "")
    openai_model: str = os.getenv("OPENAI_MODEL", "gpt-3.5-turbo")
    
    # Supabase Configuration
    supabase_url: str = os.getenv("SUPABASE_URL", "")
    supabase_service_key: str = os.getenv("SUPABASE_SERVICE_KEY", "")
    
    # Database Configuration
    database_url: str = os.getenv("DATABASE_URL", "")
    
    # Application Configuration
    port: int = int(os.getenv("PORT", "3002"))
    environment: str = os.getenv("ENVIRONMENT", "development")
    log_level: str = os.getenv("LOG_LEVEL", "INFO")
    
    # Queue Configuration
    queue_poll_interval: int = int(os.getenv("QUEUE_POLL_INTERVAL", "5"))
    
    # Job Factory Configuration
    job_poll_interval: int = int(os.getenv("JOB_POLL_INTERVAL", "5"))
    job_batch_size: int = int(os.getenv("JOB_BATCH_SIZE", "10"))
    job_visibility_timeout: int = int(os.getenv("JOB_VISIBILITY_TIMEOUT", "30"))
    
    class Config:
        env_file = "../.env"
        env_file_encoding = "utf-8"
    
    def validate_required_settings(self) -> None:
        """Validate that all required settings are present."""
        required_fields = [
            ("openai_api_key", "OPENAI_API_KEY"),
            ("supabase_url", "SUPABASE_URL"),
            ("supabase_service_key", "SUPABASE_SERVICE_KEY"),
            ("database_url", "DATABASE_URL"),
        ]
        
        missing_fields = []
        for field_name, env_var in required_fields:
            if not getattr(self, field_name):
                missing_fields.append(env_var)
        
        if missing_fields:
            raise ValueError(f"Missing required environment variables: {', '.join(missing_fields)}")


# Global settings instance
settings = Settings()
