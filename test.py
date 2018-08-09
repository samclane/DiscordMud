import unittest

from gamelogic.actors import *
from gamelogic.events import *
from gamelogic.gamespace import *
from gamelogic.items import *
from gamelogic.weapons import *


class PlayerTest(unittest.TestCase):

    def setUp(self):
        pass

    def test_player_object(self):
        player = PlayerCharacter(None, None)
        player.Name = "Algor"
        player.Class = WandererClass
        player.HitPoints = 100
        self.assertEqual(player.Name, "Algor")
        self.assertEqual(player.Class, WandererClass)
        self.assertEqual(player.HitPoints, 100)

    def test_equipment(self):
        es = EquipmentSet()
        es.Chest = ChestEquipment('Chain Mail', 100, 1000)
        es.Head = HeadEquipment('Steel Helmet', 100, 1000)
        es.Feet = FeetEquipment('Steel Boots', 100, 1000)
        es.Legs = LegsEquipment('Pantaloons', 100, 1000)
        es.MainHand = MainHandEquipment('Steel Sword', 10, 100)
        es.OffHand = OffHandEquipment('Shield', 10, 1000)
        self.assertEqual(es.Chest.Name, 'Chain Mail')

    def test_world(self):
        w = World("Testworld", 50, 50)
        t = Town(1, 1, 'Braxton', 50, FarmingIndustry)
        w.addTown(t)
        self.assertIn(t, w.Towns)
        i = Wilds(2, 2, 'Hidden Forrest')
        w.addWilds(i)
        self.assertIn(i, w.Wilds)

    def test_run_event(self):
        w = World("Testworld", 50, 50)
        i = Wilds(2, 2, 'Hidden Forrest')
        e = EncounterEvent(.5, "You find a penny in the road.",
                           {"Pick it up": "Gain a penny", "Leave it": "Gain nothing"})
        e2 = EncounterEvent(.5, "You find a scav in the road.",
                            {"Shoot him": "Gain a gun", "Leave him": "Get shot (-5hp)"})
        i.addEvent(e)
        i.addEvent(e2)
        w.addWilds(i)
        player = PlayerCharacter(None, None)
        player.Name = "Algor"
        player.Class = WandererClass
        player.HitPoints = 100
        i.runEvent(player)


class WeaponsTest(unittest.TestCase):

    def setUp(self):
        pass

    def test_init(self):
        name = "TestName"
        weight = 100
        value = 100
        dmg = 5
        rng = 2
        chance = 0.5
        factor = 0.1
        capacity = 30
        w = Weapon(dmg, name=name, weight=weight, base_value=value)
        r = RangedWeapon(rng, base_damage=dmg, name=name, weight=weight, base_value=value)
        p = ProjectileWeapon(ProjectileType.Thrown, base_damage=dmg, name=name, weight=weight, base_value=value)
        f1 = Firearm(Caliber.BB, burst_size=3, capacity=capacity, base_damage=dmg, name=name, weight=weight,
                     base_value=value)
        f2 = Firearm(Caliber.BB, capacity=1, base_damage=dmg, name=name, weight=weight, base_value=value)
        m = MeleeWeapon(dmg, name=name, weight=weight, base_value=value)
        b = BladedWeapon(chance, factor, dmg, name=name, weight=weight, base_value=value)
        bu = BluntWeapon(chance, dmg, name=name, weight=weight, base_value=value)

        self.assertEqual(r.Range, rng)
        self.assertEqual(f1.Range, 1)
        self.assertEqual(f1.Capacity, capacity)
        self.assertEqual(f1.currentCapacity, capacity)
        self.assertFalse(f1.isSingleShot)
        self.assertTrue(f2.isSingleShot)
        with self.assertRaises(AttributeError) as _:
            f1.currentCapacity = 5
        f1.fire()
        self.assertEqual(f1.currentCapacity, capacity - f1.BurstSize)
        f2.fire()
        self.assertTrue(f2.isEmpty)
