"""
RoraOS Agent Chat API - Python Example
=======================================

Example of using the Agent Chat API.
Each agent has a unique API key and pre-configured system prompt.

Installation:
    pip install requests

Usage:
    python agent_api.py
"""

import requests
import json

# Configuration
API_URL = "https://labs.roraos.com/api/v1/agents/chat"
AGENT_API_KEY = "agent_xxxxxxxxxxxxx"  # Agent-specific API key (get from agent page)


def agent_chat(messages: list, stream: bool = False, temperature: float = None, max_tokens: int = None):
    """
    Send chat request to Agent API.

    The agent already has a system prompt, knowledge base, and its own configuration.

    Args:
        messages: List of messages with format [{"role": "user", "content": "Hello"}]
        stream: Use streaming response
        temperature: Override agent temperature (optional)
        max_tokens: Override agent max_tokens (optional)

    Returns:
        Response from API
    """
    headers = {
        "Authorization": f"Bearer {AGENT_API_KEY}",
        "Content-Type": "application/json"
    }

    payload = {
        "messages": messages,
        "stream": stream
    }

    # Optional overrides
    if temperature is not None:
        payload["temperature"] = temperature
    if max_tokens is not None:
        payload["max_tokens"] = max_tokens

    if stream:
        return agent_chat_stream(headers, payload)

    response = requests.post(API_URL, headers=headers, json=payload)
    response.raise_for_status()
    return response.json()


def agent_chat_stream(headers: dict, payload: dict):
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
                    content = chunk.get('content', '')
                    if content:
                        full_content += content
                        print(content, end='', flush=True)
                except json.JSONDecodeError:
                    pass

    print()  # New line after streaming
    return full_content


# ============ Usage Examples ============

if __name__ == "__main__":
    # Example 1: Chat with agent
    print("=" * 50)
    print("Example 1: Chat with Agent")
    print("=" * 50)

    messages = [
        {"role": "user", "content": "Hello! What can you help me with?"}
    ]

    try:
        result = agent_chat(messages)
        print(f"Agent: {result['agent']['name']}")
        print(f"Response: {result['choices'][0]['message']['content']}")
    except requests.exceptions.RequestException as e:
        print(f"Error: {e}")

    # Example 2: Multi-turn conversation
    print("\n" + "=" * 50)
    print("Example 2: Multi-turn Conversation")
    print("=" * 50)

    conversation = []

    # Turn 1
    conversation.append({"role": "user", "content": "I want to learn programming"})

    try:
        result = agent_chat(conversation)
        assistant_response = result['choices'][0]['message']['content']
        print(f"User: {conversation[-1]['content']}")
        print(f"Agent: {assistant_response}")

        # Save response for context
        conversation.append({"role": "assistant", "content": assistant_response})

        # Turn 2
        conversation.append({"role": "user", "content": "Where should I start?"})

        result = agent_chat(conversation)
        print(f"\nUser: {conversation[-1]['content']}")
        print(f"Agent: {result['choices'][0]['message']['content']}")

    except requests.exceptions.RequestException as e:
        print(f"Error: {e}")

    # Example 3: Streaming with override settings
    print("\n" + "=" * 50)
    print("Example 3: Streaming with Custom Settings")
    print("=" * 50)

    messages = [
        {"role": "user", "content": "Give me productivity tips."}
    ]

    try:
        print("Response: ", end='')
        agent_chat(messages, stream=True, temperature=0.8, max_tokens=500)
    except requests.exceptions.RequestException as e:
        print(f"Error: {e}")
