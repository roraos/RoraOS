"""
RoraOS LINE Bot - Python Example
=================================

LINE bot using LINE Messaging API with RoraOS.

Installation:
    pip install line-bot-sdk flask requests

Setup:
    1. Create channel at LINE Developers Console
    2. Get Channel Secret and Channel Access Token
    3. Set webhook URL to your server
    4. Run: python line_bot.py

Usage with ngrok for development:
    ngrok http 5000
    Set webhook URL in LINE console to ngrok URL + /callback
"""

import os
from flask import Flask, request, abort
from linebot.v3 import WebhookHandler
from linebot.v3.exceptions import InvalidSignatureError
from linebot.v3.messaging import (
    Configuration,
    ApiClient,
    MessagingApi,
    ReplyMessageRequest,
    TextMessage,
)
from linebot.v3.webhooks import (
    MessageEvent,
    TextMessageContent,
    FollowEvent,
)
import requests

# =====================================================
# CONFIGURATION
# =====================================================

# LINE Config
LINE_CHANNEL_SECRET = os.getenv("LINE_CHANNEL_SECRET", "your-channel-secret")
LINE_CHANNEL_ACCESS_TOKEN = os.getenv("LINE_CHANNEL_ACCESS_TOKEN", "your-channel-access-token")

# RoraOS Config
RORAOS_API_URL = "https://labs.roraos.com/api/v1/chat"
RORAOS_API_KEY = os.getenv("RORAOS_API_KEY", "your-api-key-here")

# Bot Config
SYSTEM_PROMPT = """You are a friendly AI assistant on LINE.
- Give clear and concise answers (max 2000 characters)
- Use appropriate emoji
- Language: match user's language
"""

# Flask app
app = Flask(__name__)

# LINE SDK
configuration = Configuration(access_token=LINE_CHANNEL_ACCESS_TOKEN)
handler = WebhookHandler(LINE_CHANNEL_SECRET)

# Conversation storage
conversations = {}


# =====================================================
# AI RESPONSE
# =====================================================

def get_ai_response(user_id: str, message: str) -> str:
    """Get response from RoraOS API."""

    # Initialize conversation
    if user_id not in conversations:
        conversations[user_id] = [
            {"role": "system", "content": SYSTEM_PROMPT}
        ]

    # Add user message
    conversations[user_id].append({"role": "user", "content": message})

    # Limit history
    if len(conversations[user_id]) > 21:
        conversations[user_id] = [
            conversations[user_id][0]
        ] + conversations[user_id][-20:]

    try:
        response = requests.post(
            RORAOS_API_URL,
            headers={
                "Authorization": f"Bearer {RORAOS_API_KEY}",
                "Content-Type": "application/json"
            },
            json={
                "messages": conversations[user_id],
                "model": "gpt-4o",
                "temperature": 0.7,
                "max_tokens": 500
            },
            timeout=60
        )
        response.raise_for_status()

        data = response.json()
        ai_response = data["choices"][0]["message"]["content"]

        # Save to history
        conversations[user_id].append({
            "role": "assistant",
            "content": ai_response
        })

        # LINE has 2000 char limit
        if len(ai_response) > 2000:
            ai_response = ai_response[:1997] + "..."

        return ai_response

    except Exception as e:
        print(f"API Error: {e}")
        return "Sorry, an error occurred. Please try again."


# =====================================================
# LINE HANDLERS
# =====================================================

@app.route("/callback", methods=["POST"])
def callback():
    """LINE webhook callback."""
    signature = request.headers.get("X-Line-Signature", "")
    body = request.get_data(as_text=True)

    try:
        handler.handle(body, signature)
    except InvalidSignatureError:
        abort(400)

    return "OK"


@handler.add(FollowEvent)
def handle_follow(event):
    """Handle when user follows/adds the bot."""
    with ApiClient(configuration) as api_client:
        line_bot_api = MessagingApi(api_client)
        line_bot_api.reply_message(
            ReplyMessageRequest(
                reply_token=event.reply_token,
                messages=[
                    TextMessage(text="Hello!\n\nI'm an AI Assistant powered by RoraOS.\n\nSend any message and I'll help!\n\nType 'reset' to start a new conversation.")
                ]
            )
        )


@handler.add(MessageEvent, message=TextMessageContent)
def handle_message(event):
    """Handle text messages."""
    user_id = event.source.user_id
    user_message = event.message.text.strip()

    # Handle commands
    if user_message.lower() in ["reset", "clear", "/reset", "/clear"]:
        if user_id in conversations:
            del conversations[user_id]
        reply_text = "Conversation reset!\n\nFeel free to start a new conversation."
    elif user_message.lower() in ["help", "/help"]:
        reply_text = """*RoraOS AI Bot*

I can help you with:
- Answering questions
- Writing text
- Translation
- And more!

Commands:
- reset - Reset conversation
- help - Show help

Send any message!"""
    else:
        # Get AI response
        reply_text = get_ai_response(user_id, user_message)

    # Reply
    with ApiClient(configuration) as api_client:
        line_bot_api = MessagingApi(api_client)
        line_bot_api.reply_message(
            ReplyMessageRequest(
                reply_token=event.reply_token,
                messages=[TextMessage(text=reply_text)]
            )
        )


# =====================================================
# HEALTH CHECK
# =====================================================

@app.route("/health", methods=["GET"])
def health():
    return {"status": "healthy", "bot": "line-roraos"}


# =====================================================
# MAIN
# =====================================================

if __name__ == "__main__":
    print("=" * 50)
    print("LINE Bot Starting...")
    print("=" * 50)
    print(f"Webhook URL: http://your-domain/callback")
    print("=" * 50)

    app.run(host="0.0.0.0", port=5000, debug=True)
