"""
RoraOS WhatsApp Bot - Python Example
======================================

WhatsApp bot using whatsapp-web.js library via Python.
Uses wa-automate-python or green-api library.

Method 1: Using Green API (Recommended - No Session needed)
Method 2: Using whatsapp-web.js with bridge

Installation (Green API):
    pip install requests

Setup Green API:
    1. Register at green-api.com
    2. Create instance and get credentials
    3. Scan QR code
    4. Run script

Usage:
    python whatsapp_bot.py
"""

import os
import time
import requests
from typing import Optional
import json

# =====================================================
# CONFIGURATION
# =====================================================

# RoraOS API
RORAOS_API_URL = "https://labs.roraos.com/api/v1/chat"
RORAOS_API_KEY = os.getenv("RORAOS_API_KEY", "your-api-key-here")

# Green API (for WhatsApp)
GREEN_API_ID = os.getenv("GREEN_API_ID", "your-instance-id")
GREEN_API_TOKEN = os.getenv("GREEN_API_TOKEN", "your-api-token")
GREEN_API_URL = f"https://api.green-api.com/waInstance{GREEN_API_ID}"

# Bot settings
BOT_NAME = "RoraOS Bot"
SYSTEM_PROMPT = """You are a friendly AI assistant on WhatsApp.
- Give clear and concise answers
- Use appropriate emoji
- If asked something you don't know, be honest
"""

# Storage for conversation per phone number
conversations = {}


# =====================================================
# AI RESPONSE
# =====================================================

def get_ai_response(phone_number: str, message: str) -> str:
    """Get response from RoraOS API."""

    # Initialize conversation if not exists
    if phone_number not in conversations:
        conversations[phone_number] = [
            {"role": "system", "content": SYSTEM_PROMPT}
        ]

    # Add user message
    conversations[phone_number].append({"role": "user", "content": message})

    # Limit history (max 20 messages)
    if len(conversations[phone_number]) > 21:
        conversations[phone_number] = [
            conversations[phone_number][0]
        ] + conversations[phone_number][-20:]

    try:
        response = requests.post(
            RORAOS_API_URL,
            headers={
                "Authorization": f"Bearer {RORAOS_API_KEY}",
                "Content-Type": "application/json"
            },
            json={
                "messages": conversations[phone_number],
                "model": "gpt-4o",
                "temperature": 0.7,
                "max_tokens": 500  # WhatsApp messages should be short
            },
            timeout=60
        )
        response.raise_for_status()

        data = response.json()
        ai_response = data["choices"][0]["message"]["content"]

        # Save to history
        conversations[phone_number].append({
            "role": "assistant",
            "content": ai_response
        })

        return ai_response

    except requests.exceptions.RequestException as e:
        print(f"API Error: {e}")
        return "Sorry, an error occurred. Please try again later."


# =====================================================
# GREEN API FUNCTIONS
# =====================================================

def send_message(phone_number: str, message: str) -> bool:
    """Send WhatsApp message via Green API."""
    try:
        url = f"{GREEN_API_URL}/sendMessage/{GREEN_API_TOKEN}"

        # Format number (add @c.us if needed)
        chat_id = phone_number if "@" in phone_number else f"{phone_number}@c.us"

        response = requests.post(url, json={
            "chatId": chat_id,
            "message": message
        })

        return response.ok

    except Exception as e:
        print(f"Send message error: {e}")
        return False


def receive_notification() -> Optional[dict]:
    """Receive notification from Green API."""
    try:
        url = f"{GREEN_API_URL}/receiveNotification/{GREEN_API_TOKEN}"
        response = requests.get(url, timeout=20)

        if response.ok and response.text:
            data = response.json()
            return data

        return None

    except Exception as e:
        # Timeout is normal when no messages
        if "timeout" not in str(e).lower():
            print(f"Receive notification error: {e}")
        return None


def delete_notification(receipt_id: int) -> bool:
    """Delete processed notification."""
    try:
        url = f"{GREEN_API_URL}/deleteNotification/{GREEN_API_TOKEN}/{receipt_id}"
        response = requests.delete(url)
        return response.ok

    except Exception as e:
        print(f"Delete notification error: {e}")
        return False


def process_incoming_message(notification: dict) -> None:
    """Process incoming message."""
    try:
        body = notification.get("body", {})
        message_data = body.get("messageData", {})

        # Get message type and content
        type_message = body.get("typeWebhook")

        if type_message != "incomingMessageReceived":
            return

        # Get sender info
        sender = body.get("senderData", {})
        phone = sender.get("chatId", "").replace("@c.us", "")
        sender_name = sender.get("senderName", "Unknown")

        # Get message content
        text_message = message_data.get("textMessageData", {})
        message = text_message.get("textMessage", "")

        # Also handle extended text messages
        if not message:
            extended = message_data.get("extendedTextMessageData", {})
            message = extended.get("text", "")

        if not message:
            return

        print(f"Message from {sender_name} ({phone}): {message}")

        # Handle commands
        if message.lower() == "/start":
            response = f"Hello {sender_name}!\n\nI am {BOT_NAME}, an AI assistant here to help.\n\nType any message and I'll respond!\n\nType /clear to reset conversation."
        elif message.lower() == "/clear":
            if phone in conversations:
                del conversations[phone]
            response = "Conversation history cleared.\n\nFeel free to start a new conversation!"
        elif message.lower() == "/help":
            response = f"*{BOT_NAME}*\n\n*Commands:*\n/start - Start bot\n/clear - Reset conversation\n/help - Show help\n\nSend any message and I'll help!"
        else:
            # Get AI response
            response = get_ai_response(phone, message)

        # Send response
        success = send_message(phone, response)
        if success:
            print(f"Sent response to {phone}")
        else:
            print(f"Failed to send response to {phone}")

    except Exception as e:
        print(f"Process message error: {e}")


def run_bot():
    """Main bot loop."""
    print("=" * 50)
    print(f"{BOT_NAME} Starting...")
    print("=" * 50)
    print(f"Green API Instance: {GREEN_API_ID}")
    print("Waiting for messages...")
    print("=" * 50)

    while True:
        try:
            # Receive notification
            notification = receive_notification()

            if notification:
                receipt_id = notification.get("receiptId")

                # Process message
                process_incoming_message(notification)

                # Delete notification
                if receipt_id:
                    delete_notification(receipt_id)

            # Small delay to prevent excessive API calls
            time.sleep(0.5)

        except KeyboardInterrupt:
            print("\nBot stopped!")
            break
        except Exception as e:
            print(f"Bot error: {e}")
            time.sleep(5)  # Wait before retry


# =====================================================
# ALTERNATIVE: Simple Webhook Mode
# =====================================================

"""
If using webhook, create Flask server:

from flask import Flask, request

app = Flask(__name__)

@app.route('/webhook', methods=['POST'])
def webhook():
    data = request.json
    process_incoming_message({"body": data})
    return "OK", 200

if __name__ == "__main__":
    app.run(port=5000)
"""


# =====================================================
# MAIN
# =====================================================

if __name__ == "__main__":
    run_bot()
