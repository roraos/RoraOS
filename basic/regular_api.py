"""
RoraOS Regular Chat API - Python Example
=========================================

Example of using the Regular Chat API for chat completion.
This API is compatible with OpenAI format.

Installation:
    pip install requests

Usage:
    python regular_api.py
"""

import requests
import json

# Configuration
API_URL = "https://labs.roraos.com/api/v1/chat"
API_KEY = "your-api-key-here"  # Get from dashboard


def chat_completion(messages: list, stream: bool = False, temperature: float = 0.7, max_tokens: int = 2000):
    """
    Send chat completion request to API.

    Args:
        messages: List of messages with format [{"role": "user", "content": "Hello"}]
        stream: Use streaming response
        temperature: Creativity (0.0 - 2.0)
        max_tokens: Maximum response tokens

    Returns:
        Response from API
    """
    headers = {
        "Authorization": f"Bearer {API_KEY}",
        "Content-Type": "application/json"
    }

    payload = {
        "messages": messages,
        "model": "gpt-4o",  # Model displayed, backend uses available model
        "stream": stream,
        "temperature": temperature,
        "max_tokens": max_tokens
    }

    if stream:
        return chat_completion_stream(headers, payload)

    response = requests.post(API_URL, headers=headers, json=payload)
    response.raise_for_status()
    return response.json()


def chat_completion_stream(headers: dict, payload: dict):
    """Handle streaming response."""
    response = requests.post(
        API_URL,
        headers=headers,
        json=payload,
        stream=True
    )
    response.raise_for_status()

    full_content = ""
    for line in response.iter_lines():
        if line:
            line = line.decode('utf-8')
            if line.startswith('data: '):
                data = line[6:]
                if data == '[DONE]':
                    break
                try:
                    chunk = json.loads(data)
                    content = chunk.get('choices', [{}])[0].get('delta', {}).get('content', '')
                    if content:
                        full_content += content
                        print(content, end='', flush=True)
                except json.JSONDecodeError:
                    pass

    print()  # New line after streaming
    return full_content


# ============ Usage Examples ============

if __name__ == "__main__":
    # Example 1: Simple chat
    print("=" * 50)
    print("Example 1: Simple Chat")
    print("=" * 50)

    messages = [
        {"role": "user", "content": "Hello! Who are you?"}
    ]

    try:
        result = chat_completion(messages)
        print(f"Response: {result['choices'][0]['message']['content']}")
    except requests.exceptions.RequestException as e:
        print(f"Error: {e}")

    # Example 2: Chat with context (multi-turn)
    print("\n" + "=" * 50)
    print("Example 2: Multi-turn Chat")
    print("=" * 50)

    messages = [
        {"role": "system", "content": "You are a helpful assistant."},
        {"role": "user", "content": "What is Python?"},
        {"role": "assistant", "content": "Python is a popular high-level programming language."},
        {"role": "user", "content": "Give me a simple code example."}
    ]

    try:
        result = chat_completion(messages, temperature=0.5)
        print(f"Response: {result['choices'][0]['message']['content']}")
    except requests.exceptions.RequestException as e:
        print(f"Error: {e}")

    # Example 3: Streaming response
    print("\n" + "=" * 50)
    print("Example 3: Streaming Response")
    print("=" * 50)

    messages = [
        {"role": "user", "content": "Explain AI in 3 sentences."}
    ]

    try:
        print("Response: ", end='')
        chat_completion(messages, stream=True)
    except requests.exceptions.RequestException as e:
        print(f"Error: {e}")
