"""
PlayerInterface is mainly concerned with getting info to-and-from Discord. This info should be relayed to the rest of
the application via Qt Signals
"""
import asyncio
import time

import discord
from PyQt5.QtCore import pyqtSignal, QObject
from discord.ext import commands

from gamelogic import actors, weapons, gamespace

MOVEMENT_WAIT_TIME = .01  # seconds
TIMEOUT = 10.0


class _CogQObjectMeta(commands.CogMeta, type(QObject)):
    """Cog and QObject both bring their own metaclass; Python needs one that is both."""
    pass


class PlayerInterface(commands.Cog, QObject, metaclass=_CogQObjectMeta):
    registered = pyqtSignal(actors.PlayerCharacter)  # (PlayerCharacter)
    moved = pyqtSignal(actors.PlayerCharacter)  # (PlayerCharacter)
    attacked = pyqtSignal(actors.PlayerCharacter, actors.PlayerCharacter, int)  # Source, Target, Damage
    innUsed = pyqtSignal(actors.PlayerCharacter, str)  # PC and Flavor Text
    buildingCreated = pyqtSignal(actors.PlayerCharacter, gamespace.Space)
    requestScreenshot = pyqtSignal(actors.PlayerCharacter)

    # Magic Functions

    def __init__(self, bot, world, *args, **kwargs):
        self.players = {pc.UserId: pc for pc in world.Players}  # Maps DiscordId -> PlayerCharacter
        self.bot = bot
        self.world = world
        super().__init__(*args, **kwargs)

    def addPlayer(self, pid, pc):
        self.players[pid] = pc
        self.registered.emit(pc)

    def check_member(self, member):
        return member.id in self.players.keys()

    async def prompt(self, ctx, question, check=None):
        """Ask the author a question and return their reply, or None on timeout."""
        await ctx.send(question)

        def _check(msg):
            if msg.author != ctx.author or msg.channel != ctx.channel:
                return False
            return check(msg) if check else True

        try:
            return await self.bot.wait_for('message', timeout=TIMEOUT, check=_check)
        except asyncio.TimeoutError:
            return None

    # Registration

    @commands.command()
    async def register(self, ctx: commands.Context):
        member = ctx.author
        if self.check_member(member):
            await ctx.send("You've already registered, dummy!")
            return
        response = await self.prompt(ctx, "Do you want to join the MUD? (say 'yes' to continue)",
                                     check=lambda msg: msg.content.lower() == 'yes')
        if response is None:
            await ctx.send('Nevermind...')
            return
        char = actors.PlayerCharacter(member.id, parentworld=self.world)
        response = await self.prompt(ctx, 'What is the name of your character?')
        if response is None:
            await ctx.send('Nevermind...')
            return
        char.Name = response.content[:255].strip('#<>@.')
        await ctx.send("You've been registered, {}! Or should I say {}? Good luck out there, comrade.".format(
            member.name, char.Name))
        self.addPlayer(member.id, char)

    # Player introspection

    @commands.command()
    async def whoami(self, ctx: commands.Context):
        member = ctx.author
        if not self.check_member(member):
            await ctx.send("You're not registered yet!")
            return
        pc = self.players[member.id]
        msg = "User: {}\n" \
              "Player Name: {}\n" \
              "Class: {}\n" \
              "Health: {}\n" \
              "Currency: {}\n" \
              "Equipment: \n{}".format(member.name,
                                       pc.Name,
                                       pc.Class.Name,
                                       pc.HitPoints,
                                       pc.Currency,
                                       str(pc.EquipmentSet))
        await ctx.send(msg)

    @commands.command()
    async def whereami(self, ctx: commands.Context):
        member = ctx.author
        if not self.check_member(member):
            await ctx.send("You're not registered yet!")
            return
        pc = self.players[member.id]
        if pc.Location is None:
            await ctx.send("You haven't spawned into the world yet. Something has gone horribly wrong.")
            return
        message = "You are at " + str(pc.Location) + '.'
        loc = pc.Location
        if pc.Location in self.world.Towns:
            message += 'You are also in the town ' + self.world.Map[loc.Y][loc.X].Name + '.'
        if pc.Location in self.world.Wilds:
            message += 'You are also in the wilds, nicknamed ' + self.world.Map[loc.Y][loc.X].Name + '.'
        self.requestScreenshot.emit(pc)
        await asyncio.sleep(.05)  # TODO wait on the Qt thread instead of guessing
        with open(r"./capture-{}.png".format(pc.Name), 'rb') as f:
            await member.send(content=message, file=discord.File(f, "capture.png"))

    @commands.group("inventory", invoke_without_command=True)
    async def inventory(self, ctx: commands.Context):
        member = ctx.author
        if not self.check_member(member):
            await ctx.send("You're not registered yet!")
            return
        pc = self.players[member.id]
        if pc.Location is None:
            await ctx.send("You haven't spawned into the world yet. Something has gone horribly wrong.")
            return
        if ctx.invoked_subcommand is None:
            msg = "{}'s inventory:\n".format(pc.Name)
            if len(pc.Inventory) == 0:
                msg += "\t(Empty)"
            else:
                for idx, e in enumerate(pc.Inventory):
                    msg += "\t#{}\t{}\n".format(idx, e)
            await ctx.send(msg)

    # Inventory Management

    @inventory.command()
    async def equip(self, ctx: commands.Context, index):
        member = ctx.author
        if not self.check_member(member):
            await ctx.send("You're not registered yet!")
            return
        pc = self.players[member.id]
        try:
            item = pc.Inventory[int(index)]
            pc.equip(item)
        except IndexError:
            await ctx.send("Invalid index")
        else:
            await ctx.send("{} has been equipped".format(item.Name))

    @inventory.command()
    async def unequip(self, ctx: commands.Context, index):
        member = ctx.author
        if not self.check_member(member):
            await ctx.send("You're not registered yet!")
            return
        pc = self.players[member.id]
        try:
            item = pc.Inventory[int(index)]
            pc.unequip(item)
        except IndexError:
            await ctx.send("Invalid index")
        else:
            await ctx.send("{} has been unequipped".format(item.Name))

    # Player Movement

    @commands.command()
    async def go(self, ctx: commands.Context, direction: str):
        # Get member and assure they're registered
        member = ctx.author
        if not self.check_member(member):
            return
        # Ensure the direction given is valid
        pc = self.players[member.id]
        if time.time() - pc.TimeLastMoved < MOVEMENT_WAIT_TIME:
            await ctx.send("Please wait before making another move.")
            return
        directions = ['n', 's', 'e', 'w']
        if direction not in directions:
            await ctx.send("Debug: Invalid direction given.")
            return
        # Generate new location based on previous, and check if out-of-bounds
        dir_index = directions.index(direction)
        direction_vectors = [(0, -1), (0, 1), (1, 0), (-1, 0)]
        if pc.attemptMove(direction_vectors[dir_index]):
            await ctx.send("Your new location is {}".format(str(pc.Location)))
            self.moved.emit(pc)
            pc.TimeLastMoved = time.time()
        else:
            await ctx.send("Move would put you outside the map!")

    @commands.command()
    async def attack(self, ctx, direction=None):
        member = ctx.author
        if not self.check_member(member):
            return
        pc = self.players[member.id]
        if not pc.hasWeaponEquiped:
            await ctx.send("You must have a weapon equipped to attack")
            return
        if direction and not isinstance(pc.weapon, weapons.RangedWeapon):
            await ctx.send("You must have a ranged weapon to attack at range.")
            return
        directions = {
            'n': (0, -1),
            's': (0, 1),
            'e': (1, 0),
            'w': (-1, 0),
            'ne': (1, -1),
            'se': (1, 1),
            'sw': (-1, 1),
            'nw': (-1, -1),
            None: (0, 0)
        }
        response = self.world.attack(pc, directions[direction])
        if response["success"]:
            await ctx.send("Dealt {} damage to {}".format(response["damage"],
                                                          response["target"].Name))
            self.attacked.emit(pc, response["target"], response["damage"])
        else:
            await ctx.send("Attack failed: {}".format(response["fail_reason"]))

    # World interaction

    @commands.group(name="town", invoke_without_command=True)
    async def town(self, ctx):
        """ Menu to perform town interactions. """
        # Make checks to ensure user is in a town
        member = ctx.author
        if not self.check_member(member):
            await ctx.send("Please register first")
            return
        if ctx.invoked_subcommand is None:
            pc = self.players[member.id]
            for town in self.world.Towns:
                if pc.Location == town:
                    await ctx.send("Debug: You're in {}!".format(town.Name))
                    return
            else:
                await ctx.send("Debug: You're NOT in a town!")

    @town.command()
    async def inn(self, ctx):
        """ Rest to restore hitpoints. """
        member = ctx.author
        pc = self.players[member.id]
        loc = pc.Location
        town = self.world.Map[loc.Y][loc.X]
        if pc.Location in self.world.Towns:
            # Restore players' hitpoints
            response_text = town.innEvent(pc)
            await ctx.send(response_text)
            self.innUsed.emit(pc, response_text)
        else:
            await ctx.send("You're not in a Town, much less an Inn!")

    @commands.group(name="build", invoke_without_command=True)
    async def build(self, ctx):
        member = ctx.author
        if not self.check_member(member):
            await ctx.send("Please register first")
            return
        if ctx.invoked_subcommand is None:
            await ctx.send("Please specify a building.")

    @build.command()
    async def base(self, ctx, *, params: str):
        if params is None:
            await ctx.send("You must give your base a name!")
            return
        member = ctx.author
        player: actors.PlayerCharacter = self.players[member.id]
        location = player.Location
        param_list = params.split(' ')
        if self.world.isBuildable(location):
            try:
                building = gamespace.Base(location.X, location.Y, *param_list)
                self.world.addTown(building)
                await ctx.send("{} base has just been added to the world.".format(building.Name))
                self.buildingCreated.emit(player, building)
            except Exception as e:
                await ctx.send("Error building town: {}".format(e))
        else:
            await ctx.send("Can't build on that location")

    # Store

    @town.group(name="store", invoke_without_command=True)
    async def store(self, ctx):
        member = ctx.author
        pc = self.players[member.id]
        loc = pc.Location
        town = self.world.Map[loc.Y][loc.X]
        msg = "Index\tName\tPrice\tCount\n"
        for idx, item in enumerate(set(town.Store.Inventory)):
            msg += "#{}\t{}\t${}\t{}\n".format(idx,
                                               item.Name,
                                               town.Store.getPrice(item),
                                               town.Store.Inventory.count(item))
        if len(msg) == 0:
            msg += "There are no items in the store at the moment. Please try again later."
        if ctx.invoked_subcommand is None:
            await ctx.send(msg)

    @store.command()
    async def buy(self, ctx, index: int = None):
        if index is None:
            await ctx.send("Please specify an item index.")
            return
        member = ctx.author
        player: actors.PlayerCharacter = self.players[member.id]
        loc = player.Location
        if loc not in self.world.Towns:
            await ctx.send("You're not in a town!")
        town = self.world.Map[loc.Y][loc.X]
        if town.Store.sellItem(index, player):
            await ctx.send("Successfully made purchase.")
        else:
            await ctx.send("Not enough money.")

    @store.command()
    async def sell(self, ctx, index: int = None):
        if index is None:
            await ctx.send("Please specify an item index.")
            return
        member = ctx.author
        player: actors.PlayerCharacter = self.players[member.id]
        loc = player.Location
        town = self.world.Map[loc.Y][loc.X]
        item = player.Inventory[index]
        price = town.Store.buyItem(item, player)
        await ctx.send("Successfully sold {} for ${}".format(item.Name, price))


# a modified version of the 'cog' setup
def setup(bot, world):
    pi = PlayerInterface(bot, world)

    # add_cog is a coroutine in discord.py 2.x, so it has to run on the bot's own loop.
    async def _setup_hook():
        await bot.add_cog(pi)

    bot.setup_hook = _setup_hook
    return pi
