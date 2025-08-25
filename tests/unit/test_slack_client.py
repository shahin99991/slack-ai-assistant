"""Tests for the Slack client component."""

import pytest
from slack_sdk.errors import SlackApiError

from slack_bot.models.message import SlackMessage
from slack_bot.services.slack_client import SlackClient


@pytest.mark.asyncio
async def test_fetch_channel_history(
    test_slack_client: SlackClient,
    mock_slack_web_client
):
    """Test fetching channel history."""
    messages = await test_slack_client.fetch_channel_history("C1234567890")
    assert len(messages) == 2
    assert isinstance(messages[0], SlackMessage)
    assert messages[0].text == "Test message 1"
    assert messages[1].text == "Test message 2"


@pytest.mark.asyncio
async def test_fetch_thread_replies(
    test_slack_client: SlackClient,
    mock_slack_web_client
):
    """Test fetching thread replies."""
    replies = await test_slack_client.fetch_thread_replies(
        "C1234567890",
        "1234567890.123456"
    )
    assert isinstance(replies, list)


@pytest.mark.asyncio
async def test_send_message(test_slack_client: SlackClient):
    """Test sending a message."""
    # Mock the chat_postMessage method
    async def mock_chat_post_message(*args, **kwargs):
        return {"ok": True}

    test_slack_client.client.chat_postMessage = mock_chat_post_message

    result = await test_slack_client.send_message(
        "C1234567890",
        "Test message"
    )
    assert result is True


@pytest.mark.asyncio
async def test_send_message_error(test_slack_client: SlackClient):
    """Test sending a message with an error."""
    # Mock the chat_postMessage method to raise an error
    async def mock_chat_post_message(*args, **kwargs):
        raise SlackApiError("Error", {"error": "channel_not_found"})

    test_slack_client.client.chat_postMessage = mock_chat_post_message

    result = await test_slack_client.send_message(
        "C1234567890",
        "Test message"
    )
    assert result is False
