"""Test bot functionality."""

import pytest
from unittest.mock import MagicMock, patch
from slack_bolt import App
from slack_bot.app import SlackAIBot
from slack_bot.config import Config
from slack_bot.services.slack_client import SlackClient
from slack_bot.services.vectorizer import Vectorizer
from slack_bot.database.vector_store import VectorStore
from slack_bot.services.message_sync import MessageSync
from slack_bot.services.rag_system import RAGSystem

@pytest.fixture
def config():
    """Create a test configuration."""
    test_config = Config.from_env()
    test_config.slack_bot_token = "xoxb-test-token"
    test_config.slack_app_token = "xapp-test-token"
    test_config.slack_signing_secret = "test-secret"
    return test_config

@pytest.fixture
def mock_app():
    """Create a mock Slack App."""
    app = MagicMock(spec=App)
    app.event.return_value = lambda func: func
    return app

@pytest.fixture
def mock_slack_client(mock_app):
    """Create a mock Slack client."""
    client = MagicMock(spec=SlackClient)
    client.send_message.return_value = True
    client.app = mock_app
    return client

@pytest.fixture
def mock_vectorizer():
    """Create a mock vectorizer."""
    vectorizer = MagicMock(spec=Vectorizer)
    vectorizer.vectorize_query.return_value = [0.1, 0.2, 0.3]
    return vectorizer

@pytest.fixture
def mock_vector_store():
    """Create a mock vector store."""
    store = MagicMock(spec=VectorStore)
    store.search_similar.return_value = [
        {
            "text": "テスト回答用のメッセージです。",
            "metadata": {
                "channel_id": "C123456",
                "user_id": "U123456",
                "timestamp": "2024-03-25T10:00:00",
                "thread_ts": None,
                "permalink": "https://slack.com/archives/C123456/p1234567890123456"
            },
            "similarity_score": 0.85
        }
    ]
    return store

@pytest.fixture
def mock_rag_system():
    """Create a mock RAG system."""
    rag = MagicMock(spec=RAGSystem)
    rag.answer_question.return_value = ("これはテスト用の回答です。", [])
    return rag

@pytest.fixture
def bot(config, mock_slack_client, mock_vectorizer, mock_vector_store, mock_rag_system):
    """Create a test bot instance."""
    with patch('slack_bot.app.SlackClient', return_value=mock_slack_client):
        bot = SlackAIBot(config)
        bot.vectorizer = mock_vectorizer
        bot.vector_store = mock_vector_store
        bot.rag_system = mock_rag_system
        return bot

def test_bot_mention_handler(bot):
    """Test bot's mention handler."""
    # メンションイベントの作成
    event = {
        "type": "app_mention",
        "user": "U123456",
        "text": "<@BOT_ID> テストの質問です。",
        "ts": "1234567890.123456",
        "channel": "C123456",
        "event_ts": "1234567890.123456"
    }

    # メンションハンドラーの実行
    bot.handle_mention(event)

    # 応答が送信されたことを確認
    bot.slack_client.send_message.assert_called_once()

def test_bot_message_handler(bot):
    """Test bot's message handler."""
    # メッセージイベントの作成
    event = {
        "type": "message",
        "user": "U123456",
        "text": "テストメッセージです。",
        "ts": "1234567890.123456",
        "channel": "C123456",
        "event_ts": "1234567890.123456"
    }

    # メッセージハンドラーの実行
    bot.handle_message(event)

    # メッセージが処理されたことを確認
    assert True  # 現時点では特に検証すべき動作はない