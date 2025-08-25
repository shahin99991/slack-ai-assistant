"""Service for synchronizing Slack messages with the vector database."""

import logging
from datetime import datetime, timedelta
from typing import List, Optional, Tuple

from ..database.vector_store import VectorStore
from ..models.message import MessageVector, SlackMessage
from ..services.slack_client import SlackClient
from ..services.vectorizer import Vectorizer

logger = logging.getLogger(__name__)


class MessageSync:
    """Service for synchronizing Slack messages with the vector database."""

    def __init__(
        self,
        slack_client: SlackClient,
        vectorizer: Vectorizer,
        vector_store: VectorStore
    ):
        """Initialize the message sync service.

        Args:
            slack_client: Slack client service
            vectorizer: Vectorizer service
            vector_store: Vector database service
        """
        self.slack_client = slack_client
        self.vectorizer = vectorizer
        self.vector_store = vector_store
        logger.info("Initialized message sync service")

    def sync_channel(
        self,
        channel_id: str,
        oldest: Optional[float] = None,
        latest: Optional[float] = None
    ) -> int:
        """Synchronize messages from a Slack channel.

        Args:
            channel_id: The ID of the channel to sync
            oldest: Optional timestamp of oldest message to sync
            latest: Optional timestamp of latest message to sync

        Returns:
            Number of messages synchronized
        """
        # Fetch messages from Slack
        messages = self.slack_client.fetch_channel_history(
            channel_id=channel_id,
            oldest=oldest,
            latest=latest
        )

        if not messages:
            logger.info("No messages to sync from channel %s", channel_id)
            return 0

        # Fetch thread replies
        thread_messages = []
        for message in messages:
            if message.thread_ts:
                replies = self.slack_client.fetch_thread_replies(
                    channel_id=channel_id,
                    thread_ts=message.thread_ts
                )
                thread_messages.extend(replies)

        # Combine main messages and thread replies
        all_messages = messages + thread_messages

        # Vectorize messages
        vectors = self.vectorizer.vectorize_messages(all_messages)

        # Create message-vector pairs
        pairs: List[Tuple[SlackMessage, MessageVector]] = []
        for message in all_messages:
            vector = next(
                (v for v in vectors if v.message_id == message.message_id),
                None
            )
            if vector:
                pairs.append((message, vector))

        # Add to vector store
        if pairs:
            self.vector_store.add_messages(pairs)

        logger.info(
            "Synchronized %d messages from channel %s",
            len(pairs),
            channel_id
        )
        return len(pairs)

    def sync_recent_messages(
        self,
        channel_ids: List[str],
        hours: int = 24
    ) -> int:
        """Synchronize recent messages from multiple channels.

        Args:
            channel_ids: List of channel IDs to sync
            hours: Number of hours of history to sync

        Returns:
            Total number of messages synchronized
        """
        latest = datetime.now().timestamp()
        oldest = (datetime.now() - timedelta(hours=hours)).timestamp()
        total_synced = 0

        for channel_id in channel_ids:
            try:
                synced = self.sync_channel(
                    channel_id=channel_id,
                    oldest=oldest,
                    latest=latest
                )
                total_synced += synced
            except Exception as e:
                logger.error(
                    "Error syncing channel %s: %s",
                    channel_id,
                    e
                )

        logger.info(
            "Synchronized %d messages from %d channels in the last %d hours",
            total_synced,
            len(channel_ids),
            hours
        )
        return total_synced

    def sync_full_history(self, channel_ids: List[str]) -> int:
        """Synchronize full message history from multiple channels.

        Args:
            channel_ids: List of channel IDs to sync

        Returns:
            Total number of messages synchronized
        """
        total_synced = 0

        for channel_id in channel_ids:
            try:
                synced = self.sync_channel(channel_id=channel_id)
                total_synced += synced
            except Exception as e:
                logger.error(
                    "Error syncing channel %s: %s",
                    channel_id,
                    e
                )

        logger.info(
            "Synchronized %d messages from %d channels (full history)",
            total_synced,
            len(channel_ids)
        )
        return total_synced
