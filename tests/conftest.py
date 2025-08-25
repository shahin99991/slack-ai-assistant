"""Test configuration and fixtures."""

import os
from datetime import datetime
from pathlib import Path
from typing import Generator
from unittest.mock import AsyncMock, MagicMock

import pytest
from slack_bolt import App
from slack_sdk.web import WebClient

from slack_bot.config import Config
from slack_bot.database.vector_store import VectorStore
from slack_bot.models.message import MessageVector, SlackMessage
from slack_bot.services.slack_client import SlackClient
from slack_bot.services.vectorizer import Vectorizer


@pytest.fixture
def test_config() -> Config:
    """Create a test configuration."""
    return Config(
        slack_bot_token="xoxb-test-token",
        slack_app_token="xapp-test-token",
        slack_signing_secret="test-secret",
        slack_channel_ids=["C1234567890"],
        gemini_api_key="test-api-key",
        chroma_persist_directory="tests/data/chroma",
        debug=True,
        log_level="DEBUG",
        max_response_time=5
    )


@pytest.fixture
def mock_web_client() -> MagicMock:
    """Create a mock Slack Web API client."""
    client = MagicMock(spec=WebClient)
    
    # Mock conversations_history
    async def mock_conversations_history(*args, **kwargs):
        return {
            "ok": True,
            "messages": [
                {
                    "type": "message",
                    "user": "U1234567890",
                    "text": "Test message 1",
                    "ts": "1234567890.123456"
                },
                {
                    "type": "message",
                    "user": "U0987654321",
                    "text": "Test message 2",
                    "ts": "1234567890.123457"
                }
            ],
            "has_more": False
        }
    client.conversations_history = AsyncMock(side_effect=mock_conversations_history)

    # Mock chat_getPermalink
    async def mock_chat_get_permalink(*args, **kwargs):
        return {
            "ok": True,
            "permalink": f"https://slack.com/archives/C1234567890/p{kwargs['message_ts'].replace('.', '')}"
        }
    client.chat_getPermalink = AsyncMock(side_effect=mock_chat_get_permalink)

    # Mock conversations_replies
    async def mock_conversations_replies(*args, **kwargs):
        return {
            "ok": True,
            "messages": [
                {
                    "type": "message",
                    "user": "U1234567890",
                    "text": "Parent message",
                    "ts": kwargs["ts"]
                },
                {
                    "type": "message",
                    "user": "U0987654321",
                    "text": "Reply message",
                    "ts": f"{float(kwargs['ts']) + 0.000001:.6f}"
                }
            ]
        }
    client.conversations_replies = AsyncMock(side_effect=mock_conversations_replies)

    # Mock chat_postMessage
    async def mock_chat_post_message(*args, **kwargs):
        return {"ok": True, "ts": "1234567890.123456"}
    client.chat_postMessage = AsyncMock(side_effect=mock_chat_post_message)

    return client


@pytest.fixture
def mock_app() -> MagicMock:
    """Create a mock Slack Bolt app."""
    app = MagicMock(spec=App)
    app.client = MagicMock()
    app.client.bot_id = "B1234567890"
    return app


@pytest.fixture
def test_slack_client(test_config: Config, mock_web_client: MagicMock, mock_app: MagicMock) -> SlackClient:
    """Create a test Slack client."""
    client = SlackClient(test_config)
    client.client = mock_web_client
    client.app = mock_app
    return client


@pytest.fixture
def test_vectorizer(test_config: Config) -> Vectorizer:
    """Create a test vectorizer."""
    return Vectorizer(test_config)


@pytest.fixture
def test_vector_store(test_config: Config) -> Generator[VectorStore, None, None]:
    """Create a test vector store."""
    # Create test directory
    Path(test_config.chroma_persist_directory).parent.mkdir(
        parents=True,
        exist_ok=True
    )

    store = VectorStore(test_config)
    yield store

    # Cleanup
    try:
        store.client.reset()
    except Exception:
        pass


@pytest.fixture
def sample_message() -> SlackMessage:
    """Create a sample Slack message."""
    return SlackMessage(
        message_id="1234567890.123456",
        channel_id="C1234567890",
        user_id="U1234567890",
        text="This is a test message",
        timestamp=datetime.now(),
        thread_ts=None,
        permalink="https://slack.com/archives/C1234567890/p1234567890123456",
        reactions=["thumbsup", "heart"]
    )


@pytest.fixture
def sample_message_vector() -> MessageVector:
    """Create a sample message vector."""
    return MessageVector(
        message_id="1234567890.123456",
        vector=[0.1] * 768,  # Gemini embedding dimension
        text="This is a test message",
        metadata={
            "channel_id": "C1234567890",
            "user_id": "U1234567890",
            "timestamp": datetime.now().isoformat(),
            "thread_ts": None,
            "permalink": "https://slack.com/archives/C1234567890/p1234567890123456"
        }
    )