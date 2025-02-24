"""Application configuration using Pydantic Settings management."""
from functools import lru_cache
from pathlib import Path
from typing import ClassVar, Any, Optional

from pydantic import Field, computed_field, ConfigDict
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""
    model_config = ConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="allow",
        validate_assignment=True
    )
    
    # Path Configuration
    data_dir: Path = Field(
        default=Path("src/data"),
        description="Base directory for all data files"
    )
    pdf_dir: Path = Field(
        default=Path("src/data/pdfs"),
        description="Directory containing PDF files"
    )
    diagram_dir: Path = Field(
        default=Path("src/data/diagrams"),
        description="Directory containing extracted diagrams"
    )
    processed_dir: Path = Field(
        default=Path("src/data/processed"),
        description="Directory for processed output files"
    )
        
    # OpenAI Configuration
    openai_api_key: Optional[str] = None
    openai_org_id: Optional[str] = None
    
    # Agent Configuration
    default_model: str = "gpt-4-turbo-preview"
    default_temperature: float = 0.3
    max_retries: int = 3
    request_timeout: int = 60
  
    # Database Configuration
    db_pool_min_size: int = Field(5, ge=1, le=100)
    db_pool_max_size: int = Field(20, ge=5, le=1000)
    
    # Supabase Configuration - Optional for development
    supabase_url: Optional[str] = Field(None, description="Supabase project URL")
    supabase_key: Optional[str] = Field(None, description="Supabase service role key")

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        # Create directories if they don't exist
        self.data_dir.mkdir(parents=True, exist_ok=True)
        self.pdf_dir.mkdir(parents=True, exist_ok=True)
        self.processed_dir.mkdir(parents=True, exist_ok=True)



@lru_cache()
def get_settings() -> Settings:
    """Get cached application settings."""
    return Settings()


# Create a global settings instance
settings = get_settings()
