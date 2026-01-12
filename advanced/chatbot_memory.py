"""
RoraOS Chatbot with Memory - Python Example
=============================================

Chatbot with more advanced memory/context management.
Includes summarization feature for long conversations.

Installation:
    pip install requests

Usage:
    python chatbot_memory.py

Features:
    - Conversation memory with sliding window
    - Automatic summarization for long context
    - Personality customization
    - Export/import conversation
"""

import requests
import json
from datetime import datetime
from typing import List, Dict, Optional

# Configuration
API_URL = "https://labs.roraos.com/api/v1/chat"
API_KEY = "your-api-key-here"


class Message:
    """Represent a chat message."""

    def __init__(self, role: str, content: str, timestamp: datetime = None):
        self.role = role
        self.content = content
        self.timestamp = timestamp or datetime.now()

    def to_dict(self) -> Dict:
        return {"role": self.role, "content": self.content}

    def to_json(self) -> Dict:
        return {
            "role": self.role,
            "content": self.content,
            "timestamp": self.timestamp.isoformat()
        }

    @classmethod
    def from_json(cls, data: Dict) -> "Message":
        return cls(
            role=data["role"],
            content=data["content"],
            timestamp=datetime.fromisoformat(data["timestamp"]) if "timestamp" in data else None
        )


class ConversationMemory:
    """Manage conversation memory with summarization."""

    def __init__(
        self,
        max_messages: int = 20,
        summarize_threshold: int = 15,
        system_prompt: str = None
    ):
        self.max_messages = max_messages
        self.summarize_threshold = summarize_threshold
        self.system_prompt = system_prompt or "You are a helpful AI assistant."
        self.messages: List[Message] = []
        self.summary: Optional[str] = None

    def add_message(self, role: str, content: str) -> None:
        """Add a message to memory."""
        self.messages.append(Message(role, content))

        # Check if we need to summarize
        if len(self.messages) >= self.summarize_threshold:
            self._summarize_old_messages()

    def _summarize_old_messages(self) -> None:
        """Summarize old messages to save context space."""
        if len(self.messages) < self.summarize_threshold:
            return

        # Keep last few messages, summarize the rest
        messages_to_summarize = self.messages[:-5]
        self.messages = self.messages[-5:]

        # Create summary prompt
        summary_text = "\n".join([
            f"{m.role}: {m.content}" for m in messages_to_summarize
        ])

        try:
            summary_messages = [
                {"role": "system", "content": "Summarize this conversation briefly in 2-3 sentences. Focus on key topics and decisions."},
                {"role": "user", "content": summary_text}
            ]

            response = requests.post(
                API_URL,
                headers={
                    "Authorization": f"Bearer {API_KEY}",
                    "Content-Type": "application/json"
                },
                json={
                    "messages": summary_messages,
                    "model": "gpt-4o",
                    "temperature": 0.3,
                    "max_tokens": 200
                },
                timeout=30
            )

            if response.ok:
                data = response.json()
                new_summary = data["choices"][0]["message"]["content"]

                if self.summary:
                    self.summary = f"{self.summary}\n{new_summary}"
                else:
                    self.summary = new_summary

                print(f"[Memory] Summarized {len(messages_to_summarize)} messages")

        except Exception as e:
            print(f"[Memory] Failed to summarize: {e}")

    def get_context_messages(self) -> List[Dict]:
        """Get messages for API call with context."""
        context = [{"role": "system", "content": self.system_prompt}]

        # Add summary if exists
        if self.summary:
            context.append({
                "role": "system",
                "content": f"Previous conversation summary:\n{self.summary}"
            })

        # Add recent messages
        for msg in self.messages[-self.max_messages:]:
            context.append(msg.to_dict())

        return context

    def clear(self) -> None:
        """Clear all memory."""
        self.messages = []
        self.summary = None

    def export_conversation(self, filename: str) -> None:
        """Export conversation to file."""
        data = {
            "exported_at": datetime.now().isoformat(),
            "system_prompt": self.system_prompt,
            "summary": self.summary,
            "messages": [m.to_json() for m in self.messages]
        }
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        print(f"Exported to {filename}")

    def import_conversation(self, filename: str) -> None:
        """Import conversation from file."""
        with open(filename, 'r', encoding='utf-8') as f:
            data = json.load(f)
        self.system_prompt = data.get("system_prompt", self.system_prompt)
        self.summary = data.get("summary")
        self.messages = [Message.from_json(m) for m in data.get("messages", [])]
        print(f"Imported {len(self.messages)} messages from {filename}")


