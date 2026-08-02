"""Smoke check that the bot still wires up against the installed discord.py."""
import asyncio
import types
import unittest

import discord_interface.basic_bot as gBot
import discord_interface.player_interface as player_interface


class BotSetupTest(unittest.TestCase):

    def test_cog_commands_registered(self):
        pi = player_interface.setup(gBot.bot, types.SimpleNamespace(Players=[]))
        asyncio.run(gBot.bot.setup_hook())
        names = {c.name for c in gBot.bot.commands}
        self.assertLessEqual({'register', 'whoami', 'whereami', 'inventory', 'go', 'attack', 'town', 'build'}, names)
        self.assertEqual({'inn', 'store'}, {c.name for c in gBot.bot.get_command('town').commands})
        self.assertEqual({'buy', 'sell'}, {c.name for c in gBot.bot.get_command('town').get_command('store').commands})
        self.assertTrue(gBot.bot.intents.message_content)
        self.assertIs(pi, gBot.bot.get_cog('PlayerInterface'))


if __name__ == "__main__":
    unittest.main()
