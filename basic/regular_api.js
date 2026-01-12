/**
 * RoraOS Regular Chat API - JavaScript Example
 * =============================================
 *
 * Example of using the Regular Chat API for chat completion.
 * This API is compatible with OpenAI format.
 *
 * Usage in Node.js:
 *   node regular_api.js
 *
 * Usage in Browser:
 *   Import the required functions
 */

// Configuration
const API_URL = "https://labs.roraos.com/api/v1/chat";
const API_KEY = "your-api-key-here"; // Get from dashboard

/**
 * Send chat completion request to API
 *
 * @param {Array} messages - Array of messages [{role, content}]
 * @param {Object} options - Additional options
 * @param {boolean} options.stream - Use streaming
 * @param {number} options.temperature - Creativity (0-2)
 * @param {number} options.max_tokens - Maximum tokens
 * @returns {Promise} Response from API
 */
async function chatCompletion(messages, options = {}) {
  const { stream = false, temperature = 0.7, max_tokens = 2000 } = options;

  const payload = {
    messages,
    model: "gpt-4o", // Model displayed, backend uses available model
    stream,
    temperature,
    max_tokens,
  };

  if (stream) {
    return chatCompletionStream(payload);
  }

  const response = await fetch(API_URL, {
    method: "POST",
    headers: {
      Authorization: `Bearer ${API_KEY}`,
      "Content-Type": "application/json",
    },
    body: JSON.stringify(payload),
  });

  if (!response.ok) {
    const error = await response.json();
    throw new Error(error.error || "API request failed");
  }

  return response.json();
}

/**
 * Handle streaming response
 */
async function chatCompletionStream(payload) {
  const response = await fetch(API_URL, {
    method: "POST",
    headers: {
      Authorization: `Bearer ${API_KEY}`,
      "Content-Type": "application/json",
    },
    body: JSON.stringify(payload),
  });

  if (!response.ok) {
    const error = await response.json();
    throw new Error(error.error || "API request failed");
  }

  const reader = response.body.getReader();
  const decoder = new TextDecoder();
  let fullContent = "";

  while (true) {
    const { done, value } = await reader.read();
    if (done) break;

    const chunk = decoder.decode(value);
    const lines = chunk.split("\n");

    for (const line of lines) {
      if (line.startsWith("data: ")) {
        const data = line.slice(6);
        if (data === "[DONE]") break;

        try {
          const parsed = JSON.parse(data);
          const content =
            parsed.content ||
            parsed.choices?.[0]?.delta?.content ||
            "";
          if (content) {
            fullContent += content;
            process.stdout.write(content);
          }
        } catch {
          // Skip invalid JSON
        }
      }
    }
  }

  console.log(); // New line
  return fullContent;
}

// ============ Usage Examples ============

async function main() {
  // Example 1: Simple chat
  console.log("=".repeat(50));
  console.log("Example 1: Simple Chat");
  console.log("=".repeat(50));

  try {
    const messages = [{ role: "user", content: "Hello! Who are you?" }];
    const result = await chatCompletion(messages);
    console.log(`Response: ${result.choices[0].message.content}`);
  } catch (error) {
    console.log(`Error: ${error.message}`);
  }

  // Example 2: Chat with context (multi-turn)
  console.log("\n" + "=".repeat(50));
  console.log("Example 2: Multi-turn Chat");
  console.log("=".repeat(50));

  try {
    const messages = [
      {
        role: "system",
        content: "You are a helpful assistant.",
      },
      { role: "user", content: "What is JavaScript?" },
      {
        role: "assistant",
        content: "JavaScript is a programming language for web development.",
      },
      { role: "user", content: "Give me a simple code example." },
    ];

    const result = await chatCompletion(messages, { temperature: 0.5 });
    console.log(`Response: ${result.choices[0].message.content}`);
  } catch (error) {
    console.log(`Error: ${error.message}`);
  }

  // Example 3: Streaming response
  console.log("\n" + "=".repeat(50));
  console.log("Example 3: Streaming Response");
  console.log("=".repeat(50));

  try {
    const messages = [
      { role: "user", content: "Explain AI in 3 sentences." },
    ];
    process.stdout.write("Response: ");
    await chatCompletion(messages, { stream: true });
  } catch (error) {
    console.log(`Error: ${error.message}`);
  }
}

// Run examples
main().catch(console.error);

// Export for use as module
if (typeof module !== "undefined") {
  module.exports = { chatCompletion, chatCompletionStream };
}
