"""
RoraOS with OpenAI SDK - Python Example
==========================================

Example of using RoraOS API with OpenAI Python SDK.
Since RoraOS is compatible with OpenAI format, we can
use the official openai library.

Installation:
    pip install openai

Usage:
    python openai_compatible.py

Benefits:
    - Familiar syntax for OpenAI developers
    - All openai SDK features available
    - Easy migration from OpenAI to RoraOS
"""

from openai import OpenAI

# Configuration - use RoraOS as backend
client = OpenAI(
    api_key="your-api-key-here",  # RoraOS API key
    base_url="https://labs.roraos.com/api/v1"  # RoraOS Base URL
)


def chat_completion_basic():
    """Basic chat completion example."""
    print("=" * 50)
    print("Example 1: Basic Chat Completion")
    print("=" * 50)

    response = client.chat.completions.create(
        model="gpt-4o",  # Model display name
        messages=[
            {"role": "system", "content": "You are a helpful assistant."},
            {"role": "user", "content": "Hello! How are you?"}
        ],
        temperature=0.7,
        max_tokens=500
    )

    print(f"Response: {response.choices[0].message.content}")
    print(f"Model: {response.model}")
    print(f"Usage: {response.usage}")


def chat_completion_streaming():
    """Streaming chat completion example."""
    print("\n" + "=" * 50)
    print("Example 2: Streaming Chat Completion")
    print("=" * 50)

    stream = client.chat.completions.create(
        model="gpt-4o",
        messages=[
            {"role": "user", "content": "Tell me about artificial intelligence in 3 sentences."}
        ],
        stream=True
    )

    print("Response: ", end="")
    for chunk in stream:
        content = chunk.choices[0].delta.content
        if content:
            print(content, end="", flush=True)
    print()


def multi_turn_conversation():
    """Multi-turn conversation example."""
    print("\n" + "=" * 50)
    print("Example 3: Multi-turn Conversation")
    print("=" * 50)

    messages = [
        {"role": "system", "content": "You are a patient math teacher."}
    ]

    # Turn 1
    messages.append({"role": "user", "content": "What is a prime number?"})

    response = client.chat.completions.create(
        model="gpt-4o",
        messages=messages
    )

    assistant_response = response.choices[0].message.content
    messages.append({"role": "assistant", "content": assistant_response})

    print(f"User: {messages[-2]['content']}")
    print(f"AI: {assistant_response[:200]}...")

    # Turn 2
    messages.append({"role": "user", "content": "Give me 5 examples."})

    response = client.chat.completions.create(
        model="gpt-4o",
        messages=messages
    )

    print(f"\nUser: {messages[-1]['content']}")
    print(f"AI: {response.choices[0].message.content}")


def creative_writing():
    """Creative writing example with high temperature."""
    print("\n" + "=" * 50)
    print("Example 4: Creative Writing")
    print("=" * 50)

    response = client.chat.completions.create(
        model="gpt-4o",
        messages=[
            {"role": "system", "content": "You are a creative and imaginative writer."},
            {"role": "user", "content": "Write a short poem about sunrise."}
        ],
        temperature=1.2,  # More creative
        max_tokens=300
    )

    print(response.choices[0].message.content)


def code_generation():
    """Code generation example."""
    print("\n" + "=" * 50)
    print("Example 5: Code Generation")
    print("=" * 50)

    response = client.chat.completions.create(
        model="gpt-4o",
        messages=[
            {"role": "system", "content": "You are an expert programmer. Provide clean, well-documented code."},
            {"role": "user", "content": "Create a Python function to check for palindrome."}
        ],
        temperature=0.3,  # More focused for code
        max_tokens=500
    )

    print(response.choices[0].message.content)


if __name__ == "__main__":
    try:
        chat_completion_basic()
        chat_completion_streaming()
        multi_turn_conversation()
        creative_writing()
        code_generation()
    except Exception as e:
        print(f"Error: {e}")
        print("\nMake sure API_KEY and BASE_URL are correct!")
