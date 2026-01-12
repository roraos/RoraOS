/**
 * RoraOS with OpenAI SDK - Node.js Example
 * ===========================================
 *
 * Example of using RoraOS API with OpenAI Node.js SDK.
 *
 * Installation:
 *   npm install openai
 *
 * Usage:
 *   node openai_compatible.js
 */

const OpenAI = require("openai");

// Configuration - use RoraOS as backend
const client = new OpenAI({
  apiKey: "your-api-key-here", // RoraOS API key
  baseURL: "https://labs.roraos.com/api/v1", // RoraOS Base URL
});

async function chatCompletionBasic() {
  console.log("=".repeat(50));
  console.log("Example 1: Basic Chat Completion");
  console.log("=".repeat(50));

  const response = await client.chat.completions.create({
    model: "gpt-4o",
    messages: [
      { role: "system", content: "You are a helpful assistant." },
      { role: "user", content: "Hello! How are you?" },
    ],
    temperature: 0.7,
    max_tokens: 500,
  });

  console.log(`Response: ${response.choices[0].message.content}`);
  console.log(`Model: ${response.model}`);
}

async function chatCompletionStreaming() {
  console.log("\n" + "=".repeat(50));
  console.log("Example 2: Streaming Chat Completion");
  console.log("=".repeat(50));

  const stream = await client.chat.completions.create({
    model: "gpt-4o",
    messages: [
      {
        role: "user",
        content: "Tell me about artificial intelligence in 3 sentences.",
      },
    ],
    stream: true,
  });

  process.stdout.write("Response: ");
  for await (const chunk of stream) {
    const content = chunk.choices[0]?.delta?.content || "";
    process.stdout.write(content);
  }
  console.log();
}

async function multiTurnConversation() {
  console.log("\n" + "=".repeat(50));
  console.log("Example 3: Multi-turn Conversation");
  console.log("=".repeat(50));

  const messages = [
    { role: "system", content: "You are a patient math teacher." },
  ];

  // Turn 1
  messages.push({ role: "user", content: "What is a prime number?" });

  let response = await client.chat.completions.create({
    model: "gpt-4o",
    messages: messages,
  });

  const assistantResponse = response.choices[0].message.content;
  messages.push({ role: "assistant", content: assistantResponse });

  console.log(`User: ${messages[1].content}`);
  console.log(`AI: ${assistantResponse.substring(0, 200)}...`);

  // Turn 2
  messages.push({ role: "user", content: "Give me 5 examples." });

  response = await client.chat.completions.create({
    model: "gpt-4o",
    messages: messages,
  });

  console.log(`\nUser: ${messages[messages.length - 1].content}`);
  console.log(`AI: ${response.choices[0].message.content}`);
}

async function codeGeneration() {
  console.log("\n" + "=".repeat(50));
  console.log("Example 4: Code Generation");
  console.log("=".repeat(50));

  const response = await client.chat.completions.create({
    model: "gpt-4o",
    messages: [
      {
        role: "system",
        content:
          "You are an expert programmer. Provide clean, well-documented code.",
      },
      {
        role: "user",
        content: "Create a JavaScript function to check for palindrome.",
      },
    ],
    temperature: 0.3,
    max_tokens: 500,
  });

  console.log(response.choices[0].message.content);
}

async function main() {
  try {
    await chatCompletionBasic();
    await chatCompletionStreaming();
    await multiTurnConversation();
    await codeGeneration();
  } catch (error) {
    console.error(`Error: ${error.message}`);
    console.log("\nMake sure API_KEY and BASE_URL are correct!");
  }
}

main();
