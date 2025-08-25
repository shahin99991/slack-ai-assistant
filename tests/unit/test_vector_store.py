"""Tests for the vector store component."""

import pytest

from slack_bot.database.vector_store import VectorStore
from slack_bot.models.message import MessageVector, SlackMessage


def test_vector_store_initialization(test_vector_store: VectorStore):
    """Test vector store initialization."""
    assert test_vector_store.collection is not None
    assert test_vector_store.collection.name == "slack_messages"


def test_add_messages(
    test_vector_store: VectorStore,
    sample_message: SlackMessage,
    sample_message_vector: MessageVector
):
    """Test adding messages to the vector store."""
    # Add a message
    test_vector_store.add_messages([(sample_message, sample_message_vector)])

    # Verify the message was added
    result = test_vector_store.get_message_by_id(sample_message.message_id)
    assert result is not None
    assert result["text"] == sample_message.text
    assert result["metadata"]["channel_id"] == sample_message.channel_id


def test_search_similar(
    test_vector_store: VectorStore,
    sample_message: SlackMessage,
    sample_message_vector: MessageVector
):
    """Test searching for similar messages."""
    # Add a message
    test_vector_store.add_messages([(sample_message, sample_message_vector)])

    # Search using the same vector
    results = test_vector_store.search_similar(
        query_vector=sample_message_vector.vector,
        n_results=1
    )

    assert len(results) == 1
    assert results[0]["text"] == sample_message.text
    assert results[0]["similarity_score"] > 0.9  # Should be very similar


def test_delete_messages(
    test_vector_store: VectorStore,
    sample_message: SlackMessage,
    sample_message_vector: MessageVector
):
    """Test deleting messages from the vector store."""
    # Add a message
    test_vector_store.add_messages([(sample_message, sample_message_vector)])

    # Delete the message
    test_vector_store.delete_messages([sample_message.message_id])

    # Verify the message was deleted
    result = test_vector_store.get_message_by_id(sample_message.message_id)
    assert result is None


def test_get_nonexistent_message(test_vector_store: VectorStore):
    """Test retrieving a nonexistent message."""
    result = test_vector_store.get_message_by_id("nonexistent")
    assert result is None
