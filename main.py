import os

import discord
from discord.ext import commands

import player

token = os.environ.get("DISCORD_BOT_TOKEN")

prefix = '*'

settings_filename = "settings.dat"
users_filename = "users.dat"
world_filename = "world.dat"

settings = {}
users = {}
player_characters = {}
world = {}

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


@bot.command(pass_context=True)
async def register(ctx: discord.ext.commands.context.Context):
    member = ctx.message.author
    await bot.say("Do you want to join the MUD? (say 'yes' to continue)")
    response = await bot.wait_for_message(timeout=5.0, author=member, check=lambda msg: msg.content.lower() == 'yes')
    if response is None:
        await bot.say("Nevermind...")
    elif response:
        user = MUDUser(member.id)
        await user.create_character()
        await bot.say("You've been registered, {}!".format((await bot.get_user_info(user.DiscordUserID)).name))
        users[member.id] = user


@bot.command(pass_context=True)
async def whoami(ctx: discord.ext.commands.context.Context):
    member = ctx.message.author
    user = users[member.id]
    await bot.say("User: ".format(member.name))
    await bot.say("Player Name: ".format(user.PlayerCharacter.Name))
    await bot.say("Class: ".format(user.PlayerCharacter.Class))
    await bot.say("Equipment: " + str(user.PlayerCharacter.EquipmentSet))


class MUDUser:
    DiscordUserID: str = None

    def __init__(self, discord_user_id: str):
        self.DiscordUserID = discord_user_id

    async def create_character(self):
        await CreatePlayerCharacter(self)

    @property
    def PlayerCharacter(self):
        return player_characters[self.DiscordUserID]

    @PlayerCharacter.setter
    def PlayerCharacter(self, x):
        player_characters[self.DiscordUserID] = x


async def CreatePlayerCharacter(mud_user: MUDUser):
    char = player.PlayerCharacter()
    await bot.say("What is the name of your character?")
    response = await bot.wait_for_message(timeout=5.0, author=await bot.get_user_info(mud_user.DiscordUserID))
    char.Name = response.content
    mud_user.PlayerCharacter = char


bot.run(token)
