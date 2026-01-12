/**
 * RoraOS Agent Chat API - JavaScript Example
 * ===========================================
 *
 * Example of using the Agent Chat API.
 * Each agent has a unique API key and pre-configured system prompt.
 *
 * Usage in Node.js:
 *   node agent_api.js
 *
 * Usage in Browser:
 *   Import the required functions
 */

// Configuration
const API_URL = "https://labs.roraos.com/api/v1/agents/chat";
const AGENT_API_KEY = "agent_xxxxxxxxxxxxx"; // Agent-specific API key

/**
 * Send chat request to Agent API
 *
 * @param {Array} messages - Array of messages [{role, content}]
 * @param {Object} options - Additional options
 * @param {boolean} options.stream - Use streaming
 * @param {number} options.temperature - Override temperature (optional)
 * @param {number} options.max_tokens - Override max_tokens (optional)
 * @returns {Promise} Response from API
 */
async function agentChat(messages, options = {}) {
  const { stream = false, temperature, max_tokens } = options;

  const payload = {
    messages,
    stream,
  };

  // Optional overrides
  if (temperature !== undefined) payload.temperature = temperature;
  if (max_tokens !== undefined) payload.max_tokens = max_tokens;

  if (stream) {
    return agentChatStream(payload);
  }

  const response = await fetch(API_URL, {
    method: "POST",
    headers: {
      Authorization: `Bearer ${AGENT_API_KEY}`,
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
async function agentChatStream(payload) {
  const response = await fetch(API_URL, {
    method: "POST",
    headers: {
      Authorization: `Bearer ${AGENT_API_KEY}`,
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
          const content = parsed.content || "";
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
  // Example 1: Chat with agent
  console.log("=".repeat(50));
  console.log("Example 1: Chat with Agent");
  console.log("=".repeat(50));

  try {
    const messages = [
      { role: "user", content: "Hello! What can you help me with?" },
    ];
    const result = await agentChat(messages);
    console.log(`Agent: ${result.agent?.name || "Unknown"}`);
    console.log(`Response: ${result.choices[0].message.content}`);
  } catch (error) {
    console.log(`Error: ${error.message}`);
  }

  // Example 2: Multi-turn conversation
  console.log("\n" + "=".repeat(50));
  console.log("Example 2: Multi-turn Conversation");
  console.log("=".repeat(50));

  try {
    const conversation = [];

    // Turn 1
    conversation.push({
      role: "user",
      content: "I want to learn programming",
    });

    let result = await agentChat(conversation);
    const response1 = result.choices[0].message.content;
    console.log(`User: ${conversation[conversation.length - 1].content}`);
    console.log(`Agent: ${response1}`);

    // Save response
    conversation.push({ role: "assistant", content: response1 });

    // Turn 2
    conversation.push({ role: "user", content: "Where should I start?" });

    result = await agentChat(conversation);
    console.log(`\nUser: ${conversation[conversation.length - 1].content}`);
    console.log(`Agent: ${result.choices[0].message.content}`);
  } catch (error) {
    console.log(`Error: ${error.message}`);
  }

  // Example 3: Streaming with override settings
  console.log("\n" + "=".repeat(50));
  console.log("Example 3: Streaming with Custom Settings");
  console.log("=".repeat(50));

  try {
    const messages = [
      { role: "user", content: "Give me productivity tips." },
    ];
    process.stdout.write("Response: ");
    await agentChat(messages, {
      stream: true,
      temperature: 0.8,
      max_tokens: 500,
    });
  } catch (error) {
    console.log(`Error: ${error.message}`);
  }
}

// Run examples
main().catch(console.error);

// Export for use as module
if (typeof module !== "undefined") {
  module.exports = { agentChat, agentChatStream };
}
