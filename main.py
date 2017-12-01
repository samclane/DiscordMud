import discord
import asyncio
import os

client = discord.Client()

token = os.environ.get("DISCORD_BOT_TOKEN")

prefix = '*'

@client.event
async def on_ready():
    print('Logged in as')
    print(client.user.name)
    print(client.user.id)
    print('------')


@client.event
async def on_message(message):
    if message.content.startswith(prefix + 'ping'):
        await client.send_message(message.channel, 'Pong!')

client.run(token)
