"""
RoraOS Telegram Bot - Python Example
======================================

Simple Telegram bot using RoraOS API.
Can answer questions and have conversations.

Installation:
    pip install python-telegram-bot requests

Setup:
    1. Create bot at @BotFather and get token
    2. Replace BOT_TOKEN and API_KEY below
    3. Run: python telegram_bot.py

Features:
    - /start - Start bot
    - /clear - Clear conversation history
    - /help - Show help
    - Reply to all messages with AI
"""

import os
import logging
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes
import requests

# Configuration
BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN", "your-telegram-bot-token")
API_URL = "https://labs.roraos.com/api/v1/chat"
API_KEY = os.getenv("RORAOS_API_KEY", "your-api-key-here")

# Logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# Storage for conversation history per user
conversations = {}


def get_ai_response(user_id: int, message: str) -> str:
    """Send message to RoraOS API and get response."""

    # Initialize history if not exists
    if user_id not in conversations:
        conversations[user_id] = [
            {"role": "system", "content": "You are a friendly and helpful AI assistant. Match the user's language."}
        ]

    # Add user message
    conversations[user_id].append({"role": "user", "content": message})

    # Limit history to avoid it getting too long (max 20 messages)
    if len(conversations[user_id]) > 21:
        conversations[user_id] = [conversations[user_id][0]] + conversations[user_id][-20:]

    try:
        response = requests.post(
            API_URL,
            headers={
                "Authorization": f"Bearer {API_KEY}",
                "Content-Type": "application/json"
            },
            json={
                "messages": conversations[user_id],
                "model": "gpt-4o",
                "temperature": 0.7,
                "max_tokens": 1000
            },
            timeout=60
        )
        response.raise_for_status()

        data = response.json()
        assistant_message = data["choices"][0]["message"]["content"]

        # Save response to history
        conversations[user_id].append({"role": "assistant", "content": assistant_message})

        return assistant_message

    except requests.exceptions.RequestException as e:
        logger.error(f"API Error: {e}")
        return "Sorry, an error occurred while processing your message. Please try again."


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handler for /start command"""
    user = update.effective_user
    await update.message.reply_html(
        f"Hello {user.mention_html()}!\n\n"
        f"I'm an AI Assistant powered by RoraOS.\n\n"
        f"<b>Commands:</b>\n"
        f"/start - Start bot\n"
        f"/clear - Clear conversation history\n"
        f"/help - Show help\n\n"
        f"Send any message and I'll help!"
    )


async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handler for /help command"""
    await update.message.reply_text(
        "RoraOS AI Bot\n\n"
        "I can help you with:\n"
        "- Answering questions\n"
        "- Writing code\n"
        "- Explaining concepts\n"
        "- Brainstorming\n"
        "- And more!\n\n"
        "Just send a message and I'll respond.\n\n"
        "Tip: Use /clear to start a new conversation."
    )


async def clear(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handler for /clear command"""
    user_id = update.effective_user.id
    if user_id in conversations:
        del conversations[user_id]
    await update.message.reply_text("Conversation history cleared. Let's start a new conversation!")


async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handler for all text messages"""
    user_id = update.effective_user.id
    user_message = update.message.text

    # Send typing indicator
    await context.bot.send_chat_action(chat_id=update.effective_chat.id, action="typing")

    # Get response from AI
    response = get_ai_response(user_id, user_message)

    # Send response (split if too long)
    if len(response) > 4096:
        for i in range(0, len(response), 4096):
            await update.message.reply_text(response[i:i+4096])
    else:
        await update.message.reply_text(response)


async def error_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Log errors"""
    logger.error(f"Update {update} caused error {context.error}")


def main() -> None:
    """Start the bot."""
    # Create Application
    application = Application.builder().token(BOT_TOKEN).build()

    # Register handlers
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("help", help_command))
    application.add_handler(CommandHandler("clear", clear))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

    # Register error handler
    application.add_error_handler(error_handler)

    # Start bot
    logger.info("Bot started!")
    application.run_polling(allowed_updates=Update.ALL_TYPES)


if __name__ == "__main__":
    main()
