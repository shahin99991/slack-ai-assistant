"""Main application class for the Slack AI Bot."""

import asyncio
import logging
import re
from typing import Dict, List, Optional

from .config import Config
from .database.vector_store import VectorStore
from .services.message_sync import MessageSync
from .services.rag_system import RAGSystem
from .services.slack_client import SlackClient
from .services.vectorizer import Vectorizer

logger = logging.getLogger(__name__)


class SlackAIBot:
    """Main application class for the Slack AI Bot."""

    def __init__(self, config: Config):
        """Initialize the Slack AI Bot.

        Args:
            config: Application configuration
        """
        self.config = config
        self.conversation_history: Dict[str, List[dict]] = {}

        # Initialize services
        self.slack_client = SlackClient(config)
        self.vectorizer = Vectorizer(config)
        self.vector_store = VectorStore(config)
        self.message_sync = MessageSync(
            slack_client=self.slack_client,
            vectorizer=self.vectorizer,
            vector_store=self.vector_store
        )
        self.rag_system = RAGSystem(
            vectorizer=self.vectorizer,
            vector_store=self.vector_store
        )

        # Get bot user ID
        self.bot_user_id = self.slack_client.get_bot_user_id()
        logger.info("Bot user ID: %s", self.bot_user_id)

        # Register event handlers
        @self.slack_client.app.event("app_mention")
        def _handle_mention(event):
            logger.debug("Received app_mention event: %s", event)
            try:
                self.handle_mention(event)
                logger.info("Handled mention successfully")
            except Exception as e:
                logger.error("Error in _handle_mention: %s", e, exc_info=True)

        @self.slack_client.app.event("message")
        def _handle_message(event):
            logger.debug("Received message event: %s", event)
            return self.handle_message(event)

        logger.info("Initialized Slack AI Bot")

    def start(self) -> None:
        """Start the Slack AI Bot."""
        # Initial sync of messages
        for channel_id in self.config.slack_channel_ids:
            try:
                self.message_sync.sync_channel(channel_id)
            except Exception as e:
                logger.error(
                    "Error during initial sync of channel %s: %s",
                    channel_id,
                    e
                )

        # Start the Slack client
        self.slack_client.start()
        logger.info("Started Slack AI Bot")

    def stop(self) -> None:
        """Stop the Slack AI Bot."""
        self.slack_client.stop()
        logger.info("Stopped Slack AI Bot")

    def handle_mention(self, event: dict) -> None:
        """Handle mentions of the bot.

        Args:
            event: The Slack event data
        """
        try:
            # 重複イベントのチェック
            event_id = event.get("event_ts", "")
            if hasattr(self, '_last_event_id') and self._last_event_id == event_id:
                logger.debug("Skipping duplicate event: %s", event_id)
                return
            self._last_event_id = event_id

            logger.debug("Received mention event: %s", event)
            # Extract the question (remove the mention)
            mention_pattern = f"<@{self.bot_user_id}>"
            question = re.sub(mention_pattern, "", event["text"]).strip()

            if not question:
                self.slack_client.send_message(
                    channel_id=event["channel"],
                    text="こんにちは！質問がありましたら、お気軽にお尋ねください。",
                    thread_ts=event.get("thread_ts")
                )
                return

            # Get conversation history for the thread
            thread_ts = event.get("thread_ts", event["ts"])
            history = self.conversation_history.get(thread_ts, [])

            # Generate answer
            answer, relevant_messages = self.rag_system.answer_question(
                question=question,
                conversation_history=history
            )

            # Update conversation history
            history.append({
                "question": question,
                "answer": answer
            })
            self.conversation_history[thread_ts] = history[-5:]  # Keep last 5

            # Format response with source links
            response = self._format_response(answer, relevant_messages)

            # Send response
            self.slack_client.send_message(
                channel_id=event["channel"],
                text=response,
                thread_ts=event.get("thread_ts")
            )

        except Exception as e:
            logger.error("Error handling mention: %s", e)
            self.slack_client.send_message(
                channel_id=event["channel"],
                text="申し訳ありません。エラーが発生しました。",
                thread_ts=event.get("thread_ts")
            )

    def handle_message(self, event: dict) -> None:
        """Handle new messages for syncing.

        Args:
            event: The Slack event data
        """
        try:
            # Skip if it's a bot message or a message edit
            if (
                event.get("subtype") or
                event.get("bot_id") or
                "edited" in event
            ):
                return

            # Skip if channel is not in monitored list
            if event["channel"] not in self.config.slack_channel_ids:
                return

            # Sync the new message
            self.message_sync.sync_channel(
                channel_id=event["channel"],
                latest=float(event["ts"]) + 1,
                oldest=float(event["ts"])
            )

        except Exception as e:
            logger.error("Error handling message: %s", e)

    def _format_response(
        self,
        answer: str,
        relevant_messages: List[dict]
    ) -> str:
        """Format the response with source links.

        Args:
            answer: The generated answer
            relevant_messages: List of relevant messages used for context

        Returns:
            Formatted response string
        """
        response_parts = [answer, "\n\n参考メッセージ:"]

        for i, msg in enumerate(relevant_messages, 1):
            metadata = msg["metadata"]
            if metadata.get("permalink"):
                response_parts.append(
                    f"{i}. <{metadata['permalink']}|元のメッセージを表示> "
                    f"(信頼度: {msg['similarity_score']:.2f})"
                )

        return "\n".join(response_parts)