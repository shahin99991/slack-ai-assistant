"""Vector database implementation using ChromaDB."""

import logging
from pathlib import Path
from typing import List, Optional, Tuple

import chromadb
from chromadb.config import Settings

from ..config import Config
from ..models.message import MessageVector, SlackMessage

logger = logging.getLogger(__name__)


class VectorStore:
    """Vector database for storing and retrieving message embeddings."""

    def __init__(self, config: Config):
        """Initialize the vector store.

        Args:
            config: Application configuration
        """
        self.config = config
        self.persist_directory = Path(config.chroma_persist_directory)
        self.persist_directory.mkdir(parents=True, exist_ok=True)

        # Initialize ChromaDB client
        self.client = chromadb.PersistentClient(
            path=str(self.persist_directory),
            settings=Settings(
                anonymized_telemetry=False,
                allow_reset=True
            )
        )

        # Create or get the collection for message embeddings
        self.collection = self.client.get_or_create_collection(
            name="slack_messages",
            metadata={"description": "Slack message embeddings"}
        )

        logger.info(
            "Initialized vector store at %s",
            self.persist_directory.absolute()
        )

    def add_messages(
        self,
        messages: List[Tuple[SlackMessage, MessageVector]]
    ) -> None:
        """Add messages and their embeddings to the vector store.

        Args:
            messages: List of tuples containing SlackMessage and MessageVector pairs
        """
        if not messages:
            return

        # Prepare data for batch insertion
        ids = []
        embeddings = []
        metadatas = []
        documents = []

        for message, vector in messages:
            ids.append(message.message_id)
            embeddings.append(vector.vector)
            # Convert metadata values to strings to avoid type issues
            metadata = {
                "channel_id": str(message.channel_id),
                "user_id": str(message.user_id),
                "timestamp": message.timestamp.isoformat(),
                "thread_ts": str(message.thread_ts) if message.thread_ts else "",
                "permalink": str(message.permalink) if message.permalink else ""
            }
            metadatas.append(metadata)
            documents.append(message.text)

        # Add to collection
        self.collection.add(
            ids=ids,
            embeddings=embeddings,
            metadatas=metadatas,
            documents=documents
        )

        logger.info("Added %d messages to vector store", len(messages))

    def search_similar(
        self,
        query_vector: List[float],
        n_results: int = 5,
        score_threshold: float = 0.7
    ) -> List[dict]:
        """Search for similar messages using a query vector.

        Args:
            query_vector: The query embedding vector
            n_results: Maximum number of results to return
            score_threshold: Minimum similarity score threshold

        Returns:
            List of similar messages with their metadata
        """
        results = self.collection.query(
            query_embeddings=[query_vector],
            n_results=n_results,
            include=["metadatas", "documents", "distances"]
        )

        # Process and filter results
        similar_messages = []
        if results["distances"]:
            for i, distance in enumerate(results["distances"][0]):
                # Convert distance to similarity score (1 - normalized_distance)
                similarity_score = 1 - (distance / 2)  # ChromaDB uses L2 distance
                if similarity_score >= score_threshold:
                    similar_messages.append({
                        "text": results["documents"][0][i],
                        "metadata": results["metadatas"][0][i],
                        "similarity_score": similarity_score
                    })

        return similar_messages

    def get_message_by_id(self, message_id: str) -> Optional[dict]:
        """Retrieve a message by its ID.

        Args:
            message_id: The unique identifier of the message

        Returns:
            Message data if found, None otherwise
        """
        try:
            result = self.collection.get(
                ids=[message_id],
                include=["metadatas", "documents"]
            )
            if result["documents"]:
                return {
                    "text": result["documents"][0],
                    "metadata": result["metadatas"][0]
                }
        except Exception as e:
            logger.error("Error retrieving message %s: %s", message_id, e)
            return None

        return None

    def delete_messages(self, message_ids: List[str]) -> None:
        """Delete messages from the vector store.

        Args:
            message_ids: List of message IDs to delete
        """
        try:
            self.collection.delete(ids=message_ids)
            logger.info("Deleted %d messages from vector store", len(message_ids))
        except Exception as e:
            logger.error("Error deleting messages: %s", e)