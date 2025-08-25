"""Configuration settings for the Slack AI Bot."""

import os
from typing import Optional

from dotenv import load_dotenv
from pydantic import BaseModel, Field

# Load environment variables from .env file
load_dotenv()


class Config(BaseModel):
    """Application configuration settings."""

    # Slack configuration
    slack_bot_token: str = Field(..., description="Slack Bot User OAuth Token")
    slack_app_token: str = Field(..., description="Slack App-Level Token")
    slack_signing_secret: str = Field(..., description="Slack Signing Secret")
    slack_channel_ids: list[str] = Field(default_factory=list, description="List of Slack channel IDs to monitor")

    # Google AI (Gemini) configuration
    gemini_api_key: str = Field(..., description="Google AI (Gemini) API Key")
    
    # ChromaDB configuration
    chroma_persist_directory: str = Field(
        default="data/chroma",
        description="Directory to persist ChromaDB data"
    )
    
    # Application settings
    debug: bool = Field(default=False, description="Enable debug mode")
    log_level: str = Field(default="INFO", description="Logging level")
    max_response_time: int = Field(
        default=10,
        description="Maximum time (in seconds) to wait for a response"
    )

    @classmethod
    def from_env(cls) -> "Config":
        """Create configuration from environment variables."""
        return cls(
            slack_bot_token=os.getenv("SLACK_BOT_TOKEN", ""),
            slack_app_token=os.getenv("SLACK_APP_TOKEN", ""),
            slack_signing_secret=os.getenv("SLACK_SIGNING_SECRET", ""),
            slack_channel_ids=os.getenv("SLACK_CHANNEL_IDS", "").split(","),
            gemini_api_key=os.getenv("GEMINI_API_KEY", ""),
            chroma_persist_directory=os.getenv(
                "CHROMA_PERSIST_DIRECTORY",
                "data/chroma"
            ),
            debug=os.getenv("DEBUG", "false").lower() == "true",
            log_level=os.getenv("LOG_LEVEL", "INFO"),
            max_response_time=int(os.getenv("MAX_RESPONSE_TIME", "10")),
        )
