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


class Store:
    Inventory: [Equipment]
    PriceRatio: float  # Lower means better buy/sell prices, higher means worse

    def __init__(self):
        self.Inventory = []
        self.PriceRatio = 1.0

    def getPrice(self, item: Equipment) -> float:
        return item.BaseValue * self.PriceRatio

    def sellItem(self, index: int, player_character) -> bool:
        item = self.Inventory[index]
        price = self.getPrice(item)
        if player_character.Currency < price:
            return False
        self.Inventory.remove(item)
        player_character -= price
        return True

    def buyItem(self, item: Equipment) -> float:
        self.Inventory.append(item)
        return item.BaseValue / self.PriceRatio

    def formatInventory(self) -> str:
        msg = ""
        for idx, item in enumerate(self.Inventory):
            msg += "{}\t{}\t{}\n".format(idx,
                                         item.Name,
                                         item.BaseValue * self.PriceRatio)
        if len(self.Inventory) == 0:
            msg += "There are no items in the store at the moment. Please try again later."
        return msg
