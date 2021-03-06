from PyQt5.QtCore import QObject, pyqtSignal

from gamelogic import items, gamespace, weapons


class BodyType:
    Humanoid = 1
    SmallAnimal = 2
    LargeAnimal = 3
    Monstrosity = 4
    Mechanical = 5


class Actor:

    def __init__(self, parentworld, hp: int = 0, name: str = "", body_type: int = 1):
        self.ParentWorld = parentworld
        self._HitPoints = self.HitPointsMax = hp
        self.Name = name
        self.BodyType = body_type
        self.Location: gamespace.Space = None
        self.FOV_Default = 1
        self.TimeLastMoved = 0

    def attemptMove(self, shift: (int, int)) -> bool:
        new_space = self.Location + shift
        new_space = self.ParentWorld.Map[new_space.Y][new_space.X]
        if not self.ParentWorld.isSpaceValid(new_space):
            return False
        else:
            self.Location = new_space
            map_space = self.ParentWorld.Map[self.Location.Y][self.Location.X]
            if isinstance(map_space, gamespace.Wilds):
                map_space.runEvent(pc=self)
            return True

    @property
    def HitPoints(self):
        return self._HitPoints

    @HitPoints.setter
    def HitPoints(self, value):
        self._HitPoints = min(max(value, 0), self.HitPointsMax)
        if self._HitPoints == 0:
            self.onDeath()

    @property
    def isDead(self) -> bool:
        return self.HitPoints <= 0

    def onDeath(self):
        pass


class NPC(Actor):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.Inventory: [] = []
        self.FlavorText = ""


class Enemy(NPC):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.BaseAttack: int = 0
        self.Abilities: {} = {}
        self.Loot: [] = []


class PlayerClass:
    def __init__(self, name=None, hitpoints_max=1):
        self.Name: str = name
        self.HitPointsMaxBase = hitpoints_max

    def __str__(self):
        return self.Name


class WandererClass(PlayerClass):
    """ Default player class with nothing special. """

    def __init__(self, *args, **kwargs):
        super().__init__(*args, hitpoints_max=50, **kwargs)
        self.Name = "Wanderer"


class PlayerCharacter(Actor):

    def __init__(self, user_id, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.UserId: str = user_id
        if self.Name is None:
            self.Name: str = "Unnamed"
        self.Class: PlayerClass = WandererClass()
        self._HitPoints = self.HitPointsMax = self.Class.HitPointsMaxBase
        self.EquipmentSet: items.EquipmentSet = items.EquipmentSet()
        self.FOV: int = self.FOV_Default
        self.Inventory: [items.Equipment] = []
        self.Currency: int = 1000

    @property
    def weapon(self):
        w = self.EquipmentSet.MainHand
        if not isinstance(w, weapons.Weapon):
            return None
        else:
            return w

    @property
    def hasWeaponEquiped(self):
        return self.weapon is not None

    def equip(self, equipment):
        self.EquipmentSet.equip(equipment)
        equipment.onEquip(self)

    def unequip(self, equipment):
        self.EquipmentSet.unequip(equipment)
        equipment.onUnequip(self)

    def take_damage(self, damage: int):
        damage -= self.EquipmentSet.ArmorCount
        self.HitPoints -= damage  # TODO Finish this

    def onDeath(self):
        self.ParentWorld.handlePlayerDeath(self.UserId)
