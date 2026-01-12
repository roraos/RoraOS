"""
RoraOS Async Client - Python Example
======================================

Async/await client for RoraOS API using aiohttp.
Suitable for async applications like Discord.py, FastAPI, etc.

Installation:
    pip install aiohttp

Usage:
    python async_client.py

Features:
    - Fully async/await
    - Connection pooling
    - Retry logic
    - Streaming support
    - Context manager
"""

import asyncio
import aiohttp
import json
from typing import List, Dict, Optional, AsyncGenerator
from dataclasses import dataclass


@dataclass
class Message:
    role: str
    content: str


@dataclass
class ChatResponse:
    content: str
    model: str
    usage: Optional[Dict] = None


class RoraOSClient:
    """Async client for RoraOS API."""

    def __init__(
        self,
        api_key: str,
        base_url: str = "https://labs.roraos.com/api/v1",
        timeout: int = 120,
        max_retries: int = 3
    ):
        self.api_key = api_key
        self.base_url = base_url.rstrip("/")
        self.timeout = aiohttp.ClientTimeout(total=timeout)
        self.max_retries = max_retries
        self._session: Optional[aiohttp.ClientSession] = None

    async def _get_session(self) -> aiohttp.ClientSession:
        """Get or create aiohttp session."""
        if self._session is None or self._session.closed:
            self._session = aiohttp.ClientSession(
                timeout=self.timeout,
                headers={
                    "Authorization": f"Bearer {self.api_key}",
                    "Content-Type": "application/json"
                }
            )
        return self._session

    async def close(self):
        """Close the session."""
        if self._session and not self._session.closed:
            await self._session.close()

    async def __aenter__(self):
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        await self.close()

    async def chat(
        self,
        messages: List[Dict[str, str]],
        model: str = "gpt-4o",
        temperature: float = 0.7,
        max_tokens: int = 2000,
        stream: bool = False
    ) -> ChatResponse:
        """Send chat completion request."""

        if stream:
            # For streaming, collect all chunks
            content = ""
            async for chunk in self.chat_stream(messages, model, temperature, max_tokens):
                content += chunk
            return ChatResponse(content=content, model=model)

        session = await self._get_session()
        url = f"{self.base_url}/chat"

        payload = {
            "messages": messages,
            "model": model,
            "temperature": temperature,
            "max_tokens": max_tokens,
            "stream": False
        }

        for attempt in range(self.max_retries):
            try:
                async with session.post(url, json=payload) as response:
                    if response.status == 200:
                        data = await response.json()
                        return ChatResponse(
                            content=data["choices"][0]["message"]["content"],
                            model=data.get("model", model),
                            usage=data.get("usage")
                        )
                    elif response.status >= 500:
                        # Retry on server errors
                        if attempt < self.max_retries - 1:
                            await asyncio.sleep(2 ** attempt)
                            continue
                    error_data = await response.json()
                    raise Exception(error_data.get("error", f"HTTP {response.status}"))

            except aiohttp.ClientError as e:
                if attempt < self.max_retries - 1:
                    await asyncio.sleep(2 ** attempt)
                    continue
                raise Exception(f"Request failed: {e}")

        raise Exception("Max retries exceeded")

    async def chat_stream(
        self,
        messages: List[Dict[str, str]],
        model: str = "gpt-4o",
        temperature: float = 0.7,
        max_tokens: int = 2000
    ) -> AsyncGenerator[str, None]:
        """Stream chat completion response."""

        session = await self._get_session()
        url = f"{self.base_url}/chat"

        payload = {
            "messages": messages,
            "model": model,
            "temperature": temperature,
            "max_tokens": max_tokens,
            "stream": True
        }

        async with session.post(url, json=payload) as response:
            if response.status != 200:
                error_data = await response.json()
                raise Exception(error_data.get("error", f"HTTP {response.status}"))

            async for line in response.content:
                line = line.decode("utf-8").strip()
                if line.startswith("data: "):
                    data = line[6:]
                    if data == "[DONE]":
                        break
                    try:
                        parsed = json.loads(data)
                        content = (
                            parsed.get("content") or
                            parsed.get("choices", [{}])[0].get("delta", {}).get("content", "")
                        )
                        if content:
                            yield content
                    except json.JSONDecodeError:
                        pass


