# Slack AI Assistant

A Slack bot that uses RAG (Retrieval-Augmented Generation) to answer questions based on channel message history. Built with Python, Slack Bolt, and Google's Gemini API.

## Features

- Monitors specified Slack channels for mentions
- Searches through message history to find relevant information
- Uses RAG with Google's Gemini API to generate context-aware responses
- Provides source links to original messages with confidence scores
- Supports multiple channels

## Prerequisites

- Python 3.10 or higher
- Slack Workspace with admin access
- Google Cloud account with Gemini API access
- ChromaDB for vector storage

## Setup

1. Clone the repository:
```bash
git clone https://github.com/shahin99991/slack-ai-assistant.git
cd slack-ai-assistant
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Create a `.env` file in the project root with the following variables:
```env
# Slack Configuration
SLACK_BOT_TOKEN=your-bot-token
SLACK_APP_TOKEN=your-app-token
SLACK_SIGNING_SECRET=your-signing-secret
SLACK_CHANNEL_IDS=channel-id-1,channel-id-2

# Gemini API Configuration
GEMINI_API_KEY=your-gemini-api-key

# Application Configuration
CHROMA_PERSIST_DIRECTORY=data/chroma
DEBUG=true
LOG_LEVEL=DEBUG
MAX_RESPONSE_TIME=10
```

4. Start the bot:

As a Python script:
```bash
python src/main.py
```

As a system service:
```bash
# Start the bot
sudo systemctl start slackbot

# Stop the bot
sudo systemctl stop slackbot
```

For detailed operation instructions, see [Operations Manual](docs/operations.md).

## Usage

1. Invite the bot to your channel:
```
/invite @SlackAIBot
```

2. Mention the bot with your question:
```
@SlackAIBot What was discussed about project requirements?
```

The bot will:
- Search through channel history
- Find relevant messages
- Generate a response using RAG
- Provide links to source messages

## Project Structure

```
slack-ai-assistant/
├── src/
│   ├── main.py                 # Entry point
│   └── slack_bot/
│       ├── app.py             # Main application class
│       ├── config.py          # Configuration settings
│       └── services/
│           ├── slack_client.py    # Slack API client
│           ├── message_sync.py    # Message synchronization
│           ├── rag_system.py     # RAG implementation
│           └── vectorizer.py     # Text vectorization
├── tests/                     # Test files
├── data/                      # Vector store data
├── .env                       # Environment variables
├── .gitignore                # Git ignore rules
├── requirements.txt          # Python dependencies
└── README.md                 # This file
```

## Contributing

1. Fork the repository
2. Create a feature branch
3. Commit your changes
4. Push to the branch
5. Create a Pull Request

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

### License Summary
- ✅ Commercial use
- ✅ Modification
- ✅ Distribution
- ✅ Private use
- ❌ Liability
- ❌ Warranty

## Acknowledgments

- [Slack Bolt for Python](https://slack.dev/bolt-python/concepts)
- [Google Gemini API](https://ai.google.dev/)
- [ChromaDB](https://docs.trychroma.com/)
