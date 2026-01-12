"""
RoraOS Discord Bot - Python Example
====================================

Simple Discord bot using RoraOS API.
Can answer questions and have conversations.

Installation:
    pip install discord.py requests

Setup:
    1. Create app at Discord Developer Portal
    2. Create bot and get token
    3. Invite bot to server with proper permissions
    4. Replace BOT_TOKEN and API_KEY below
    5. Run: python discord_bot.py

Features:
    - !ask [question] - Ask AI
    - !chat [message] - Chat with context
    - !clear - Clear conversation history
    - !help - Show help
    - Mention bot to chat
"""

import os
import discord
from discord.ext import commands
import requests
import asyncio

# Configuration
BOT_TOKEN = os.getenv("DISCORD_BOT_TOKEN", "your-discord-bot-token")
API_URL = "https://labs.roraos.com/api/v1/chat"
API_KEY = os.getenv("RORAOS_API_KEY", "your-api-key-here")

# Bot setup
intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix='!', intents=intents)

# Storage for conversation history per channel
conversations = {}


def get_ai_response(channel_id: int, message: str, single_turn: bool = False) -> str:
    """Send message to RoraOS API and get response."""

    if single_turn:
        # Single turn - no history
        messages = [
            {"role": "system", "content": "You are a friendly and helpful AI assistant on Discord."},
            {"role": "user", "content": message}
        ]
    else:
        # Multi turn - with history
        if channel_id not in conversations:
            conversations[channel_id] = [
                {"role": "system", "content": "You are a friendly and helpful AI assistant on Discord. Give clear and concise answers."}
            ]

        conversations[channel_id].append({"role": "user", "content": message})

        # Limit history
        if len(conversations[channel_id]) > 21:
            conversations[channel_id] = [conversations[channel_id][0]] + conversations[channel_id][-20:]

        messages = conversations[channel_id]

    try:
        response = requests.post(
            API_URL,
            headers={
                "Authorization": f"Bearer {API_KEY}",
                "Content-Type": "application/json"
            },
            json={
                "messages": messages,
                "model": "gpt-4o",
                "temperature": 0.7,
                "max_tokens": 1500
            },
            timeout=60
        )
        response.raise_for_status()

        data = response.json()
        assistant_message = data["choices"][0]["message"]["content"]

        # Save response to history (only for multi-turn)
        if not single_turn and channel_id in conversations:
            conversations[channel_id].append({"role": "assistant", "content": assistant_message})

        return assistant_message

    except requests.exceptions.RequestException as e:
        return f"Error: {str(e)}"


@bot.event
async def on_ready():
    print(f'Bot logged in as {bot.user}')
    await bot.change_presence(activity=discord.Game(name="!help for help"))


@bot.command(name='ask')
async def ask(ctx, *, question: str = None):
    """Ask AI (single turn, no history)"""
    if not question:
        await ctx.send("Usage: `!ask [question]`")
        return

    async with ctx.typing():
        response = await asyncio.to_thread(get_ai_response, ctx.channel.id, question, single_turn=True)

    # Split response if too long
    if len(response) > 2000:
        for i in range(0, len(response), 2000):
            await ctx.send(response[i:i+2000])
    else:
        await ctx.send(response)


@bot.command(name='chat')
async def chat(ctx, *, message: str = None):
    """Chat with AI (multi-turn with history)"""
    if not message:
        await ctx.send("Usage: `!chat [message]`")
        return

    async with ctx.typing():
        response = await asyncio.to_thread(get_ai_response, ctx.channel.id, message, single_turn=False)

    if len(response) > 2000:
        for i in range(0, len(response), 2000):
            await ctx.send(response[i:i+2000])
    else:
        await ctx.send(response)


@bot.command(name='clear')
async def clear(ctx):
    """Clear conversation history"""
    channel_id = ctx.channel.id
    if channel_id in conversations:
        del conversations[channel_id]
    await ctx.send("Conversation history cleared!")


@bot.event
async def on_message(message):
    # Ignore bot's own messages
    if message.author == bot.user:
        return

    # Respond when mentioned
    if bot.user.mentioned_in(message) and not message.mention_everyone:
        content = message.content.replace(f'<@{bot.user.id}>', '').strip()
        if content:
            async with message.channel.typing():
                response = await asyncio.to_thread(get_ai_response, message.channel.id, content, single_turn=False)

            if len(response) > 2000:
                for i in range(0, len(response), 2000):
                    await message.channel.send(response[i:i+2000])
            else:
                await message.reply(response)

    await bot.process_commands(message)


# Override default help
bot.remove_command('help')

@bot.command(name='help')
async def help_command(ctx):
    """Show help"""
    embed = discord.Embed(
        title="RoraOS AI Bot",
        description="AI Assistant powered by RoraOS",
        color=discord.Color.blue()
    )
    embed.add_field(name="!ask [question]", value="Ask AI (no history)", inline=False)
    embed.add_field(name="!chat [message]", value="Chat with AI (with history)", inline=False)
    embed.add_field(name="!clear", value="Clear conversation history", inline=False)
    embed.add_field(name="@mention", value="Mention bot to chat", inline=False)
    embed.set_footer(text="Powered by RoraOS API")
    await ctx.send(embed=embed)


if __name__ == "__main__":
    bot.run(BOT_TOKEN)
