"""
RoraOS CLI Chat - Python Example
=================================

Command-line chat interface using RoraOS API.
Interactive terminal application for chatting with AI.

Installation:
    pip install requests rich

Usage:
    python cli_chat.py

Features:
    - Interactive chat in terminal
    - Syntax highlighting for code
    - Conversation history
    - Commands: /clear, /save, /load, /exit
"""

import os
import sys
import json
import requests
from datetime import datetime

# Try to import rich for better display
try:
    from rich.console import Console
    from rich.markdown import Markdown
    from rich.panel import Panel
    from rich.prompt import Prompt
    RICH_AVAILABLE = True
except ImportError:
    RICH_AVAILABLE = False
    print("Tip: Install 'rich' for better display: pip install rich")

# Configuration
API_URL = "https://labs.roraos.com/api/v1/chat"
API_KEY = os.getenv("RORAOS_API_KEY", "your-api-key-here")
HISTORY_FILE = "chat_history.json"

# Console for rich output
console = Console() if RICH_AVAILABLE else None


class ChatCLI:
    def __init__(self):
        self.messages = [
            {"role": "system", "content": "You are a helpful AI assistant. Format responses with markdown when appropriate."}
        ]
        self.model = "gpt-4o"

    def send_message(self, user_input: str) -> str:
        """Send message to API and get response."""
        self.messages.append({"role": "user", "content": user_input})

        # Limit history
        if len(self.messages) > 41:
            self.messages = [self.messages[0]] + self.messages[-40:]

        try:
            response = requests.post(
                API_URL,
                headers={
                    "Authorization": f"Bearer {API_KEY}",
                    "Content-Type": "application/json"
                },
                json={
                    "messages": self.messages,
                    "model": self.model,
                    "temperature": 0.7,
                    "max_tokens": 2000
                },
                timeout=120
            )
            response.raise_for_status()

            data = response.json()
            assistant_message = data["choices"][0]["message"]["content"]

            self.messages.append({"role": "assistant", "content": assistant_message})

            return assistant_message

        except requests.exceptions.Timeout:
            return "Request timeout. Please try again."
        except requests.exceptions.RequestException as e:
            return f"Error: {str(e)}"

    def clear_history(self):
        """Clear conversation history."""
        self.messages = [self.messages[0]]
        return "Conversation history cleared."

    def save_history(self, filename: str = None):
        """Save history to file."""
        filename = filename or HISTORY_FILE
        try:
            with open(filename, 'w', encoding='utf-8') as f:
                json.dump({
                    "saved_at": datetime.now().isoformat(),
                    "messages": self.messages
                }, f, ensure_ascii=False, indent=2)
            return f"History saved to {filename}"
        except Exception as e:
            return f"Failed to save: {e}"

    def load_history(self, filename: str = None):
        """Load history from file."""
        filename = filename or HISTORY_FILE
        try:
            with open(filename, 'r', encoding='utf-8') as f:
                data = json.load(f)
            self.messages = data["messages"]
            return f"History loaded from {filename} ({len(self.messages)} messages)"
        except FileNotFoundError:
            return f"File {filename} not found"
        except Exception as e:
            return f"Failed to load: {e}"

    def print_response(self, text: str):
        """Print response with formatting."""
        if RICH_AVAILABLE:
            console.print(Panel(Markdown(text), title="AI", border_style="blue"))
        else:
            print(f"\nAI:\n{text}\n")

    def print_system(self, text: str):
        """Print system message."""
        if RICH_AVAILABLE:
            console.print(f"[dim]{text}[/dim]")
        else:
            print(text)

    def show_help(self):
        """Show help."""
        help_text = """
Commands:
  /clear          - Clear conversation history
  /save [file]    - Save history to file
  /load [file]    - Load history from file
  /model [name]   - Change model (display only)
  /history        - Show message count
  /help           - Show this help
  /exit, /quit    - Exit application

Tips:
  - Press Ctrl+C to cancel
  - Use /clear to start a new topic
"""
        if RICH_AVAILABLE:
            console.print(Panel(help_text, title="Help", border_style="green"))
        else:
            print(help_text)

    def run(self):
        """Main loop for chat CLI."""
        if RICH_AVAILABLE:
            console.print(Panel.fit(
                "[bold blue]RoraOS CLI Chat[/bold blue]\n"
                "Type /help to see commands\n"
                "Type /exit to quit",
                border_style="blue"
            ))
        else:
            print("\n" + "="*50)
            print("RoraOS CLI Chat")
            print("Type /help to see commands")
            print("Type /exit to quit")
            print("="*50 + "\n")

        while True:
            try:
                # Get user input
                if RICH_AVAILABLE:
                    user_input = Prompt.ask("\n[bold green]You[/bold green]")
                else:
                    user_input = input("\nYou: ").strip()

                if not user_input:
                    continue

                # Handle commands
                if user_input.startswith('/'):
                    parts = user_input.split(maxsplit=1)
                    cmd = parts[0].lower()
                    arg = parts[1] if len(parts) > 1 else None

                    if cmd in ['/exit', '/quit']:
                        self.print_system("Goodbye!")
                        break
                    elif cmd == '/clear':
                        self.print_system(self.clear_history())
                    elif cmd == '/save':
                        self.print_system(self.save_history(arg))
                    elif cmd == '/load':
                        self.print_system(self.load_history(arg))
                    elif cmd == '/model':
                        if arg:
                            self.model = arg
                            self.print_system(f"Model changed to: {arg}")
                        else:
                            self.print_system(f"Current model: {self.model}")
                    elif cmd == '/history':
                        self.print_system(f"{len(self.messages)} messages in history")
                    elif cmd == '/help':
                        self.show_help()
                    else:
                        self.print_system(f"Unknown command: {cmd}")
                    continue

                # Send message to AI
                if RICH_AVAILABLE:
                    with console.status("[bold blue]Thinking...[/bold blue]"):
                        response = self.send_message(user_input)
                else:
                    print("Thinking...")
                    response = self.send_message(user_input)

                self.print_response(response)

            except KeyboardInterrupt:
                print("\n")
                self.print_system("(Cancelled)")
                continue
            except EOFError:
                break

        print()


if __name__ == "__main__":
    chat = ChatCLI()
    chat.run()
