"""Slack client service for interacting with the Slack API."""

import logging
from datetime import datetime
from typing import List, Optional

from slack_bolt import App
from slack_bolt.adapter.socket_mode import SocketModeHandler
from slack_sdk import WebClient
from slack_sdk.errors import SlackApiError

from ..config import Config
from ..models.message import SlackMessage

logger = logging.getLogger(__name__)


class SlackClient:
    """Service for interacting with Slack API."""

    def __init__(self, config: Config):
        """Initialize the Slack client.

        Args:
            config: Application configuration
        """
        self.config = config
        self.client = WebClient(token=config.slack_bot_token)
        self.app = App(
            token=config.slack_bot_token,
            signing_secret=config.slack_signing_secret,
            token_verification_enabled=True,  # Enable token verification for production
            process_before_response=True,
            logger=logging.getLogger("slack_bolt")
        )
        
        # Add middleware for logging
        @self.app.middleware
        def log_request(logger, body, next):
            logger.debug("Received request: %s", body)
            return next()

        self.handler = SocketModeHandler(
            app=self.app,
            app_token=config.slack_app_token
        )
        logger.info("Initialized Slack client")

    def start(self) -> None:
        """Start the Socket Mode handler."""
        self.handler.start()
        logger.info("Started Slack Socket Mode handler")

    def stop(self) -> None:
        """Stop the Socket Mode handler."""
        self.handler.close()
        logger.info("Stopped Slack Socket Mode handler")

    def get_bot_user_id(self) -> str:
        """Get the bot's user ID.

        Returns:
            The bot's user ID
        """
        try:
            response = self.client.auth_test()
            if response["ok"]:
                return response["user_id"]
            else:
                raise SlackApiError("Failed to get bot user ID", response)
        except SlackApiError as e:
            logger.error("Error getting bot user ID: %s", e)
            raise

    def fetch_channel_history(
        self,
        channel_id: str,
        oldest: Optional[float] = None,
        latest: Optional[float] = None
    ) -> List[SlackMessage]:
        """Fetch message history from a Slack channel.

        Args:
            channel_id: The ID of the channel to fetch messages from
            oldest: Timestamp of oldest message to fetch
            latest: Timestamp of latest message to fetch

        Returns:
            List of SlackMessage objects
        """
        messages = []
        try:
            # Fetch messages using pagination
            has_more = True
            cursor = None
            while has_more:
                response = self.client.conversations_history(
                    channel=channel_id,
                    cursor=cursor,
                    oldest=oldest,
                    latest=latest,
                    limit=100  # Maximum allowed by Slack API
                )

                if not response["ok"]:
                    logger.error(
                        "Error fetching messages from channel %s: %s",
                        channel_id,
                        response.get("error", "Unknown error")
                    )
                    break

                # Process messages
                for msg in response["messages"]:
                    if "subtype" in msg:  # Skip system messages
                        continue

                    # Get permalink for the message
                    try:
                        permalink_response = self.client.chat_getPermalink(
                            channel=channel_id,
                            message_ts=msg["ts"]
                        )
                        permalink = (
                            permalink_response["permalink"]
                            if permalink_response["ok"]
                            else None
                        )
                    except SlackApiError as e:
                        logger.warning(
                            "Error getting permalink for message %s: %s",
                            msg["ts"],
                            e
                        )
                        permalink = None

                    # Create SlackMessage object
                    message = SlackMessage(
                        message_id=msg["ts"],
                        channel_id=channel_id,
                        user_id=msg.get("user", "unknown"),
                        text=msg["text"],
                        timestamp=datetime.fromtimestamp(float(msg["ts"])),
                        thread_ts=msg.get("thread_ts"),
                        permalink=permalink,
                        reactions=[
                            reaction["name"]
                            for reaction in msg.get("reactions", [])
                        ]
                    )
                    messages.append(message)

                # Check for more messages
                cursor = response.get("response_metadata", {}).get("next_cursor")
                has_more = bool(cursor)

        except SlackApiError as e:
            logger.error(
                "Error fetching messages from channel %s: %s",
                channel_id,
                e
            )

        logger.info(
            "Fetched %d messages from channel %s",
            len(messages),
            channel_id
        )
        return messages

    def fetch_thread_replies(
        self,
        channel_id: str,
        thread_ts: str
    ) -> List[SlackMessage]:
        """Fetch replies in a message thread.

        Args:
            channel_id: The ID of the channel containing the thread
            thread_ts: Timestamp of the parent message

        Returns:
            List of SlackMessage objects representing the replies
        """
        replies = []
        try:
            response = self.client.conversations_replies(
                channel=channel_id,
                ts=thread_ts
            )

            if not response["ok"]:
                logger.error(
                    "Error fetching replies for thread %s: %s",
                    thread_ts,
                    response.get("error", "Unknown error")
                )
                return replies

            # Skip the first message (parent message)
            for msg in response["messages"][1:]:
                # Get permalink for the reply
                try:
                    permalink_response = self.client.chat_getPermalink(
                        channel=channel_id,
                        message_ts=msg["ts"]
                    )
                    permalink = (
                        permalink_response["permalink"]
                        if permalink_response["ok"]
                        else None
                    )
                except SlackApiError as e:
                    logger.warning(
                        "Error getting permalink for message %s: %s",
                        msg["ts"],
                        e
                    )
                    permalink = None

                reply = SlackMessage(
                    message_id=msg["ts"],
                    channel_id=channel_id,
                    user_id=msg.get("user", "unknown"),
                    text=msg["text"],
                    timestamp=datetime.fromtimestamp(float(msg["ts"])),
                    thread_ts=thread_ts,
                    permalink=permalink,
                    reactions=[
                        reaction["name"]
                        for reaction in msg.get("reactions", [])
                    ]
                )
                replies.append(reply)

        except SlackApiError as e:
            logger.error(
                "Error fetching replies for thread %s: %s",
                thread_ts,
                e
            )

        logger.info(
            "Fetched %d replies from thread %s",
            len(replies),
            thread_ts
        )
        return replies

    def send_message(
        self,
        channel_id: str,
        text: str,
        thread_ts: Optional[str] = None
    ) -> bool:
        """Send a message to a Slack channel.

        Args:
            channel_id: The ID of the channel to send the message to
            text: The message text to send
            thread_ts: Optional timestamp of a thread to reply to

        Returns:
            True if successful, False otherwise
        """
        try:
            response = self.client.chat_postMessage(
                channel=channel_id,
                text=text,
                thread_ts=thread_ts
            )
            return response["ok"]
        except SlackApiError as e:
            logger.error(
                "Error sending message to channel %s: %s",
                channel_id,
                e
            )
            return False