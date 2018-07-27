import uuid


class Event:

    def __init__(self, probability: float, flavor: str):
        self.Probability: float = probability
        self.Uid: str = str(uuid.uuid4())
        self.FlavorText: str = flavor

    def run(self, pc):
        print("Error: Tried to run a generic event or class didn't implement run. Please use an event subclass.")


class CombatEvent(Event):

    def __init__(self, probability: float, flavor: str, enemies: list, conditions=None):
        super().__init__(probability, flavor)
        self.Enemies: [] = enemies
        self.SpecialConditions: [] = conditions

    def run(self, pc):
        print("We're in combat!")


class EncounterEvent(Event):

    def __init__(self, probability: float, flavor: str, choices_dict: dict, npc=None):
        super().__init__(probability, flavor)
        self.ChoiceDict = choices_dict
        self.NPCInvolved = npc

    def run(self, pc):
        print("Ahh, encounter!")
        if self.FlavorText:
            print(self.FlavorText)


class MerchantEvent(Event):

    def __init__(self, probability, flavor, items):
        super().__init__(probability, flavor)
        self.Items: {} = items

    def run(self, pc):
        print("Merchant encountered!")
