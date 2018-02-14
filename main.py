import os
import shelve
import threading

import discord
from discord.ext import commands

import gamespace
import player
import ui

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
    w = settings['world']
    t = gamespace.Town(5, 3, 'Braxton', 53, gamespace.IndustryType.Mining)
    w.addTown(t)
    f = gamespace.Wilds(5, 2, 'The Ruined Forest')
    w.addWilds(f)
    save_setting('world', None, w)
    settings['starting_town'] = t
    settings['game_channel'] = None  # The public text channel where public events take place


def save_setting(name, index, value):
    subsetting = settings[name]
    if index is not None:
        subsetting[index] = value
    else:
        subsetting = value
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
    if user.Location in settings['world'].Towns:
        l = user.Location
        message += 'You are also in the town ' + settings['world'].Map[l.X][l.Y].Name + '.'
    if user.Location in settings['world'].Wilds:
        l = user.Location
        message += 'You are also in the wilds, nicknamed ' + settings['world'].Map[l.X][l.Y].Name + '.'
    await bot.say(message)


@bot.command(pass_context=True)
async def go(ctx: discord.ext.commands.context.Context, dir_in: str):
    member = ctx.message.author
    if not await check_member(member):
        return
    user = settings['users'][member.id]
    directions = ['n', 's', 'e', 'w']
    direction_vectors = [gamespace.Space(0, 1), gamespace.Space(0, -1), gamespace.Space(1, 0), gamespace.Space(-1, 0)]
    if dir_in not in directions:
        await bot.say("Invalid direction given.")
        return
    dir_index = directions.index(dir_in)
    new_location = user.Location + direction_vectors[dir_index]
    world = settings['world']
    if new_location.X < 0 or new_location.Y < 0 or new_location.X > world.Width or new_location.Y > world.Height:
        await bot.say("Move would put you outside the map!")
        return
    user.Location = new_location
    save_setting('users', user.DiscordUserID, user)
    await bot.say("Your new location is ({},{})".format(new_location.X, new_location.Y))
    if user.Location in settings['world'].Towns:
        locat = user.Location
        await bot.say('You are also in the town ' + settings['world'].Map[locat.X][locat.Y].Name + '.')
    if user.Location in settings['world'].Wilds:
        locat = user.Location
        await bot.say('You are also in the wilds, nicknamed ' + settings['world'].Map[locat.X][locat.Y].Name + '.')
        settings['world'].Map[locat.X][locat.Y].runEvent()


class MUDUser:
    DiscordUserID: str = None
    __x = 0
    __y = 0

    # PlayerCharacter
    # Location

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

    @Location.setter
    def Location(self, other: gamespace.Space):
        self.__x = other.X
        self.__y = other.Y


async def CreatePlayerCharacter(mud_user: MUDUser):
    char = player.PlayerCharacter(mud_user.DiscordUserID)
    await bot.say('What is the name of your character?')
    response = await bot.wait_for_message(timeout=5.0, author=await bot.get_user_info(mud_user.DiscordUserID))
    char.Name = response.content
    mud_user.PlayerCharacter = char

threads = []
if __name__ == "__main__":
    # initialize the bot
    default_init()
    tBot = threading.Thread(target=bot.run, args=(token,))
    threads.append(tBot)
    tBot.start()

    # initialize the gui
    root = ui.Tk()
    root.geometry("1500x1500")
    app = ui.Window(root, settings)
    tGUI = threading.Thread(target=root.mainloop())
    threads.append(tGUI)
    tGUI.start()

