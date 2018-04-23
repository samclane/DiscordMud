import uuid

import npc


class Event:
    Uid: str = None
    Probability = 0.0
    FlavorText: str = ""

    def __init__(self, probability: float, flavor: str):
        self.Probability = probability
        self.Uid = str(uuid.uuid4())
        if flavor:
            self.FlavorText = flavor

    def run(self, pc):
        print("Error: Tried to run a generic event or class didn't implement run. Please use an event subclass.")


class CombatEvent(Event):
    Enemies: [] = []
    SpecialConditions: [] = []

    def __init__(self, probability: float, flavor: str, enemies: list, conditions=None):
        super().__init__(probability, flavor)
        self.Enemies = enemies
        self.SpecialConditions = conditions

    def run(self, pc):
        print("Ahhh, we're in combat!")


class EncounterEvent(Event):
    Choices: [] = []
    Outcomes: {} = {}
    NPCInvolved: npc.NPC = None

    def __init__(self, probability: float, flavor: str, choices_dict: dict, npc: npc.NPC = None):
        super().__init__(probability, flavor)
        self.ChoiceDict = choices_dict
        self.NPCInvolved = npc

    def run(self, pc):
        print("Ahh, encounter!")
        if self.FlavorText:
            print(self.FlavorText)


class MerchantEvent(Event):
    Items: {} = {}

    def __init__(self, probability, flavor, items):
        super().__init__(probability, flavor)
        self.Items = items

    def run(self, pc):
        print("Ahhh, merchant!")
