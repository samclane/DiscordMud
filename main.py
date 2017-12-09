import atexit
import os
import shelve

import discord
from discord.ext import commands

token = os.environ.get("DISCORD_BOT_TOKEN")

prefix = '*'

settings_filename = "settings.dat"
users_filename = "users.dat"
world_filename = "world.dat"

settings = shelve.open(settings_filename)
users = shelve.open(users_filename)
world = shelve.open(world_filename)

game_channel = None
settings['game_channel'] = None

description = '''Attempt at a discord MUD server'''

bot = commands.Bot(command_prefix='*', description=description)


@bot.event
async def on_ready():
    print('Logged in as')
    print(bot.user.name)
    print(bot.user.id)
    print('------')


@bot.event
async def on_server_remove(server: discord.Server):
    print('Logging out')
    print('------')
    save_files()


@atexit.register
def save_files():
    settings.close()
    users.close()
    world.close()


@bot.command(pass_context=True)
async def register(ctx : discord.ext.commands.context.Context):
    member = ctx.message.author
    await bot.say("Do you want to join the MUD?")
    response = await bot.wait_for_message(timeout=5.0, author=member, check=lambda msg: msg.content.lower() == 'yes')
    if response is None:
        await bot.say("Nevermind...")
    elif response:
        settings[member.id] = MUDUser(member)
        await bot.say("You've joined!")


class MUDUser:
    DiscordUser = None

    def __init__(self, discord_user: discord.User):
        self.DiscordUser = discord_user


bot.run(token)
