/**
 * RoraOS Express.js Server - Node.js Example
 * ============================================
 *
 * Simple Express.js proxy server for RoraOS API.
 *
 * Installation:
 *   npm install express cors axios
 *
 * Run:
 *   node express_server.js
 *
 * Endpoints:
 *   POST /api/chat - Chat completion
 *   POST /api/chat/stream - Streaming chat
 *   GET /api/models - List models
 *   GET /health - Health check
 */

const express = require("express");
const cors = require("cors");
const axios = require("axios");

// Configuration
const PORT = process.env.PORT || 3001;
const RORAOS_API_URL = "https://labs.roraos.com/api/v1/chat";
const RORAOS_API_KEY = process.env.RORAOS_API_KEY || "your-api-key-here";

// Express app
const app = express();

// Middleware
app.use(cors());
app.use(express.json());

// Available models
const AVAILABLE_MODELS = [
  { id: "gpt-4o", name: "GPT-4o", provider: "OpenAI" },
  { id: "gpt-4-turbo", name: "GPT-4 Turbo", provider: "OpenAI" },
  { id: "claude-3.5-sonnet", name: "Claude 3.5 Sonnet", provider: "Anthropic" },
  { id: "gemini-2.0-flash", name: "Gemini 2.0 Flash", provider: "Google" },
];

// Helper: Get API key from header or use default
function getApiKey(req) {
  const authHeader = req.headers["x-api-key"] || req.headers["authorization"];
  if (authHeader && authHeader.startsWith("Bearer ")) {
    return authHeader.slice(7);
  }
  return authHeader || RORAOS_API_KEY;
}

// Health check
app.get("/health", (req, res) => {
  res.json({
    status: "healthy",
    service: "roraos-express-proxy",
    timestamp: new Date().toISOString(),
  });
});

// List models
app.get("/api/models", (req, res) => {
  res.json({ models: AVAILABLE_MODELS });
});

// Chat completion
app.post("/api/chat", async (req, res) => {
  try {
    const {
      messages,
      model = "gpt-4o",
      temperature = 0.7,
      max_tokens = 2000,
    } = req.body;

    if (!messages || !Array.isArray(messages)) {
      return res.status(400).json({ error: "messages array is required" });
    }

    const apiKey = getApiKey(req);

    const response = await axios.post(
      RORAOS_API_URL,
      {
        messages,
        model,
        temperature,
        max_tokens,
        stream: false,
      },
      {
        headers: {
          Authorization: `Bearer ${apiKey}`,
          "Content-Type": "application/json",
        },
        timeout: 120000,
      }
    );

    res.json({
      content: response.data.choices[0].message.content,
      model: response.data.model || model,
      usage: response.data.usage,
    });
  } catch (error) {
    console.error("Chat error:", error.message);

    if (error.response) {
      return res.status(error.response.status).json({
        error: error.response.data.error || "API request failed",
      });
    }

    res.status(500).json({ error: "Internal server error" });
  }
});

// Streaming chat completion
app.post("/api/chat/stream", async (req, res) => {
  try {
    const {
      messages,
      model = "gpt-4o",
      temperature = 0.7,
      max_tokens = 2000,
    } = req.body;

    if (!messages || !Array.isArray(messages)) {
      return res.status(400).json({ error: "messages array is required" });
    }

    const apiKey = getApiKey(req);

    // Set SSE headers
    res.setHeader("Content-Type", "text/event-stream");
    res.setHeader("Cache-Control", "no-cache");
    res.setHeader("Connection", "keep-alive");

    const response = await axios.post(
      RORAOS_API_URL,
      {
        messages,
        model,
        temperature,
        max_tokens,
        stream: true,
      },
      {
        headers: {
          Authorization: `Bearer ${apiKey}`,
          "Content-Type": "application/json",
        },
        responseType: "stream",
        timeout: 120000,
      }
    );

    // Pipe stream to response
    response.data.on("data", (chunk) => {
      res.write(chunk);
    });

    response.data.on("end", () => {
      res.end();
    });

    response.data.on("error", (err) => {
      console.error("Stream error:", err);
      res.end();
    });
  } catch (error) {
    console.error("Stream error:", error.message);

    if (!res.headersSent) {
      res.status(500).json({ error: "Internal server error" });
    } else {
      res.end();
    }
  }
});

