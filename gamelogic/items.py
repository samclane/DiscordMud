class Equipment:

    def __init__(self, name="Empty", type_="None", weight=0, base_value=0):
        self.Name = name
        self.Type = type_
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
    def __init__(self):
        self.Head: HeadEquipment = HeadEquipment()
        self.Chest: ChestEquipment = ChestEquipment()
        self.Legs: LegsEquipment = LegsEquipment()
        self.Feet: FeetEquipment = FeetEquipment()
        self.MainHand: MainHandEquipment = MainHandEquipment()
        self.OffHand: OffHandEquipment = OffHandEquipment()

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
