import os

import discord
from discord.ext import commands
import shelve

import player
import gamespace

token = os.environ.get('DISCORD_BOT_TOKEN')

prefix = '*'

settings_filename = 'settings'

settings = shelve.open(settings_filename)

description = '''Attempt at a discord MUD server'''

bot = commands.Bot(command_prefix='*', description=description)


def default_init():
    settings['users'] = {}
    settings['player_characters'] = {}
    settings['world']: gamespace.World = gamespace.World(50, 50)
    settings['game_channel'] = None
    settings['starting_town'] = gamespace.Town(0, 0, 'Braxton', 53, gamespace.IndustryType.Mining)


def save_setting(name, index, value):
    subsetting = settings[name]
    subsetting[index] = value
    settings[name] = subsetting


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
    if member.id in settings['users'].keys():
        await bot.say("You're already registered, dummy!")
        return
    await bot.say("Do you want to join the MUD? (say 'yes' to continue)")
    response = await bot.wait_for_message(timeout=5.0, author=member, check=lambda msg: msg.content.lower() == 'yes')
    if response is None:
        await bot.say('Nevermind...')
    elif response:
        user = MUDUser(member.id)
        await CreatePlayerCharacter(user)
        await bot.say("You've been registered, {}!".format((await bot.get_user_info(user.DiscordUserID)).name))
        save_setting('users', user.DiscordUserID, user)


async def check_member(m):
    if m.id not in settings['users'].keys():
        await bot.say("You're not registered yet!")
        return False
    return True


@bot.command(pass_context=True)
async def whoami(ctx: discord.ext.commands.context.Context):
    member = ctx.message.author
    if not await check_member(member):
        return
    user = settings['users'][member.id]
    await bot.say('User: {}'.format(member.name))
    await bot.say('Player Name: {}'.format(user.PlayerCharacter.Name))
    await bot.say('Class: {}'.format(user.PlayerCharacter.Class.Name))
    await bot.say("Equipment: \n{}".format(str(user.PlayerCharacter.EquipmentSet)))


@bot.command(pass_context=True)
async def whereami(ctx: discord.ext.commands.context.Context):
    member = ctx.message.author
    if not await check_member(member):
        return
    user = settings['users'][member.id]
    message = "You are at " + str(user.Location) + '.'
    # if user.Location in settings['world'].Towns:
    #    message += ' You are also in the town ' + settings[]
    await bot.say(message)


class MUDUser:
    DiscordUserID: str = None
    __x = 0
    __y = 0

    def __init__(self, discord_user_id: str):
        self.DiscordUserID = discord_user_id
        self.__x = settings['starting_town'].X
        self.__y = settings['starting_town'].Y

    @property
    def PlayerCharacter(self):
        return settings['player_characters'][self.DiscordUserID]

    @PlayerCharacter.setter
    def PlayerCharacter(self, x: player.PlayerCharacter):
        save_setting('player_characters', self.DiscordUserID, x)

    @property
    def Location(self):
        return gamespace.Space(self.__x, self.__y)


async def CreatePlayerCharacter(mud_user: MUDUser):
    char = player.PlayerCharacter(mud_user.DiscordUserID)
    await bot.say('What is the name of your character?')
    response = await bot.wait_for_message(timeout=5.0, author=await bot.get_user_info(mud_user.DiscordUserID))
    char.Name = response.content
    mud_user.PlayerCharacter = char


default_init()
bot.run(token)
