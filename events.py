import uuid

import npc


class EventType:
    pass


class Event:
    Uid: str = None
    Type: EventType = None
    Probability = 0.0
    FlavorText: str = ""

    def __init__(self, e_type: EventType, probability, flavor: str = None):
        self.Type = e_type
        self.Probability = probability
        self.Uid = str(uuid.uuid4())
        if flavor:
            self.FlavorText = flavor


class CombatEvent(EventType):
    Enemies: [] = []
    SpecialConditions: [] = []

    def __init__(self, enemies, conditions=None):
        self.Enemies = enemies
        self.SpecialConditions = conditions


class EncounterEvent(EventType):
    Choices: [] = []
    Outcomes: {} = {}
    NPCInvolved: npc.NPC = None

    def __init__(self, choices, outcomes, npc=None):
        self.Choices = choices
        self.Outcomes = outcomes
        self.NPCInvolved = npc


class MerchantEvent(EventType):
    Items: {} = {}

    def __init__(self, items):
        self.Items = items
