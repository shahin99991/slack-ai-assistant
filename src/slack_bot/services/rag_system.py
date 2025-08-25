"""RAG (Retrieval-Augmented Generation) system implementation."""

import logging
from typing import List, Optional

import google.generativeai as genai

from ..database.vector_store import VectorStore
from ..services.vectorizer import Vectorizer

logger = logging.getLogger(__name__)


class RAGSystem:
    """RAG system for answering questions using retrieved context."""

    def __init__(
        self,
        vectorizer: Vectorizer,
        vector_store: VectorStore,
        max_context_messages: int = 5
    ):
        """Initialize the RAG system.

        Args:
            vectorizer: Vectorizer service
            vector_store: Vector database service
            max_context_messages: Maximum number of context messages to use
        """
        self.vectorizer = vectorizer
        self.vector_store = vector_store
        self.max_context_messages = max_context_messages
        self.model = genai.GenerativeModel("gemini-2.5-flash")
        logger.info("Initialized RAG system")

    def answer_question(
        self,
        question: str,
        conversation_history: Optional[List[dict]] = None
    ) -> tuple[str, List[dict]]:
        """Answer a question using retrieved context.

        Args:
            question: The question to answer
            conversation_history: Optional list of previous Q&A pairs

        Returns:
            Tuple of (answer, relevant_messages)
        """
        # Vectorize the question
        query_vector = self.vectorizer.vectorize_query(question)
        if not query_vector:
            return (
                "申し訳ありません。質問の処理中にエラーが発生しました。",
                []
            )

        # Search for relevant messages
        relevant_messages = self.vector_store.search_similar(
            query_vector=query_vector,
            n_results=self.max_context_messages
        )

        if not relevant_messages:
            return (
                "申し訳ありません。関連する情報が見つかりませんでした。",
                []
            )

        # Construct prompt with context
        prompt = self._construct_prompt(
            question=question,
            relevant_messages=relevant_messages,
            conversation_history=conversation_history
        )

        try:
            # Generate answer using Gemini
            response = self.model.generate_content(prompt)
            answer = response.text

            # Format answer if needed
            answer = self._format_answer(answer)

            return answer, relevant_messages

        except Exception as e:
            logger.error("Error generating answer: %s", e)
            return (
                "申し訳ありません。回答の生成中にエラーが発生しました。",
                relevant_messages
            )

    def _construct_prompt(
        self,
        question: str,
        relevant_messages: List[dict],
        conversation_history: Optional[List[dict]] = None
    ) -> str:
        """Construct a prompt for the language model.

        Args:
            question: The current question
            relevant_messages: List of relevant messages from the vector store
            conversation_history: Optional list of previous Q&A pairs

        Returns:
            Formatted prompt string
        """
        prompt_parts = [
            "以下の情報を参考に、簡潔に回答してください：\n"
        ]

        # 最も関連性の高い3つのメッセージのみを使用
        for i, msg in enumerate(relevant_messages[:3], 1):
            prompt_parts.append(f"{i}. {msg['text']}")

        prompt_parts.extend([
            "\n質問:",
            question,
            "\n回答は日本語で、簡潔に提供してください。"
        ])

        return "\n".join(prompt_parts)

    def _format_answer(self, answer: str) -> str:
        """Format the generated answer.

        Args:
            answer: Raw answer from the language model

        Returns:
            Formatted answer string
        """
        # Remove any unnecessary prefixes
        answer = answer.lstrip("回答：").lstrip("A:").strip()

        # Ensure the answer starts with a complete sentence
        if answer and not answer[0].isupper() and not "。" in answer[:10]:
            answer = "申し訳ありません。" + answer

        return answer
