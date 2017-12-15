from enum import Enum


class NPC:
    HP: int = 0
    Name: str = ""
    BodyType: BodyType = None
    Inventory: [] = []
    FlavorText = ""

    def __init__(self, hp: int, name: str, body_type: BodyType):
        self.HP = hp
        self.Name = name
        self.BodyType = body_type


class BodyType(Enum):
    Humanoid = 1
    SmallAnimal = 2
    LargeAnimal = 3
    Monstrosity = 4
    Mechanical = 5


class Enemy(NPC):
    BaseAttack: int = 0
    Abilities: {} = {}
    Loot: [] = []
