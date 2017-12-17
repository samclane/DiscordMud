import items

class PlayerClass:
    Name: str = None


class WandererClass(PlayerClass):
    Name = "Wanderer"


class PlayerCharacter:
    Name: str = None
    Class: PlayerClass = None
    HitPoints: int = None
    EquipmentSet: items.EquipmentSet = None

    def __init__(self):
        pass