"""
RoraOS Slack Bot - Python Example
==================================

Simple Slack bot using RoraOS API.

Installation:
    pip install slack-bolt requests

Setup:
    1. Create app at api.slack.com/apps
    2. Enable Socket Mode
    3. Add Bot Token Scopes: chat:write, app_mentions:read, im:history
    4. Install app to workspace
    5. Copy Bot Token and App Token
    6. Run: python slack_bot.py

Features:
    - Mention bot to chat (@botname)
    - Direct message with bot
    - Thread support
"""

import os
import logging
import requests
from slack_bolt import App
from slack_bolt.adapter.socket_mode import SocketModeHandler

# Configuration
SLACK_BOT_TOKEN = os.getenv("SLACK_BOT_TOKEN", "xoxb-your-bot-token")
SLACK_APP_TOKEN = os.getenv("SLACK_APP_TOKEN", "xapp-your-app-token")
API_URL = "https://labs.roraos.com/api/v1/chat"
API_KEY = os.getenv("RORAOS_API_KEY", "your-api-key-here")

# Logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize Slack app
app = App(token=SLACK_BOT_TOKEN)

# Conversation storage per thread/channel
conversations = {}


def get_conversation_key(channel: str, thread_ts: str = None) -> str:
    """Generate unique key for conversation."""
    return f"{channel}:{thread_ts or 'main'}"


def get_ai_response(conv_key: str, message: str) -> str:
    """Get response from RoraOS API."""

    if conv_key not in conversations:
        conversations[conv_key] = [
            {"role": "system", "content": "You are a helpful AI assistant on Slack. Give clear and concise answers. Use emoji when appropriate."}
        ]

    conversations[conv_key].append({"role": "user", "content": message})

    # Limit history
    if len(conversations[conv_key]) > 21:
        conversations[conv_key] = [conversations[conv_key][0]] + conversations[conv_key][-20:]

    try:
        response = requests.post(
            API_URL,
            headers={
                "Authorization": f"Bearer {API_KEY}",
                "Content-Type": "application/json"
            },
            json={
                "messages": conversations[conv_key],
                "model": "gpt-4o",
                "temperature": 0.7,
                "max_tokens": 1000
            },
            timeout=60
        )
        response.raise_for_status()

        data = response.json()
        assistant_message = data["choices"][0]["message"]["content"]

        conversations[conv_key].append({"role": "assistant", "content": assistant_message})

        return assistant_message

    except requests.exceptions.RequestException as e:
        logger.error(f"API Error: {e}")
        return "Sorry, an error occurred. Please try again."


@app.event("app_mention")
def handle_mention(event, say, client):
    """Handle when bot is mentioned."""
    channel = event["channel"]
    thread_ts = event.get("thread_ts", event["ts"])
    user = event["user"]

    # Remove bot mention from text
    text = event["text"]
    # Simple removal of mention (you might need to adjust based on your bot's user ID)
    text = " ".join(word for word in text.split() if not word.startswith("<@"))
    text = text.strip()

    if not text:
        say(
            text="Hello! How can I help?",
            thread_ts=thread_ts
        )
        return

    conv_key = get_conversation_key(channel, thread_ts)

    # Show typing indicator
    try:
        response = get_ai_response(conv_key, text)
        say(text=response, thread_ts=thread_ts)
    except Exception as e:
        logger.error(f"Error: {e}")
        say(text="Oops, something went wrong!", thread_ts=thread_ts)


@app.event("message")
def handle_direct_message(event, say, client):
    """Handle direct messages."""
    # Only respond to DMs (channel type 'im')
    channel_type = event.get("channel_type")
    if channel_type != "im":
        return

    # Ignore bot messages
    if event.get("bot_id"):
        return

    channel = event["channel"]
    text = event.get("text", "")
    thread_ts = event.get("thread_ts", event["ts"])

    if not text:
        return

    conv_key = get_conversation_key(channel, thread_ts)

    try:
        response = get_ai_response(conv_key, text)
        say(text=response, thread_ts=thread_ts)
    except Exception as e:
        logger.error(f"Error: {e}")
        say(text="Oops, something went wrong!", thread_ts=thread_ts)


@app.command("/ai")
def handle_slash_command(ack, respond, command):
    """Handle /ai slash command."""
    ack()

    text = command.get("text", "").strip()
    channel = command["channel_id"]

    if not text:
        respond("Usage: `/ai [question]`")
        return

    conv_key = get_conversation_key(channel)

    try:
        response = get_ai_response(conv_key, text)
        respond(response)
    except Exception as e:
        logger.error(f"Error: {e}")
        respond("Oops, something went wrong!")


@app.command("/clear")
def handle_clear_command(ack, respond, command):
    """Handle /clear slash command to clear conversation."""
    ack()

    channel = command["channel_id"]
    conv_key = get_conversation_key(channel)

    if conv_key in conversations:
        del conversations[conv_key]

    respond("Conversation history cleared!")


def main():
    """Start the Slack bot."""
    handler = SocketModeHandler(app, SLACK_APP_TOKEN)
    logger.info("Slack bot is running!")
    handler.start()


if __name__ == "__main__":
    main()
