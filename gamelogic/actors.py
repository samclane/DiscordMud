from gamelogic import items, gamespace


class BodyType:
    Humanoid = 1
    SmallAnimal = 2
    LargeAnimal = 3
    Monstrosity = 4
    Mechanical = 5


class Actor:

    def __init__(self, parentworld, hp: int = 0, name: str = "", body_type: int = 1):
        self.ParentWorld = parentworld
        self.HitPoints = hp
        self.Name = name
        self.BodyType = body_type
        self.Location = None

    def attemptMove(self, shift: (int, int)):
        new_space = self.Location + shift
        if new_space.X < 0 or new_space.Y < 0 or new_space.X > self.ParentWorld.Width - 1 or new_space.Y > self.ParentWorld.Height - 1:
            return False
        else:
            self.Location = new_space
            map_space = self.ParentWorld.Map[self.Location.Y][self.Location.X]
            if isinstance(map_space, gamespace.Wilds):
                map_space.runEvent(pc=self)
            return True


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
    def __init__(self, name=None):
        self.Name: str = name

    def __str__(self):
        return self.Name


class WandererClass(PlayerClass):
    """ Default player class with nothing special. """

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.Name = "Wanderer"
        self.HitPointsMaxBase = 50


class PlayerCharacter(Actor):

    def __init__(self, user_id, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.UserId: str = user_id
        self.Name: str = "Unnamed"
        self.Class: PlayerClass = WandererClass()
        self.HitPoints = self.HitPointsMax = self.Class.HitPointsMaxBase
        self.EquipmentSet: items.EquipmentSet = items.EquipmentSet()
