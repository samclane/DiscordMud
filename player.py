import items


class PlayerClass:
    Name: str = None

    def __str__(self):
        return self.Name


class WandererClass(PlayerClass):
    """ Default player class with nothing special. """
    Name = "Wanderer"
    HitPointsMaxBase = 50


class PlayerCharacter:
    UserId: str = None
    Name: str = None
    Class: PlayerClass = WandererClass()
    HitPoints: int = WandererClass.HitPointsMaxBase
    HitPointsMax: int = WandererClass.HitPointsMaxBase
    EquipmentSet: items.EquipmentSet = items.EquipmentSet()

    def __init__(self, user_id=None):
        self.UserId = user_id
