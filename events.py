import uuid

import npc


class Event:
    Uid: str = None
    Probability = 0.0
    FlavorText: str = ""

    def __init__(self, probability, flavor):
        self.Probability = probability
        self.Uid = str(uuid.uuid4())
        if flavor:
            self.FlavorText = flavor

    def run(self, pc):
        print("Error: Tried to run a generic event or class didn't implement run. Please use an event subclass.")


class CombatEvent(Event):
    Enemies: [] = []
    SpecialConditions: [] = []

    def __init__(self, probability, flavor, enemies, conditions=None):
        super().__init__(probability, flavor)
        self.Enemies = enemies
        self.SpecialConditions = conditions

    def run(self, pc):
        print("Ahhh, we're in combat!")


class EncounterEvent(Event):
    Choices: [] = []
    Outcomes: {} = {}
    NPCInvolved: npc.NPC = None

    def __init__(self, probability, flavor, choices_dict, npc=None):
        super().__init__(probability, flavor)
        self.ChoiceDict = choices_dict
        self.NPCInvolved = npc

    def run(self, pc):
        print("Ahh, encounter!")


class MerchantEvent(Event):
    Items: {} = {}

    def __init__(self, probability, flavor, items):
        super().__init__(probability, flavor)
        self.Items = items

    def run(self, pc):
        print("Ahhh, merchant!")
