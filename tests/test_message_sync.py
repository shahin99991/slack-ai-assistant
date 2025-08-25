"""Test message synchronization functionality."""

import os
import pytest
from unittest.mock import MagicMock, patch
from slack_bot.config import Config
from slack_bot.services.message_sync import MessageSync
from slack_bot.services.slack_client import SlackClient
from slack_bot.services.vectorizer import Vectorizer
from slack_bot.database.vector_store import VectorStore
from slack_bot.models.message import SlackMessage, MessageVector
from datetime import datetime

@pytest.fixture
def config():
    """Create a test configuration."""
    return Config.from_env()

@pytest.fixture
def mock_slack_client():
    """Create a mock Slack client."""
    client = MagicMock(spec=SlackClient)
    client.fetch_channel_history.return_value = [
        SlackMessage(
            message_id="1234567890.123456",
            channel_id="C123456",
            user_id="U123456",
            text="テストメッセージ1",
            timestamp=datetime.fromtimestamp(1234567890.123456),
            thread_ts=None,
            permalink="https://slack.com/archives/C123456/p1234567890123456",
            reactions=[]
        ),
        SlackMessage(
            message_id="1234567891.123456",
            channel_id="C123456",
            user_id="U234567",
            text="テストメッセージ2",
            timestamp=datetime.fromtimestamp(1234567891.123456),
            thread_ts=None,
            permalink="https://slack.com/archives/C123456/p1234567891123456",
            reactions=[]
        )
    ]
    client.fetch_thread_replies.return_value = []
    return client

@pytest.fixture
def mock_vectorizer():
    """Create a mock vectorizer."""
    vectorizer = MagicMock(spec=Vectorizer)
    vectorizer.vectorize_messages.return_value = [
        MessageVector(
            message_id="1234567890.123456",
            vector=[0.1, 0.2, 0.3],
            text="テストメッセージ1",
            metadata={
                "channel_id": "C123456",
                "user_id": "U123456",
                "timestamp": "2009-02-13T23:31:30.123456",
                "thread_ts": None,
                "permalink": "https://slack.com/archives/C123456/p1234567890123456"
            }
        ),
        MessageVector(
            message_id="1234567891.123456",
            vector=[0.4, 0.5, 0.6],
            text="テストメッセージ2",
            metadata={
                "channel_id": "C123456",
                "user_id": "U234567",
                "timestamp": "2009-02-13T23:31:31.123456",
                "thread_ts": None,
                "permalink": "https://slack.com/archives/C123456/p1234567891123456"
            }
        )
    ]
    return vectorizer

@pytest.fixture
def mock_vector_store():
    """Create a mock vector store."""
    store = MagicMock(spec=VectorStore)
    store.add_messages.return_value = None
    return store

def test_message_sync(config, mock_slack_client, mock_vectorizer, mock_vector_store):
    """Test message synchronization."""
    sync = MessageSync(
        slack_client=mock_slack_client,
        vectorizer=mock_vectorizer,
        vector_store=mock_vector_store
    )

    # メッセージ同期の実行
    result = sync.sync_channel("C123456")

    # 同期されたメッセージ数を確認
    assert result == 2

    # Slack APIが呼び出されたことを確認
    mock_slack_client.fetch_channel_history.assert_called_once_with(
        channel_id="C123456",
        oldest=None,
        latest=None
    )

    # メッセージがベクトル化されたことを確認
    mock_vectorizer.vectorize_messages.assert_called_once()

    # ベクトルストアにメッセージが保存されたことを確認
    mock_vector_store.add_messages.assert_called_once()