class ChatSession:
    """Chat session with history management."""

    def __init__(
        self,
        client: RoraOSClient,
        system_prompt: str = "You are a helpful assistant.",
        max_history: int = 20
    ):
        self.client = client
        self.system_prompt = system_prompt
        self.max_history = max_history
        self.messages: List[Dict[str, str]] = []

    async def send(self, content: str, **kwargs) -> str:
        """Send message and get response."""
        self.messages.append({"role": "user", "content": content})

        # Trim history
        if len(self.messages) > self.max_history:
            self.messages = self.messages[-self.max_history:]

        # Build full messages list
        full_messages = [
            {"role": "system", "content": self.system_prompt},
            *self.messages
        ]

        response = await self.client.chat(full_messages, **kwargs)

        self.messages.append({"role": "assistant", "content": response.content})

        return response.content

    async def stream(self, content: str, **kwargs) -> AsyncGenerator[str, None]:
        """Stream message response."""
        self.messages.append({"role": "user", "content": content})

        if len(self.messages) > self.max_history:
            self.messages = self.messages[-self.max_history:]

        full_messages = [
            {"role": "system", "content": self.system_prompt},
            *self.messages
        ]

        full_response = ""
        async for chunk in self.client.chat_stream(full_messages, **kwargs):
            full_response += chunk
            yield chunk

        self.messages.append({"role": "assistant", "content": full_response})

    def clear(self):
        """Clear conversation history."""
        self.messages = []


# =====================================================
# EXAMPLES
# =====================================================

async def example_basic():
    """Basic usage example."""
    print("=" * 50)
    print("Example 1: Basic Chat")
    print("=" * 50)

    async with RoraOSClient(api_key="your-api-key") as client:
        response = await client.chat([
            {"role": "user", "content": "Hello! How are you?"}
        ])
        print(f"Response: {response.content}")


async def example_streaming():
    """Streaming example."""
    print("\n" + "=" * 50)
    print("Example 2: Streaming")
    print("=" * 50)

    async with RoraOSClient(api_key="your-api-key") as client:
        print("Response: ", end="")
        async for chunk in client.chat_stream([
            {"role": "user", "content": "Tell me about artificial intelligence."}
        ]):
            print(chunk, end="", flush=True)
        print()


async def example_session():
    """Session with history example."""
    print("\n" + "=" * 50)
    print("Example 3: Chat Session")
    print("=" * 50)

    async with RoraOSClient(api_key="your-api-key") as client:
        session = ChatSession(
            client,
            system_prompt="You are a patient math teacher."
        )

        response1 = await session.send("What is a prime number?")
        print(f"User: What is a prime number?")
        print(f"AI: {response1[:200]}...")

        response2 = await session.send("Give me 3 examples.")
        print(f"\nUser: Give me 3 examples.")
        print(f"AI: {response2}")


async def example_concurrent():
    """Concurrent requests example."""
    print("\n" + "=" * 50)
    print("Example 4: Concurrent Requests")
    print("=" * 50)

    async with RoraOSClient(api_key="your-api-key") as client:
        # Send 3 requests concurrently
        tasks = [
            client.chat([{"role": "user", "content": "What is Python?"}]),
            client.chat([{"role": "user", "content": "What is JavaScript?"}]),
            client.chat([{"role": "user", "content": "What is Rust?"}]),
        ]

        responses = await asyncio.gather(*tasks)

        for i, resp in enumerate(responses, 1):
            print(f"Response {i}: {resp.content[:100]}...")


async def main():
    try:
        await example_basic()
        await example_streaming()
        await example_session()
        await example_concurrent()
    except Exception as e:
        print(f"\nError: {e}")
        print("Make sure API_KEY and BASE_URL are correct!")


if __name__ == "__main__":
    asyncio.run(main())