// =====================================================
// UTILITY ENDPOINTS
// =====================================================

// Summarize text
app.post("/api/summarize", async (req, res) => {
  try {
    const { text, language = "en" } = req.body;

    if (!text) {
      return res.status(400).json({ error: "text is required" });
    }

    const apiKey = getApiKey(req);

    const response = await axios.post(
      RORAOS_API_URL,
      {
        messages: [
          {
            role: "system",
            content: `Summarize the following text concisely in ${language === "id" ? "Indonesian" : "English"}.`,
          },
          { role: "user", content: text },
        ],
        model: "gpt-4o",
        temperature: 0.3,
        max_tokens: 500,
      },
      {
        headers: {
          Authorization: `Bearer ${apiKey}`,
          "Content-Type": "application/json",
        },
      }
    );

    res.json({
      summary: response.data.choices[0].message.content,
    });
  } catch (error) {
    console.error("Summarize error:", error.message);
    res.status(500).json({ error: "Failed to summarize" });
  }
});

// Translate text
app.post("/api/translate", async (req, res) => {
  try {
    const { text, from = "auto", to = "en" } = req.body;

    if (!text) {
      return res.status(400).json({ error: "text is required" });
    }

    const apiKey = getApiKey(req);

    const languageNames = {
      en: "English",
      id: "Indonesian",
      ja: "Japanese",
      ko: "Korean",
      zh: "Chinese",
      es: "Spanish",
      fr: "French",
      de: "German",
    };

    const targetLang = languageNames[to] || to;

    const response = await axios.post(
      RORAOS_API_URL,
      {
        messages: [
          {
            role: "system",
            content: `Translate the following text to ${targetLang}. Only output the translation, nothing else.`,
          },
          { role: "user", content: text },
        ],
        model: "gpt-4o",
        temperature: 0.3,
        max_tokens: 1000,
      },
      {
        headers: {
          Authorization: `Bearer ${apiKey}`,
          "Content-Type": "application/json",
        },
      }
    );

    res.json({
      translation: response.data.choices[0].message.content,
      from,
      to,
    });
  } catch (error) {
    console.error("Translate error:", error.message);
    res.status(500).json({ error: "Failed to translate" });
  }
});

// Generate code
app.post("/api/code/generate", async (req, res) => {
  try {
    const { prompt, language = "javascript" } = req.body;

    if (!prompt) {
      return res.status(400).json({ error: "prompt is required" });
    }

    const apiKey = getApiKey(req);

    const response = await axios.post(
      RORAOS_API_URL,
      {
        messages: [
          {
            role: "system",
            content: `You are an expert ${language} programmer. Generate clean, well-documented code. Only output the code, no explanations unless asked.`,
          },
          { role: "user", content: prompt },
        ],
        model: "gpt-4o",
        temperature: 0.3,
        max_tokens: 2000,
      },
      {
        headers: {
          Authorization: `Bearer ${apiKey}`,
          "Content-Type": "application/json",
        },
      }
    );

    res.json({
      code: response.data.choices[0].message.content,
      language,
    });
  } catch (error) {
    console.error("Code generate error:", error.message);
    res.status(500).json({ error: "Failed to generate code" });
  }
});

// =====================================================
// START SERVER
// =====================================================

app.listen(PORT, () => {
  console.log("=".repeat(50));
  console.log(`RoraOS Express Server`);
  console.log(`Running on http://localhost:${PORT}`);
  console.log("=".repeat(50));
  console.log("Endpoints:");
  console.log(`  GET  /health`);
  console.log(`  GET  /api/models`);
  console.log(`  POST /api/chat`);
  console.log(`  POST /api/chat/stream`);
  console.log(`  POST /api/summarize`);
  console.log(`  POST /api/translate`);
  console.log(`  POST /api/code/generate`);
  console.log("=".repeat(50));
});
