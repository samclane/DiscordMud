import unittest
from builtins import property

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
        player.Class = WandererClass()
        self.assertEqual(player.Name, "Algor")
        self.assertIsInstance(player.Class, WandererClass)
        self.assertEqual(player.HitPoints, WandererClass().HitPointsMaxBase)

    def test_equipment(self):
        es = EquipmentSet()
        es.Chest = ChestArmor(1, 'Chain Mail', 100, 1000)
        es.Head = HeadArmor(1, 'Steel Helmet', 100, 1000)
        es.Feet = FootArmor(1, 'Steel Boots', 100, 1000)
        es.Legs = LegArmor(0, 'Pantaloons', 100, 1000)
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

    def test_distance(self):
        s1 = Space(0, 0)
        s2 = Space(3, 4)
        d12 = s1.distance(s2)
        self.assertEqual(d12, 5)
        s3 = Space(1, 2)
        s4 = Space(4, 6)
        d34 = s3.distance(s4)
        self.assertEqual(d34, 5)

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

    def test_combat(self):
        w = World("Testworld", 50, 50)
        t = Town(0, 0, "Testville", 123, 1, SandTerrain())
        w.addTown(t, True)
        p1 = PlayerCharacter(None, w, hp=100, name='p1')
        p2 = PlayerCharacter(None, w, hp=100, name='p2')
        w.addActor(p1)
        w.addActor(p2)
        self.assertEqual(p1.Location.distance(p2.Location), 0)
        if not p1.attemptMove((3, 4)):
            self.fail("P1 couldn't move for some reason.")
        self.assertEqual(p1.Location.distance(p2.Location), 5)
        ppsh41 = PPSh41()
        p1.equip(ppsh41)
        ak = AK47()
        p2.equip(ak)
        self.assertEqual(p1.EquipmentSet.MainHand, ppsh41)
        self.assertEqual(p1.EquipmentSet.OffHand, ppsh41)
        self.assertEqual(p2.EquipmentSet.MainHand, ak)
        self.assertEqual(p2.EquipmentSet.OffHand, ak)
        p1.attack(p2)
        print(p2.HitPoints, p2.HitPointsMax)
        if not p1.attemptMove((-2, -3)):
            self.fail("P1 couldn't move for some reason")
        p1.attack(p2)
        print(p2.HitPoints, p2.HitPointsMax)




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
        w = Weapon(dmg, name=name, weightlb=weight, base_value=value)
        r = RangedWeapon(rng, base_damage=dmg, name=name, weightlb=weight, base_value=value)
        p = ProjectileWeapon(ProjectileType.Thrown, base_damage=dmg, name=name, weightlb=weight, base_value=value)
        f1 = Firearm(Caliber.BB, FiringAction.BurstFireOnly, burst_size=3, capacity=capacity, base_damage=dmg,
                     name=name, weightlb=weight,
                     base_value=value)
        f2 = Firearm(Caliber.BB, FiringAction.SingleShot, capacity=1, base_damage=dmg, name=name, weightlb=weight,
                     base_value=value)
        m = MeleeWeapon(dmg, name=name, weightlb=weight, base_value=value)
        b = BladedWeapon(chance, factor, dmg, name=name, weightlb=weight, base_value=value)
        bu = BluntWeapon(chance, dmg, name=name, weightlb=weight, base_value=value)
        re = WeblyRevolver()
        aps = APS()
        pp = PPSh41()
        ow = OwenSMG()
        ak = AK47()
        hk = HKG3()
        j = Jezail()
        fn = FNMinimi()

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
        f1.reload()
        self.assertEqual(f1.currentCapacity, capacity)
        aps.toggleAction()
        self.assertEqual(aps.Action, FiringAction.FullyAutomatic)
        aps.toggleAction()
        self.assertEqual(aps.Action, FiringAction.SemiAutomatic)

        print("")
        print(ImplementedWeaponsList)
        print("---")
        print(ImplementedWeaponsDict)
