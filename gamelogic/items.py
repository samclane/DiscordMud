class Equipment:
    Name: str
    WeightLb: float
    BaseValue: int

    def __init__(self, name: str = "Empty", weightlb: float = 0, base_value: int = 0):
        self.Name = name
        self.WeightLb = weightlb
        self.BaseValue = base_value
        self.isEquipped = False

    def __str__(self):
        return self.Name

    def onEquip(self, player_character):
        self.isEquipped = True

    def onUnequip(self, player_character):
        self.isEquipped = False


class Armor(Equipment):
    ArmorCount: int

    def __init__(self, armor_count=0, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.ArmorCount = armor_count

    def activateUtility(self, player_character):
        pass


class HeadArmor(Armor):
    Name: str = "Head"


class ChestArmor(Armor):
    Name: str = "Chest"


class LegArmor(Armor):
    Name: str = "Legs"


class FootArmor(Armor):
    Name: str = "Feet"


class MainHandEquipment(Equipment):
    Name: str = "Main Hand"


class OffHandEquipment(Equipment):
    Name: str = "Off Hand"


class EquipmentSet:
    Head: HeadArmor
    Chest: ChestArmor
    Legs: LegArmor
    Feet: FootArmor
    MainHand: MainHandEquipment
    OffHand: OffHandEquipment

    def __init__(self):
        self.Head = HeadArmor()
        self.Chest = ChestArmor()
        self.Legs = LegArmor()
        self.Feet = FootArmor()
        self.MainHand = MainHandEquipment()
        self.OffHand = OffHandEquipment()

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

    def __iter__(self):
        yield self.Head
        yield self.Chest
        yield self.Legs
        yield self.Feet
        yield self.MainHand
        yield self.OffHand

    @property
    def ArmorSet(self) -> [Armor]:
        armorlist = [self.Head,
                     self.Chest,
                     self.Legs,
                     self.Feet]
        if hasattr(self.MainHand, 'ArmorCount'):
            armorlist.append(self.MainHand)
        if hasattr(self.OffHand, 'ArmorCount'):
            armorlist.append(self.OffHand)
        return armorlist

    @property
    def ArmorCount(self) -> int:
        return sum([armor.ArmorCount for armor in self.ArmorSet])

    def equip(self, equipment):
        if isinstance(equipment, HeadArmor):
            self.Head = equipment
        if isinstance(equipment, ChestArmor):
            self.Chest = equipment
        if isinstance(equipment, LegArmor):
            self.Legs = equipment
        if isinstance(equipment, FootArmor):
            self.Feet = equipment
        if isinstance(equipment, MainHandEquipment):
            self.MainHand = equipment
        if isinstance(equipment, OffHandEquipment):
            self.OffHand = equipment
        else:
            raise ValueError("Equipment was not of recognized type.")

    def unequip(self, equipment):
        if isinstance(equipment, HeadArmor):
            self.Head = HeadArmor()
        if isinstance(equipment, ChestArmor):
            self.Chest = ChestArmor()
        if isinstance(equipment, LegArmor):
            self.Legs = LegArmor()
        if isinstance(equipment, FootArmor):
            self.Feet = FootArmor()
        if isinstance(equipment, MainHandEquipment):
            self.MainHand = MainHandEquipment()
        if isinstance(equipment, OffHandEquipment):
            self.OffHand = OffHandEquipment()
        else:
            raise ValueError("Equipment was not of recognized type.")


class Store:
    Inventory: [Equipment]
    PriceRatio: float  # Lower means better buy/sell prices, higher means worse

    def __init__(self, inventory=None):
        self.Inventory = inventory if inventory else []
        self.PriceRatio = 1.0

    def getPrice(self, item: Equipment) -> float:
        return item.BaseValue * self.PriceRatio

    def sellItem(self, index: int, player_character) -> bool:
        item = self.Inventory[index]
        price = self.getPrice(item)
        if player_character.Currency < price:
            return False
        self.Inventory.remove(item)
        player_character.Currency -= price
        player_character.Inventory.add(item)
        return True

    def buyItem(self, item: Equipment) -> float:
        self.Inventory.append(item)
        return item.BaseValue / self.PriceRatio
