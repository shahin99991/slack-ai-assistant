"""Message models for the Slack AI Bot."""

from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field


class SlackMessage(BaseModel):
    """Represents a Slack message."""

    message_id: str = Field(..., description="Unique identifier for the message")
    channel_id: str = Field(..., description="ID of the channel where the message was posted")
    user_id: str = Field(..., description="ID of the user who posted the message")
    text: str = Field(..., description="Message text content")
    timestamp: datetime = Field(..., description="Message timestamp")
    thread_ts: Optional[str] = Field(None, description="Parent thread timestamp if in thread")
    permalink: Optional[str] = Field(None, description="Permanent link to the message")
    reactions: list[str] = Field(default_factory=list, description="List of reactions to the message")

    class Config:
        """Pydantic model configuration."""

        json_encoders = {
            datetime: lambda v: v.isoformat()
        }


class MessageVector(BaseModel):
    """Represents a vectorized message with metadata."""

    message_id: str = Field(..., description="Original message ID")
    vector: list[float] = Field(..., description="Embedding vector")
    text: str = Field(..., description="Original message text")
    metadata: dict = Field(default_factory=dict, description="Additional metadata")

    class Config:
        """Pydantic model configuration."""

        arbitrary_types_allowed = True
