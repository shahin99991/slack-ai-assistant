"""Tests for the RAG system component."""

from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from slack_bot.services.rag_system import RAGSystem


@pytest.fixture
def mock_vectorizer():
    """Create a mock vectorizer."""
    vectorizer = MagicMock()
    vectorizer.vectorize_query = AsyncMock(return_value=[0.1] * 768)
    return vectorizer


@pytest.fixture
def mock_vector_store():
    """Create a mock vector store."""
    vector_store = MagicMock()
    vector_store.search_similar.return_value = [
        {
            "text": "Test message 1",
            "metadata": {
                "channel_id": "C1234567890",
                "user_id": "U1234567890",
                "timestamp": "2024-03-14T12:00:00",
                "permalink": "https://slack.com/archives/C1234567890/p1234567890123456"
            },
            "similarity_score": 0.95
        }
    ]
    return vector_store


@pytest.fixture
def mock_genai():
    """Create a mock Gemini API."""
    class MockResponse:
        text = "Test answer"

    mock = MagicMock()
    mock.GenerativeModel.return_value.generate_content.return_value = MockResponse()
    return mock


@pytest.fixture
def rag_system(mock_vectorizer, mock_vector_store, mock_genai):
    """Create a RAG system with mock components."""
    with patch("slack_bot.services.rag_system.genai", mock_genai):
        system = RAGSystem(
            vectorizer=mock_vectorizer,
            vector_store=mock_vector_store
        )
        return system


@pytest.mark.asyncio
async def test_answer_question_success(rag_system):
    """Test successful question answering."""
    answer, relevant_messages = await rag_system.answer_question(
        "Test question"
    )

    assert answer == "Test answer"
    assert len(relevant_messages) == 1
    assert relevant_messages[0]["text"] == "Test message 1"


@pytest.mark.asyncio
async def test_answer_question_no_context(rag_system, mock_vector_store):
    """Test question answering with no relevant context."""
    mock_vector_store.search_similar.return_value = []
    rag_system.vector_store = mock_vector_store

    answer, relevant_messages = await rag_system.answer_question(
        "Test question"
    )

    assert "申し訳ありません" in answer
    assert "関連する情報が見つかりませんでした" in answer
    assert len(relevant_messages) == 0


@pytest.mark.asyncio
async def test_answer_question_vectorization_error(
    rag_system,
    mock_vectorizer
):
    """Test question answering with vectorization error."""
    mock_vectorizer.vectorize_query.return_value = None
    rag_system.vectorizer = mock_vectorizer

    answer, relevant_messages = await rag_system.answer_question(
        "Test question"
    )

    assert "申し訳ありません" in answer
    assert "質問の処理中にエラーが発生しました" in answer
    assert len(relevant_messages) == 0


@pytest.mark.asyncio
async def test_answer_question_with_history(rag_system):
    """Test question answering with conversation history."""
    history = [
        {
            "question": "Previous question",
            "answer": "Previous answer"
        }
    ]

    answer, relevant_messages = await rag_system.answer_question(
        "Test question",
        conversation_history=history
    )

    assert answer == "Test answer"
    assert len(relevant_messages) == 1

    # Verify that history was included in the prompt
    prompt = rag_system.model.generate_content.call_args[0][0]
    assert "Previous question" in prompt
    assert "Previous answer" in prompt