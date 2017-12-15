import npc


class Event:
    Type: EventType = None
    FlavorText: str = ""

    def __init__(self, type: EventType):
        self.Type = type


class EventType:
    pass


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
