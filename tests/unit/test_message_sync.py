"""Tests for the message sync component."""

from datetime import datetime, timedelta
from unittest.mock import AsyncMock, MagicMock

import pytest

from slack_bot.models.message import MessageVector, SlackMessage
from slack_bot.services.message_sync import MessageSync


@pytest.fixture
def mock_slack_client():
    """Create a mock Slack client."""
    client = MagicMock()
    
    async def mock_fetch_channel_history(*args, **kwargs):
        channel_id = kwargs.get("channel_id", args[0])
        return [
            SlackMessage(
                message_id=f"{channel_id}.123456",
                channel_id=channel_id,
                user_id="U1234567890",
                text=f"Test message for {channel_id}",
                timestamp=datetime.now(),
                thread_ts=None,
                permalink=f"https://slack.com/archives/{channel_id}/p123456",
                reactions=[]
            )
        ]
    
    client.fetch_channel_history = AsyncMock(side_effect=mock_fetch_channel_history)
    client.fetch_thread_replies = AsyncMock(return_value=[])
    return client


@pytest.fixture
def mock_vectorizer():
    """Create a mock vectorizer."""
    vectorizer = MagicMock()
    
    async def mock_vectorize_messages(messages):
        return [
            MessageVector(
                message_id=msg.message_id,
                vector=[0.1] * 768,
                text=msg.text,
                metadata={
                    "channel_id": msg.channel_id,
                    "user_id": msg.user_id,
                    "timestamp": msg.timestamp.isoformat(),
                    "thread_ts": msg.thread_ts,
                    "permalink": msg.permalink
                }
            )
            for msg in messages
        ]
    
    vectorizer.vectorize_messages = AsyncMock(side_effect=mock_vectorize_messages)
    return vectorizer


@pytest.fixture
def mock_vector_store():
    """Create a mock vector store."""
    store = MagicMock()
    store.add_messages = MagicMock()
    return store


@pytest.fixture
def message_sync(mock_slack_client, mock_vectorizer, mock_vector_store):
    """Create a message sync service with mock components."""
    return MessageSync(
        slack_client=mock_slack_client,
        vectorizer=mock_vectorizer,
        vector_store=mock_vector_store
    )


@pytest.mark.asyncio
async def test_sync_channel(message_sync):
    """Test syncing messages from a channel."""
    result = await message_sync.sync_channel("C1234567890")
    assert result == 1

    # Verify that the components were called correctly
    message_sync.slack_client.fetch_channel_history.assert_called_once()
    message_sync.vectorizer.vectorize_messages.assert_called_once()
    message_sync.vector_store.add_messages.assert_called_once()


@pytest.mark.asyncio
async def test_sync_channel_no_messages(message_sync, mock_slack_client):
    """Test syncing when there are no messages."""
    mock_slack_client.fetch_channel_history.return_value = []
    message_sync.slack_client = mock_slack_client

    result = await message_sync.sync_channel("C1234567890")
    assert result == 0

    message_sync.vectorizer.vectorize_messages.assert_not_called()
    message_sync.vector_store.add_messages.assert_not_called()


@pytest.mark.asyncio
async def test_sync_channel_with_thread(message_sync, mock_slack_client):
    """Test syncing messages with thread replies."""
    # Add a message with thread
    thread_ts = "1234567890.123456"
    mock_slack_client.fetch_channel_history.return_value = [
        SlackMessage(
            message_id=thread_ts,
            channel_id="C1234567890",
            user_id="U1234567890",
            text="Test message 1",
            timestamp=datetime.now(),
            thread_ts=thread_ts,
            permalink="https://slack.com/archives/C1234567890/p1234567890123456",
            reactions=[]
        )
    ]

    # Add thread replies
    mock_slack_client.fetch_thread_replies.return_value = [
        SlackMessage(
            message_id="1234567890.123457",
            channel_id="C1234567890",
            user_id="U0987654321",
            text="Test reply 1",
            timestamp=datetime.now(),
            thread_ts=thread_ts,
            permalink="https://slack.com/archives/C1234567890/p1234567890123457",
            reactions=[]
        )
    ]

    result = await message_sync.sync_channel("C1234567890")
    assert result == 2  # Main message + reply

    message_sync.slack_client.fetch_thread_replies.assert_called_once_with(
        channel_id="C1234567890",
        thread_ts=thread_ts
    )


@pytest.mark.asyncio
async def test_sync_recent_messages(message_sync):
    """Test syncing recent messages from multiple channels."""
    channels = ["C1234567890", "C0987654321"]
    result = await message_sync.sync_recent_messages(channels, hours=24)
    assert result == 2  # 1 message per channel

    # Verify timestamps
    now = datetime.now()
    oldest = (now - timedelta(hours=24)).timestamp()

    calls = message_sync.slack_client.fetch_channel_history.call_args_list
    assert len(calls) == len(channels)
    for call in calls:
        assert float(call.kwargs["oldest"]) >= oldest - 1  # Allow 1 second tolerance
        assert float(call.kwargs["latest"]) <= now.timestamp() + 1  # Allow 1 second tolerance

    # Verify that each channel was processed
    called_channels = [call.args[0] for call in calls]
    assert set(called_channels) == set(channels)