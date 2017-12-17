class Equipment:
    Name: str = None
    Type: str = None
    Weight: int = None
    BaseValue: int = None


class HeadEquipment(Equipment):
    Type = "Head"


class ChestEquipment(Equipment):
    Type = "Chest"


class LegsEquipment(Equipment):
    Type = "Legs"


class FeetEquipment(Equipment):
    Type = "Feet"


class MainHandEquipment(Equipment):
    Type = "Main Hand"


class OffHandEquipment(Equipment):
    Type = "Off Hand"


class EquipmentSet:
    Head: HeadEquipment = None
    Chest: ChestEquipment = None
    Legs: LegsEquipment = None
    Feet: FeetEquipment = None
    MainHand: MainHandEquipment = None
    OffHand: OffHandEquipment = None

    def __str__(self):
        return "Head: {}\r\n" \
               "Chest: {}\r\n" \
               "Legs: {}\r\n" \
               "Feet: {}\r\n" \
               "MainHand: {}\r\n" \
               "OffHand: {}\r\n"
