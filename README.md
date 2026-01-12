<div align="center">

# RoraOS API

### One API. All Models. Unlimited Possibilities.

[![API Status](https://img.shields.io/badge/API-Online-brightgreen?style=for-the-badge)](https://labs.roraos.com)
[![OpenAI Compatible](https://img.shields.io/badge/OpenAI-Compatible-blue?style=for-the-badge&logo=openai)](https://labs.roraos.com)
[![License](https://img.shields.io/badge/License-MIT-yellow?style=for-the-badge)](LICENSE)

**Access GPT-4, Claude, Gemini, Llama, and 50+ AI models through a single, unified API.**

[Get Started](#quick-start) · [API Docs](#api-reference) · [Examples](#code-examples) · [Support](mailto:support@roraos.com)

---

</div>

## Why RoraOS?

| Feature | Benefit |
|---------|---------|
| **Unified API** | One API key, one endpoint, all models |
| **OpenAI Compatible** | Drop-in replacement - use existing OpenAI SDK |
| **Multi-Model Access** | GPT-4o, Claude 3.5, Gemini 2.0, Llama 3.2, and more |
| **Streaming Support** | Real-time responses with Server-Sent Events |
| **Custom Agents** | Create specialized AI agents with persistent context |
| **Enterprise Ready** | High availability, rate limiting, usage analytics |

---

## Quick Start

Get up and running in **under 30 seconds**.

### Python

```python
import requests

response = requests.post(
    "https://labs.roraos.com/api/v1/chat",
    headers={
        "Authorization": "Bearer YOUR_API_KEY",
        "Content-Type": "application/json"
    },
    json={
        "messages": [{"role": "user", "content": "Hello!"}],
        "model": "gpt-4o"
    }
)

print(response.json()["choices"][0]["message"]["content"])
```

### JavaScript

```javascript
const response = await fetch("https://labs.roraos.com/api/v1/chat", {
  method: "POST",
  headers: {
    "Authorization": "Bearer YOUR_API_KEY",
    "Content-Type": "application/json"
  },
  body: JSON.stringify({
    messages: [{ role: "user", content: "Hello!" }],
    model: "gpt-4o"
  })
});

const data = await response.json();
console.log(data.choices[0].message.content);
```

### Using OpenAI SDK (Zero Code Changes!)

```python
from openai import OpenAI

client = OpenAI(
    api_key="YOUR_API_KEY",
    base_url="https://labs.roraos.com/api/v1"  # Just change this!
)

response = client.chat.completions.create(
    model="gpt-4o",
    messages=[{"role": "user", "content": "Hello!"}]
)
```

---

## API Reference

### Authentication

```http
Authorization: Bearer YOUR_API_KEY
```

### Endpoints

| Endpoint | Description |
|----------|-------------|
| `POST /api/v1/chat` | General chat completion |
| `POST /api/v1/agents/chat` | Chat with custom agent |

### Request Parameters

| Parameter | Type | Required | Default | Description |
|-----------|------|:--------:|---------|-------------|
| `messages` | array | ✅ | - | Array of chat messages |
| `model` | string | - | `gpt-4o` | Model to use |
| `stream` | boolean | - | `false` | Enable streaming |
| `temperature` | number | - | `0.7` | Creativity (0-2) |
| `max_tokens` | number | - | `4096` | Max response tokens |

### Response Format

```json
{
  "id": "chatcmpl-xxx",
  "object": "chat.completion",
  "model": "gpt-4o",
  "choices": [{
    "index": 0,
    "message": { "role": "assistant", "content": "..." },
    "finish_reason": "stop"
  }],
  "usage": { "prompt_tokens": 10, "completion_tokens": 50 }
}
```

---

## Available Models

<table>
<tr>
<td width="25%" valign="top">

### OpenAI
- gpt-4o
- gpt-4-turbo
- gpt-4
- o1-preview
- o1-mini

</td>
<td width="25%" valign="top">

### Anthropic
- claude-3.5-sonnet
- claude-3-opus
- claude-3-haiku

</td>
<td width="25%" valign="top">

### Google
- gemini-2.0-flash
- gemini-1.5-pro
- gemini-1.5-flash

</td>
<td width="25%" valign="top">

### Others
- llama-3.2-90b
- mistral-large-2
- grok-2
- deepseek-v3

</td>
</tr>
</table>

---

## Code Examples

### Basic Examples

| File | Description |
|------|-------------|
| [basic/regular_api.py](basic/regular_api.py) | Python - Regular API with streaming |
| [basic/regular_api.js](basic/regular_api.js) | JavaScript - Regular API with streaming |
| [basic/agent_api.py](basic/agent_api.py) | Python - Custom Agent API |
| [basic/agent_api.js](basic/agent_api.js) | JavaScript - Custom Agent API |

### OpenAI SDK Compatible

| File | Description |
|------|-------------|
| [openai-sdk/openai_compatible.py](openai-sdk/openai_compatible.py) | Python - OpenAI SDK integration |
| [openai-sdk/openai_compatible.js](openai-sdk/openai_compatible.js) | Node.js - OpenAI SDK integration |

### Advanced Examples

| File | Description |
|------|-------------|
| [advanced/async_client.py](advanced/async_client.py) | Async/await client with aiohttp |
| [advanced/chatbot_memory.py](advanced/chatbot_memory.py) | Chatbot with conversation memory & personalities |
| [advanced/cli_chat.py](advanced/cli_chat.py) | Interactive CLI chat with rich formatting |
| [advanced/langchain_integration.py](advanced/langchain_integration.py) | LangChain integration examples |

---

## Bot Examples

Build AI-powered bots for any platform in minutes.

| Platform | File | Features |
|----------|------|----------|
| **Telegram** | [telegram_bot.py](bots/telegram/telegram_bot.py) | Multi-turn chat, commands, typing indicator |
| **Discord** | [discord_bot.py](bots/discord/discord_bot.py) | Slash commands, mentions, history per channel |
| **Slack** | [slack_bot.py](bots/slack/slack_bot.py) | Socket Mode, @mentions, /ai command |
| **WhatsApp** | [whatsapp_bot.py](bots/whatsapp/whatsapp_bot.py) | Green API integration, conversation memory |
| **LINE** | [line_bot.py](bots/line/line_bot.py) | Webhook handler, multi-turn conversations |

### Quick Setup

```bash
# Telegram
pip install python-telegram-bot requests
export TELEGRAM_BOT_TOKEN="your-token"
export RORAOS_API_KEY="your-api-key"
python bots/telegram/telegram_bot.py

# Discord
pip install discord.py requests
export DISCORD_BOT_TOKEN="your-token"
export RORAOS_API_KEY="your-api-key"
python bots/discord/discord_bot.py
```

---

## Framework Integration

### Backend Servers

| Framework | File | Features |
|-----------|------|----------|
| **FastAPI** | [fastapi_server.py](servers/fastapi_server.py) | Streaming, CORS, custom endpoints |
| **Express.js** | [express_server.js](servers/express_server.js) | REST API, utilities, SSE streaming |

### Frontend Integration

| Framework | File | Features |
|-----------|------|----------|
| **React** | [react_useChat.tsx](frontend/react_useChat.tsx) | Custom hook with TypeScript, streaming |
| **Vanilla JS** | [web_chat_widget.html](frontend/web_chat_widget.html) | Embeddable widget, localStorage |

### Running Servers

```bash
# FastAPI
pip install fastapi uvicorn requests
uvicorn servers.fastapi_server:app --reload --port 8000

# Express.js
npm install express cors axios
node servers/express_server.js
```

---

## Pricing

| Plan | Requests/Day | Best For |
|------|:------------:|----------|
| **Free** | 20 | Testing & Development |
| **Starter** | 2,000 | Side Projects |
| **Pro** | 25,000 | Production Apps |
| **Enterprise** | Unlimited | Scale Without Limits |

---

## Project Structure

```
roraOS/
├── basic/                  # Getting started examples
├── openai-sdk/             # OpenAI SDK compatibility
├── advanced/               # Production-ready patterns
├── bots/                   # Messaging platform bots
│   ├── telegram/
│   ├── discord/
│   ├── slack/
│   ├── whatsapp/
│   └── line/
├── servers/                # Backend API servers
└── frontend/               # Frontend integration
```

---

## Error Handling

| Status | Description |
|:------:|-------------|
| `200` | Success |
| `400` | Bad Request - Check your request body |
| `401` | Unauthorized - Invalid API key |
| `429` | Rate limit exceeded - Upgrade your plan |
| `500` | Server error - Try again later |

```json
{
  "error": "Error message description"
}
```

---

<div align="center">

## Get Started Today

[Create Free Account](https://labs.roraos.com) · [Read Documentation](https://docs.roraos.com) · [Contact Sales](mailto:sales@roraos.com)

---

**Built with passion by the RoraOS Team**

[Website](https://roraos.com) · [Twitter](https://twitter.com/roraos) · [GitHub](https://github.com/roraos)

</div>
