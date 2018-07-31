"""
PlayerInterface is mainly concerned with getting info to-and-from Discord. This info should be relayed to the rest of
the application via Qt Signals
"""
import time

import discord
from PyQt5.QtCore import pyqtSignal, QObject
from discord.ext import commands

from gamelogic import actors

MOVEMENT_WAIT_TIME = 10  # seconds


class PlayerInterface(QObject):
    registered = pyqtSignal(actors.PlayerCharacter)  # (PlayerCharacter)
    moved = pyqtSignal(actors.PlayerCharacter)  # (PlayerCharacter)

    def __init__(self, bot, world, *args, **kwargs):
        self.players = {pc.UserId: pc for pc in world.Players}  # Maps DiscordId -> PlayerCharacter
        self.bot = bot
        self.world = world
        super().__init__(*args, **kwargs)
        self.registered.connect(lambda *_: print('<Emitted "registered">'))
        self.moved.connect(lambda *_: print('<Emitted "moved">'))

    def addPlayer(self, pid, pc):
        self.players[pid] = pc
        self.registered.emit(pc)

    def check_member(self, member):
        return member.id in self.players.keys()

    @commands.command(pass_context=True)
    async def register(self, ctx: discord.ext.commands.context.Context):
        member = ctx.message.author
        if self.check_member(member):
            await self.bot.say("You've already registered, dummy!")
            return
        await self.bot.say("Do you want to join the MUD? (say 'yes' to continue)")
        response = await self.bot.wait_for_message(timeout=5.0, author=member,
                                                   check=lambda msg: msg.content.lower() == 'yes')
        if response is None:
            await self.bot.say('Nevermind...')
            return
        char = actors.PlayerCharacter(member.id, parentworld=self.world)
        await self.bot.say('What is the name of your character?')
        response = await self.bot.wait_for_message(timeout=5.0, author=await self.bot.get_user_info(member.id))
        char.Name = response.content
        await self.bot.say("You've been registered, {}!".format((await self.bot.get_user_info(member.id)).name))
        self.addPlayer(member.id, char)

    @commands.command(pass_context=True)
    async def whoami(self, ctx: discord.ext.commands.context.Context):
        member = ctx.message.author
        if not self.check_member(member):
            await self.bot.say("You're not registered yet!")
            return
        pc = self.players[member.id]
        await self.bot.say('User: {}'.format(member.name))
        await self.bot.say('Player Name: {}'.format(pc.Name))
        await self.bot.say('Class: {}'.format(pc.Class.Name))
        await self.bot.say("Equipment: \n{}".format(str(pc.EquipmentSet)))

    @commands.command(pass_context=True)
    async def whereami(self, ctx: discord.ext.commands.context.Context):
        member = ctx.message.author
        if not self.check_member(member):
            await self.bot.say("You're not registered yet!")
            return
        pc = self.players[member.id]
        if pc.Location is None:
            await self.bot.say("You haven't spawned into the world yet. Something has gone horribly wrong.")
            return
        message = "You are at " + str(pc.Location) + '.'
        l = pc.Location
        if pc.Location in self.world.Towns:
            message += 'You are also in the town ' + self.world.Map[l.Y][l.X].Name + '.'
        if pc.Location in self.world.Wilds:
            message += 'You are also in the wilds, nicknamed ' + self.world.Map[l.Y][l.X].Name + '.'
        await self.bot.say(message)

    @commands.command(pass_context=True)
    async def go(self, ctx: discord.ext.commands.context.Context, direction: str):
        # Get member and assure they're registered
        member = ctx.message.author
        if not self.check_member(member):
            return

        # Ensure the direction given is valid
        pc = self.players[member.id]
        if time.time() - pc.TimeLastMoved < MOVEMENT_WAIT_TIME:
            await self.bot.say("Please wait before making another move.")
            return
        directions = ['n', 's', 'e', 'w']
        if direction not in directions:
            await self.bot.say("Debug: Invalid direction given.")
            return
        # Generate new location based on previous, and check if out-of-bounds
        dir_index = directions.index(direction)
        direction_vectors = [(0, -1), (0, 1), (1, 0), (-1, 0)]
        if pc.attemptMove(direction_vectors[dir_index]):
            await self.bot.say("Your new location is {}".format(str(pc.Location)))
            self.moved.emit(pc)
            pc.TimeLastMoved = time.time()
        else:
            await self.bot.say("Move would put you outside the map!")

    @commands.command(pass_context=True)
    async def world(self, ctx):
        """ TODO Get a picture of the current gameworld. """
        """
        # we need to take a picture of the canvas
        pic_path = app.get_canvas_image()
        with open(pic_path, 'rb') as f:
            await bot.send_file(ctx.message.author, f)
        """
        await self.bot.say("UNIMPLEMENTED")

    @commands.group(name="town", pass_context=True)
    async def _town(self, ctx):
        """ Menu to perform town interactions. """
        # Make checks to ensure user is in a town
        member = ctx.message.author
        if not self.check_member(member):
            await self.bot.say("Please register first")
            return
        pc = self.players[member.id]
        if pc.Location in self.world.Towns:
            await self.bot.say("Debug: You're in a town!")
        else:
            await self.bot.say("Debug: You're NOT in a town!")
        if ctx.invoked_subcommand is None:
            pass

    @_town.command(pass_context=True)
    async def inn(self, ctx):
        """ Rest to restore hitpoints. """
        member = ctx.message.author
        pc = self.players[member.id]
        locat = pc.Location

        town = self.world.Map[locat.Y][locat.X]  # will eventually use to add inn-specific effects
        if pc.Location in self.world.Towns:
            # Restore players' hitpoints
            pc.HitPoints = pc.HitPointsMax
            await self.bot.say("HP Restored!")
        else:
            await self.bot.say("You're not in a Town, much less an Inn!")


# a modified version of the 'cog' setup
def setup(bot, world):
    pi = PlayerInterface(bot, world)
    bot.add_cog(pi)
    return pi
