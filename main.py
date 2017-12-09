import atexit
import os
import shelve

import discord

client = discord.Client()

token = os.environ.get("DISCORD_BOT_TOKEN")

prefix = '*'

settings_filename = "settings.dat"
users_filename = "users.dat"
world_filename = "world.dat"

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
        text = message.content.replace(prefix, '')  # strip the prefix from the message
        user = message.author
        channel = message.channel
        if not (user.id in users.keys()):
            users[user.id] = MUDUser(user)
            await register_user(users[user.id], channel)


@client.event
async def on_server_remove(server: discord.Server):
    print('Logging out')
    print('------')
    save_files()


@atexit.register
def save_files():
    settings.close()
    users.close()
    world.close()


class MUDUser:
    DiscordUser = None

    def __init__(self, discord_user: discord.User):
        self.DiscordUser = discord_user


async def register_user(mud_user: MUDUser, channel: discord.Channel):
    await client.send_message(channel, mud_user.DiscordUser.name + ", would you like to join the MUD?")
    return


client.run(token)
