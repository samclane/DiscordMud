class Equipment:
    Name: str = "Empty"
    Type: str = "None"
    Weight: int = 0
    BaseValue: int = 0

    def __init__(self, name, weight, base_value):
        self.Name = name
        self.Weight = weight
        self.BaseValue = base_value


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
    Head: HeadEquipment = HeadEquipment
    Chest: ChestEquipment = ChestEquipment
    Legs: LegsEquipment = LegsEquipment
    Feet: FeetEquipment = FeetEquipment
    MainHand: MainHandEquipment = MainHandEquipment
    OffHand: OffHandEquipment = OffHandEquipment

    def __str__(self):
        return "Head: {}\r\n" \
               "Chest: {}\r\n" \
               "Legs: {}\r\n" \
               "Feet: {}\r\n" \
               "MainHand: {}\r\n" \
               "OffHand: {}\r\n".format(
            self.Head.Name,
            self.Chest.Name,
            self.Legs.Name,
            self.Feet.Name,
            self.MainHand.Name,
            self.OffHand.Name
        )
