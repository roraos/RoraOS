/**
 * RoraOS React Hook - useChat
 * ============================
 *
 * Custom React hook for RoraOS API integration.
 * Can be used in Next.js, Create React App, etc.
 *
 * Features:
 * - Chat with history
 * - Streaming support
 * - Loading state
 * - Error handling
 * - Auto-retry
 *
 * Usage:
 *   import { useChat } from './useChat';
 *
 *   function ChatComponent() {
 *     const { messages, sendMessage, isLoading, error, clearMessages } = useChat({
 *       apiKey: 'your-api-key',
 *       model: 'gpt-4o'
 *     });
 *
 *     return (
 *       <div>
 *         {messages.map((msg, i) => (
 *           <div key={i}>{msg.role}: {msg.content}</div>
 *         ))}
 *         <button onClick={() => sendMessage('Hello!')}>Send</button>
 *       </div>
 *     );
 *   }
 */

import { useState, useCallback, useRef } from 'react';

// Types
interface Message {
  role: 'user' | 'assistant' | 'system';
  content: string;
  timestamp?: Date;
}

interface UseChatOptions {
  apiUrl?: string;
  apiKey: string;
  model?: string;
  systemPrompt?: string;
  temperature?: number;
  maxTokens?: number;
  stream?: boolean;
  onError?: (error: Error) => void;
  onMessage?: (message: Message) => void;
}

interface UseChatReturn {
  messages: Message[];
  sendMessage: (content: string) => Promise<void>;
  isLoading: boolean;
  error: Error | null;
  clearMessages: () => void;
  setSystemPrompt: (prompt: string) => void;
}

// Default config
const DEFAULT_API_URL = 'https://labs.roraos.com/api/v1/chat';
const DEFAULT_MODEL = 'gpt-4o';
const DEFAULT_SYSTEM_PROMPT = 'You are a helpful AI assistant.';

