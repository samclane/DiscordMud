import os

import discord
from discord.ext import commands

TOKEN = os.environ.get('DISCORD_TOKEN')
PREFIX = '*'
DESCRIPTION = "Attempt at a Discord MUD Server"

# message_content is privileged: enable it for the bot in the Discord developer portal.
intents = discord.Intents.default()
intents.message_content = True

bot = commands.Bot(command_prefix=PREFIX, description=DESCRIPTION, intents=intents)


@bot.event
async def on_ready():
    print('Logged in as')
    print(bot.user.name)
    print(bot.user.id)
    print('------')
