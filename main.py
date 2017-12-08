import discord
import asyncio
import shelve
import os

client = discord.Client()

token = os.environ.get("DISCORD_BOT_TOKEN")

prefix = '*'

settings_filename = os.path.join(os.path.dirname(__file__), '/settings')

users_filename = os.path.join(os.path.dirname(__file__), '/users')

world_filename = os.path.join(os.path.dirname(__file__), '/world')

settings = shelve.open(settings_filename)

users = shelve.open(users_filename)

world = shelve.open(world_filename)

@client.event
async def on_ready():
    print('Logged in as')
    print(client.user.name)
    print(client.user.id)
    print('------')


@client.event
async def on_message(message: discord.Message):
    if message.content.startswith(prefix):
        text = message.content.replace('prefix', '') #strip the prefix from the message
        user = message.author


@client.event
async def on_server_remove(server: discord.Server):
    print('Logging out')
    print('------')
    settings.close()
    users.close()
    world.close()

client.run(token)
