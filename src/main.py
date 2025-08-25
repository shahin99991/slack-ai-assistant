"""Entry point for the Slack AI Bot."""

import asyncio
import logging
import os
import signal
import sys
from pathlib import Path

from dotenv import load_dotenv

from slack_bot.app import SlackAIBot
from slack_bot.config import Config

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(
    level=logging.DEBUG,
    handlers=[logging.StreamHandler()],
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


async def main():
    """Main entry point for the application."""
    try:
        # Load configuration
        config = Config.from_env()

        # Create data directory if it doesn't exist
        Path(config.chroma_persist_directory).parent.mkdir(
            parents=True,
            exist_ok=True
        )

        # Initialize and start the bot
        bot = SlackAIBot(config)
        bot.start()

        # Set up signal handlers
        loop = asyncio.get_running_loop()
        for sig in (signal.SIGTERM, signal.SIGINT):
            loop.add_signal_handler(
                sig,
                lambda s=sig: asyncio.create_task(handle_signal(s, bot, loop))
            )

        # Keep the bot running
        while True:
            await asyncio.sleep(1)

    except Exception as e:
        logger.error("Error in main: %s", e)
        sys.exit(1)


async def handle_signal(sig: signal.Signals, bot: SlackAIBot, loop: asyncio.AbstractEventLoop):
    """Handle termination signals.

    Args:
        sig: The signal received
        bot: The Slack AI Bot instance
        loop: The event loop
    """
    logger.info("Received signal %s", sig.name)
    bot.stop()
    loop.stop()


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logger.info("Application stopped by user")
    except Exception as e:
        logger.error("Unhandled error: %s", e)
        sys.exit(1)