from gamelogic import items, gamespace


class BodyType:
    Humanoid = 1
    SmallAnimal = 2
    LargeAnimal = 3
    Monstrosity = 4
    Mechanical = 5


class Actor:
    HitPoints: int = 0
    Name: str = ""
    BodyType: int = None
    Location = None
    ParentWorld = None

    def __init__(self, parentworld, hp: int = 0, name: str = "", body_type: int = 1):
        self.ParentWorld = parentworld
        self.HitPoints = hp
        self.Name = name
        self.BodyType = body_type

    def attemptMove(self, shift: (int, int)):
        new_space = self.Location + shift
        if new_space.X < 0 or new_space.Y < 0 or new_space.X > self.ParentWorld.Width - 1 or new_space.Y > self.ParentWorld.Height - 1:
            return False
        else:
            self.Location = new_space
            return True


class NPC(Actor):
    Inventory: [] = []
    FlavorText = ""


class Enemy(NPC):
    BaseAttack: int = 0
    Abilities: {} = {}
    Loot: [] = []


class PlayerClass:
    Name: str = None

    def __str__(self):
        return self.Name


class WandererClass(PlayerClass):
    """ Default player class with nothing special. """
    Name = "Wanderer"
    HitPointsMaxBase = 50


class PlayerCharacter(Actor):
    UserId: str = None
    Name: str = None
    Class: PlayerClass = WandererClass()
    HitPoints: int = WandererClass.HitPointsMaxBase
    HitPointsMax: int = WandererClass.HitPointsMaxBase
    EquipmentSet: items.EquipmentSet = items.EquipmentSet()

    def __init__(self, user_id, *args, **kwargs):
        self.UserId = user_id
        super().__init__(*args, **kwargs)
