import os
import threading
import time

import discord
from discord.ext import commands

import events
import gamespace
import player
import ui

token = os.environ.get('DISCORD_BOT_TOKEN')

prefix = '*'

description = '''Attempt at a discord MUD server'''

bot = commands.Bot(command_prefix='*', description=description)

world = None
app = None

game_channel = None  # The public text channel where public events take place


# my test routine to initialize the world. Should be replaced with ui stuff eventually
def default_init(xWidth, yHeight):
    world = gamespace.World(xWidth, yHeight)
    example_town = gamespace.Town(5, 3, 'Braxton', 53, gamespace.IndustryType.Mining)
    world.addTown(example_town)
    example_wilds = gamespace.Wilds(5, 2, 'The Ruined Forest')
    event1 = events.CombatEvent(.5, "Test monster appears", "TODO: Monster class", "TODO: conditions class")
    example_wilds.addEvent(event1)
    event2 = events.EncounterEvent(.5, "You found a friendly scav", {"Give meds": "Get $100", "Kill him": "Get pistol"},
                                   "TODO: NPC class")
    example_wilds.addEvent(event2)
    world.addWilds(example_wilds)
    world.StartingTown = example_town
    return world


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
    if member.id in world.Users.keys():
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
        world.Users[user.DiscordUserID] = user


@bot.command(pass_context=True)
async def whoami(ctx: discord.ext.commands.context.Context):
    member = ctx.message.author
    if not await check_member(member):
        return
    user = world.Users[member.id]
    await bot.say('User: {}'.format(member.name))
    await bot.say('Player Name: {}'.format(user.PlayerCharacter.Name))
    await bot.say('Class: {}'.format(user.PlayerCharacter.Class.Name))
    await bot.say("Equipment: \n{}".format(str(user.PlayerCharacter.EquipmentSet)))


@bot.command(pass_context=True)
async def whereami(ctx: discord.ext.commands.context.Context):
    member = ctx.message.author
    if not await check_member(member):
        return
    user = world.Users[member.id]
    message = "You are at " + str(user.Location) + '.'
    if user.Location in world.Towns:
        l = user.Location
        message += 'You are also in the town ' + world.Map[l.Y][l.X].Name + '.'
    if user.Location in world.Wilds:
        l = user.Location
        message += 'You are also in the wilds, nicknamed ' + world.Map[l.Y][l.X].Name + '.'
    await bot.say(message)


@bot.command(pass_context=True)
async def go(ctx: discord.ext.commands.context.Context, dir_in: str):
    member = ctx.message.author
    if not await check_member(member):
        return
    user = world.Users[member.id]
    directions = ['n', 's', 'e', 'w']
    direction_vectors = [gamespace.Space(-1, 0), gamespace.Space(1, 0), gamespace.Space(0, 1), gamespace.Space(0, -1)]
    if dir_in not in directions:
        await bot.say("Invalid direction given.")
        return
    dir_index = directions.index(dir_in)
    new_location = user.Location + direction_vectors[dir_index]
    if new_location.X < 0 or new_location.Y < 0 or new_location.X > world.Width or new_location.Y > world.Height:
        await bot.say("Move would put you outside the map!")
        return
    user.Location = new_location
    world.Users[user.DiscordUserID] = user
    await bot.say("Your new location is ({},{})".format(new_location.X, new_location.Y))
    if user.Location in world.Towns:
        locat = user.Location
        await bot.say('You are also in the town ' + world.Map[locat.Y][locat.X].Name + '.')
    if user.Location in world.Wilds:
        locat = user.Location
        await bot.say('You are also in the wilds, nicknamed ' + world.Map[locat.Y][locat.X].Name + '.')
        world.Map[locat.Y][locat.X].runEvent(user.PlayerCharacter)

@bot.command(pass_context=True)
async def world(ctx):
    '''Get a picture of the current gameworld'''
    # we need to take a picture of the canvas
    pic_path = app.get_canvas_image()
    with open(pic_path, 'rb') as f:
        await bot.send_file(ctx.message.author, f)


async def check_member(m):
    if m.id not in world.Users.keys():
        await bot.say("You're not registered yet!")
        return False
    return True


class MUDUser:
    DiscordUserID: str = None
    PlayerCharacter: player.PlayerCharacter = None
    __x = 0
    __y = 0

    def __init__(self, discord_user_id: str):
        self.DiscordUserID = discord_user_id
        self.__x = world.StartingTown.X
        self.__y = world.StartingTown.Y

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


def listenForWorld():
    global world
    while True:
        world = app.gameWorld
        time.sleep(.25)

threads = {}
if __name__ == "__main__":
    # initialize the bot
    # world = default_init(50, 50)
    tBot = threading.Thread(target=bot.run, args=(token,))
    threads['bot'] = tBot
    tBot.start()

    # initialize the gui
    root = ui.Tk()
    root.geometry("500x500")
    app = ui.Window(root)
    root.protocol("WM_DELETE_WINDOW", app.on_closing)  # close all threads on exit
    root.after(app.REFRESH_RATE, app.update)  # set update hook

    # my hacky way of updating the world
    worldListener = threading.Thread(target=listenForWorld)
    threads['worldlistener'] = worldListener
    worldListener.start()

    # start GUI (LEAVE THIS LAST)
    # apparently can't run tk in a non-main thread
    root.mainloop()