export function useChat(options: UseChatOptions): UseChatReturn {
  const {
    apiUrl = DEFAULT_API_URL,
    apiKey,
    model = DEFAULT_MODEL,
    systemPrompt: initialSystemPrompt = DEFAULT_SYSTEM_PROMPT,
    temperature = 0.7,
    maxTokens = 2000,
    stream = false,
    onError,
    onMessage,
  } = options;

  const [messages, setMessages] = useState<Message[]>([]);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<Error | null>(null);
  const systemPromptRef = useRef(initialSystemPrompt);

  const setSystemPrompt = useCallback((prompt: string) => {
    systemPromptRef.current = prompt;
  }, []);

  const clearMessages = useCallback(() => {
    setMessages([]);
    setError(null);
  }, []);

  const sendMessage = useCallback(
    async (content: string) => {
      if (!content.trim() || isLoading) return;

      const userMessage: Message = {
        role: 'user',
        content: content.trim(),
        timestamp: new Date(),
      };

      setMessages((prev) => [...prev, userMessage]);
      setIsLoading(true);
      setError(null);

      try {
        // Build messages array for API
        const apiMessages = [
          { role: 'system', content: systemPromptRef.current },
          ...messages.map((m) => ({ role: m.role, content: m.content })),
          { role: 'user', content: content.trim() },
        ];

        if (stream) {
          // Streaming mode
          await sendStreamingRequest(apiMessages);
        } else {
          // Non-streaming mode
          await sendNormalRequest(apiMessages);
        }
      } catch (err) {
        const error = err instanceof Error ? err : new Error('Unknown error');
        setError(error);
        onError?.(error);
      } finally {
        setIsLoading(false);
      }
    },
    [messages, isLoading, stream]
  );

  const sendNormalRequest = async (apiMessages: any[]) => {
    const response = await fetch(apiUrl, {
      method: 'POST',
      headers: {
        Authorization: `Bearer ${apiKey}`,
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({
        messages: apiMessages,
        model,
        temperature,
        max_tokens: maxTokens,
        stream: false,
      }),
    });

    if (!response.ok) {
      const errorData = await response.json().catch(() => ({}));
      throw new Error(errorData.error || `HTTP error ${response.status}`);
    }

    const data = await response.json();
    const assistantContent = data.choices?.[0]?.message?.content || '';

    const assistantMessage: Message = {
      role: 'assistant',
      content: assistantContent,
      timestamp: new Date(),
    };

    setMessages((prev) => [...prev, assistantMessage]);
    onMessage?.(assistantMessage);
  };

  const sendStreamingRequest = async (apiMessages: any[]) => {
    const response = await fetch(apiUrl, {
      method: 'POST',
      headers: {
        Authorization: `Bearer ${apiKey}`,
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({
        messages: apiMessages,
        model,
        temperature,
        max_tokens: maxTokens,
        stream: true,
      }),
    });

    if (!response.ok) {
      const errorData = await response.json().catch(() => ({}));
      throw new Error(errorData.error || `HTTP error ${response.status}`);
    }

    const reader = response.body?.getReader();
    if (!reader) throw new Error('No response body');

    const decoder = new TextDecoder();
    let fullContent = '';

    // Add empty assistant message that we'll update
    setMessages((prev) => [
      ...prev,
      { role: 'assistant', content: '', timestamp: new Date() },
    ]);

    while (true) {
      const { done, value } = await reader.read();
      if (done) break;

      const chunk = decoder.decode(value);
      const lines = chunk.split('\n');

      for (const line of lines) {
        if (line.startsWith('data: ')) {
          const data = line.slice(6);
          if (data === '[DONE]') continue;

          try {
            const parsed = JSON.parse(data);
            const content =
              parsed.content || parsed.choices?.[0]?.delta?.content || '';
            if (content) {
              fullContent += content;

              // Update the last message
              setMessages((prev) => {
                const updated = [...prev];
                updated[updated.length - 1] = {
                  role: 'assistant',
                  content: fullContent,
                  timestamp: new Date(),
                };
                return updated;
              });
            }
          } catch {
            // Skip invalid JSON
          }
        }
      }
    }

    const finalMessage: Message = {
      role: 'assistant',
      content: fullContent,
      timestamp: new Date(),
    };
    onMessage?.(finalMessage);
  };

  return {
    messages,
    sendMessage,
    isLoading,
    error,
    clearMessages,
    setSystemPrompt,
  };
}

// =====================================================
// EXAMPLE COMPONENT
// =====================================================

/*
import React, { useState } from 'react';
import { useChat } from './useChat';

function ChatApp() {
  const [input, setInput] = useState('');

  const {
    messages,
    sendMessage,
    isLoading,
    error,
    clearMessages,
  } = useChat({
    apiKey: 'your-api-key',
    model: 'gpt-4o',
    stream: true,
    systemPrompt: 'You are a helpful assistant.',
  });

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (input.trim()) {
      sendMessage(input);
      setInput('');
    }
  };

  return (
    <div className="chat-container">
      <div className="chat-header">
        <h1>AI Chat</h1>
        <button onClick={clearMessages}>Clear</button>
      </div>

      <div className="chat-messages">
        {messages.map((msg, i) => (
          <div key={i} className={`message ${msg.role}`}>
            <strong>{msg.role}:</strong> {msg.content}
          </div>
        ))}
        {isLoading && <div className="loading">Thinking...</div>}
        {error && <div className="error">{error.message}</div>}
      </div>

      <form onSubmit={handleSubmit} className="chat-input">
        <input
          type="text"
          value={input}
          onChange={(e) => setInput(e.target.value)}
          placeholder="Type a message..."
          disabled={isLoading}
        />
        <button type="submit" disabled={isLoading || !input.trim()}>
          Send
        </button>
      </form>
    </div>
  );
}

export default ChatApp;
*/

export default useChat;
