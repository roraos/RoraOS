"""
RoraOS FastAPI Integration - Python Example
=============================================

Example of integrating RoraOS API with FastAPI to create
your own backend/proxy API.

Installation:
    pip install fastapi uvicorn requests

Run:
    uvicorn fastapi_server:app --reload --port 8000

Endpoints:
    POST /chat - Chat completion
    POST /chat/stream - Streaming chat
    GET /models - List available models
    GET /health - Health check
"""

from fastapi import FastAPI, HTTPException, Header
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
from typing import List, Optional
import requests
import json

# Configuration
RORAOS_API_URL = "https://labs.roraos.com/api/v1/chat"
RORAOS_API_KEY = "your-api-key-here"

# FastAPI app
app = FastAPI(
    title="RoraOS Proxy API",
    description="Proxy API for RoraOS Chat",
    version="1.0.0"
)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Models
class Message(BaseModel):
    role: str
    content: str


class ChatRequest(BaseModel):
    messages: List[Message]
    model: Optional[str] = "gpt-4o"
    temperature: Optional[float] = 0.7
    max_tokens: Optional[int] = 2000
    stream: Optional[bool] = False


class ChatResponse(BaseModel):
    content: str
    model: str
    usage: Optional[dict] = None


# Available models (for display)
AVAILABLE_MODELS = [
    {"id": "gpt-4o", "name": "GPT-4o", "provider": "OpenAI"},
    {"id": "gpt-4-turbo", "name": "GPT-4 Turbo", "provider": "OpenAI"},
    {"id": "claude-3.5-sonnet", "name": "Claude 3.5 Sonnet", "provider": "Anthropic"},
    {"id": "gemini-2.0-flash", "name": "Gemini 2.0 Flash", "provider": "Google"},
]


@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {"status": "healthy", "service": "roraos-proxy"}


@app.get("/models")
async def list_models():
    """List available models."""
    return {"models": AVAILABLE_MODELS}


@app.post("/chat", response_model=ChatResponse)
async def chat(request: ChatRequest, x_api_key: Optional[str] = Header(None)):
    """
    Chat completion endpoint.

    Optionally accepts X-API-Key header to use custom API key.
    """
    api_key = x_api_key or RORAOS_API_KEY

    try:
        response = requests.post(
            RORAOS_API_URL,
            headers={
                "Authorization": f"Bearer {api_key}",
                "Content-Type": "application/json"
            },
            json={
                "messages": [m.model_dump() for m in request.messages],
                "model": request.model,
                "temperature": request.temperature,
                "max_tokens": request.max_tokens,
                "stream": False
            },
            timeout=120
        )

        if not response.ok:
            error_data = response.json()
            raise HTTPException(
                status_code=response.status_code,
                detail=error_data.get("error", "API request failed")
            )

        data = response.json()

        return ChatResponse(
            content=data["choices"][0]["message"]["content"],
            model=data.get("model", request.model),
            usage=data.get("usage")
        )

    except requests.exceptions.Timeout:
        raise HTTPException(status_code=504, detail="Request timeout")
    except requests.exceptions.RequestException as e:
        raise HTTPException(status_code=502, detail=str(e))


@app.post("/chat/stream")
async def chat_stream(request: ChatRequest, x_api_key: Optional[str] = Header(None)):
    """
    Streaming chat completion endpoint.
    Returns Server-Sent Events.
    """
    api_key = x_api_key or RORAOS_API_KEY

    def generate():
        try:
            response = requests.post(
                RORAOS_API_URL,
                headers={
                    "Authorization": f"Bearer {api_key}",
                    "Content-Type": "application/json"
                },
                json={
                    "messages": [m.model_dump() for m in request.messages],
                    "model": request.model,
                    "temperature": request.temperature,
                    "max_tokens": request.max_tokens,
                    "stream": True
                },
                stream=True,
                timeout=120
            )

            if not response.ok:
                yield f"data: {json.dumps({'error': 'API request failed'})}\n\n"
                return

            for line in response.iter_lines():
                if line:
                    yield line.decode('utf-8') + "\n"

        except Exception as e:
            yield f"data: {json.dumps({'error': str(e)})}\n\n"

    return StreamingResponse(
        generate(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive"
        }
    )


# Custom endpoint examples
@app.post("/summarize")
async def summarize(text: str, x_api_key: Optional[str] = Header(None)):
    """Summarize text using AI."""
    request = ChatRequest(
        messages=[
            Message(role="system", content="Summarize the following text concisely."),
            Message(role="user", content=text)
        ],
        temperature=0.3,
        max_tokens=500
    )
    return await chat(request, x_api_key)


@app.post("/translate")
async def translate(text: str, target_language: str = "English", x_api_key: Optional[str] = Header(None)):
    """Translate text to target language."""
    request = ChatRequest(
        messages=[
            Message(role="system", content=f"Translate the following text to {target_language}. Only output the translation."),
            Message(role="user", content=text)
        ],
        temperature=0.3,
        max_tokens=1000
    )
    return await chat(request, x_api_key)


@app.post("/code/explain")
async def explain_code(code: str, x_api_key: Optional[str] = Header(None)):
    """Explain code."""
    request = ChatRequest(
        messages=[
            Message(role="system", content="Explain the following code clearly and concisely."),
            Message(role="user", content=f"```\n{code}\n```")
        ],
        temperature=0.3,
        max_tokens=1000
    )
    return await chat(request, x_api_key)


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
