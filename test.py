import unittest

from gamelogic.gamespace import *
from gamelogic.items import *
from gamelogic.player import *
from gamelogic.events import *

class PlayerTest(unittest.TestCase):

    def setUp(self):
        pass

    def test_player_object(self):
        player = PlayerCharacter(None)
        player.Name = "Algor"
        player.Class = WandererClass
        player.HitPoints = 100
        self.assertEqual(player.Name, "Algor")
        self.assertEqual(player.Class, WandererClass)
        self.assertEqual(player.HitPoints, 100)

    def test_equipment(self):
        es = EquipmentSet
        es.Chest = ChestEquipment('Chain Mail', 100, 1000)
        es.Head = HeadEquipment('Steel Helmet', 100, 1000)
        es.Feet = FeetEquipment('Steel Boots', 100, 1000)
        es.Legs = LegsEquipment('Pantaloons', 100, 1000)
        es.MainHand = MainHandEquipment('Steel Sword', 10, 100)
        es.OffHand = OffHandEquipment('Shield', 10, 1000)
        self.assertEqual(es.Chest.Name, 'Chain Mail')

    def test_world(self):
        w = World(50, 50)
        t = Town(1, 1, 'Braxton', 50, FarmingIndustry)
        w.addTown(t)
        self.assertIn(t, w.Towns)
        i = Wilds(2, 2, 'Hidden Forrest')
        w.addWilds(i)
        self.assertIn(i, w.Wilds)

    def test_run_event(self):
        w = World(50, 50)
        i = Wilds(2, 2, 'Hidden Forrest')
        e = EncounterEvent(.5, "You find a penny in the road.",
                           {"Pick it up": "Gain a penny", "Leave it": "Gain nothing"})
        i.addEvent(e)
        w.addWilds(i)
        player = PlayerCharacter(None)
        player.Name = "Algor"
        player.Class = WandererClass
        player.HitPoints = 100
        i.runEvent(player)