class Chatbot:
    """Chatbot with personality and memory."""

    PERSONALITIES = {
        "friendly": "You are a friendly, warm, and helpful AI assistant. Use casual and friendly language.",
        "professional": "You are a professional and formal assistant. Give precise and to-the-point answers.",
        "creative": "You are a creative and imaginative assistant. You like using analogies and metaphors.",
        "teacher": "You are a patient teacher who loves explaining. Use examples and break down complex concepts.",
        "coder": "You are an expert programmer. Provide clean, well-documented code following best practices."
    }

    def __init__(self, personality: str = "friendly"):
        system_prompt = self.PERSONALITIES.get(personality, self.PERSONALITIES["friendly"])
        self.memory = ConversationMemory(system_prompt=system_prompt)
        self.personality = personality

    def set_personality(self, personality: str) -> None:
        """Change bot personality."""
        if personality in self.PERSONALITIES:
            self.personality = personality
            self.memory.system_prompt = self.PERSONALITIES[personality]
            print(f"Personality changed to: {personality}")
        else:
            print(f"Unknown personality. Available: {list(self.PERSONALITIES.keys())}")

    def chat(self, user_input: str) -> str:
        """Send message and get response."""
        self.memory.add_message("user", user_input)

        try:
            response = requests.post(
                API_URL,
                headers={
                    "Authorization": f"Bearer {API_KEY}",
                    "Content-Type": "application/json"
                },
                json={
                    "messages": self.memory.get_context_messages(),
                    "model": "gpt-4o",
                    "temperature": 0.7,
                    "max_tokens": 1500
                },
                timeout=60
            )
            response.raise_for_status()

            data = response.json()
            assistant_message = data["choices"][0]["message"]["content"]

            self.memory.add_message("assistant", assistant_message)

            return assistant_message

        except requests.exceptions.RequestException as e:
            return f"Error: {str(e)}"

    def get_stats(self) -> Dict:
        """Get conversation statistics."""
        return {
            "personality": self.personality,
            "message_count": len(self.memory.messages),
            "has_summary": self.memory.summary is not None,
            "summary_length": len(self.memory.summary) if self.memory.summary else 0
        }


# ============ Interactive Demo ============

def main():
    print("=" * 50)
    print("RoraOS Chatbot with Memory")
    print("=" * 50)
    print("\nAvailable personalities: friendly, professional, creative, teacher, coder")
    print("Commands: /personality [name], /stats, /clear, /export, /import, /quit\n")

    bot = Chatbot(personality="friendly")

    while True:
        try:
            user_input = input("You: ").strip()

            if not user_input:
                continue

            # Handle commands
            if user_input.startswith('/'):
                parts = user_input.split(maxsplit=1)
                cmd = parts[0].lower()
                arg = parts[1] if len(parts) > 1 else None

                if cmd == '/quit':
                    print("Goodbye!")
                    break
                elif cmd == '/clear':
                    bot.memory.clear()
                    print("Memory cleared!")
                elif cmd == '/stats':
                    stats = bot.get_stats()
                    print(f"Stats: {json.dumps(stats, indent=2)}")
                elif cmd == '/personality':
                    if arg:
                        bot.set_personality(arg)
                    else:
                        print(f"Current: {bot.personality}")
                        print(f"Available: {list(Chatbot.PERSONALITIES.keys())}")
                elif cmd == '/export':
                    filename = arg or "conversation.json"
                    bot.memory.export_conversation(filename)
                elif cmd == '/import':
                    filename = arg or "conversation.json"
                    try:
                        bot.memory.import_conversation(filename)
                    except FileNotFoundError:
                        print(f"File not found: {filename}")
                else:
                    print(f"Unknown command: {cmd}")
                continue

            # Chat
            response = bot.chat(user_input)
            print(f"Bot: {response}\n")

        except KeyboardInterrupt:
            print("\nGoodbye!")
            break


if __name__ == "__main__":
    main()
