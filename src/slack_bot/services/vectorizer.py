"""Service for text vectorization using Google's Gemini API."""

import logging
from typing import List, Optional

import google.generativeai as genai

from ..config import Config
from ..models.message import MessageVector, SlackMessage

logger = logging.getLogger(__name__)


class Vectorizer:
    """Service for converting text to vectors using Gemini API."""

    def __init__(self, config: Config):
        """Initialize the vectorizer service.

        Args:
            config: Application configuration
        """
        self.config = config
        genai.configure(api_key=config.gemini_api_key)
        logger.info("Initialized vectorizer service")

    def vectorize_message(
        self,
        message: SlackMessage
    ) -> Optional[MessageVector]:
        """Convert a Slack message to a vector representation.

        Args:
            message: The Slack message to vectorize

        Returns:
            MessageVector if successful, None otherwise
        """
        try:
            # Generate embedding for the message text
            result = genai.embed_content(
                model="embedding-001",
                content=message.text,
            )

            if not result or "embedding" not in result:
                logger.error(
                    "Failed to generate embedding for message %s",
                    message.message_id
                )
                return None

            # Create message vector with metadata
            return MessageVector(
                message_id=message.message_id,
                vector=result["embedding"],
                text=message.text,
                metadata={
                    "channel_id": message.channel_id,
                    "user_id": message.user_id,
                    "timestamp": message.timestamp.isoformat(),
                    "thread_ts": message.thread_ts,
                    "permalink": message.permalink
                }
            )

        except Exception as e:
            logger.error(
                "Error vectorizing message %s: %s",
                message.message_id,
                str(e)
            )
            return None

    def vectorize_messages(
        self,
        messages: List[SlackMessage]
    ) -> List[MessageVector]:
        """Convert multiple Slack messages to vector representations.

        Args:
            messages: List of Slack messages to vectorize

        Returns:
            List of successfully vectorized messages
        """
        vectors = []
        for message in messages:
            vector = self.vectorize_message(message)
            if vector:
                vectors.append(vector)

        logger.info(
            "Vectorized %d/%d messages successfully",
            len(vectors),
            len(messages)
        )
        return vectors

    def vectorize_query(self, query: str) -> Optional[List[float]]:
        """Convert a search query to a vector representation.

        Args:
            query: The search query text

        Returns:
            Query vector if successful, None otherwise
        """
        try:
            result = genai.embed_content(
                model="embedding-001",
                content=query,
            )

            if not result or "embedding" not in result:
                logger.error("Failed to generate embedding for query")
                return None

            return result["embedding"]

        except Exception as e:
            logger.error("Error vectorizing query: %s", str(e))
            return None
