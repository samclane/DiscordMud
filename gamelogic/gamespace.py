import numpy

from gamelogic import events, actors


class Space:

    def __init__(self, x, y):
        self.X = x
        self.Y = y

    def __str__(self):
        return "({}, {})".format(self.X, self.Y)

    def __eq__(self, other):
        return self.X == other.X and self.Y == other.Y

    def __add__(self, other):
        if isinstance(other, Space):
            return Space(self.X + other.X, self.Y + other.Y)
        else:
            return Space(self.X + other[0], self.Y + other[1])

    def __hash__(self):
        return self.X + 100 * self.Y


class IndustryType(object):
    Name = "Null"


class MiningIndustry(IndustryType):
    Name = "Mining"


class FarmingIndustry(IndustryType):
    Name = "Farming"


class SmithingIndustry(IndustryType):
    Name = "Smithing"


class WoodworkingInudstry(IndustryType):
    Name = "Woodworking"


class Town(Space):

    def __init__(self, x, y, name, population, industry=None):
        super(Town, self).__init__(x, y)
        self.Name = name
        self.Population = population
        self.Industry = industry


class Wilds(Space):

    def __init__(self, x, y, name):
        super(Wilds, self).__init__(x, y)
        self.Name = name
        self.null_event = events.Event(1.0, "Null Event")
        self.Events = []
        self.Events.append(self.null_event)

    def addEvent(self, event: events.Event):
        self.Events.append(event)
        self.null_event.Probability -= event.Probability

    def runEvent(self, pc):
        n = 1
        result = numpy.random.choice(self.Events, size=n, p=[event.Probability for event in self.Events])[0]
        result.run(pc)


class World:

    def __init__(self, name: str, width: int, height: int):
        self.Name = name
        self.Width = width
        self.Height = height
        self.Map = [[Space(x, y) for x in range(width)] for y in range(height)]
        self.Towns = []
        self.Wilds = []
        self.Users = []
        self.StartingTown: Town = None

    def addTown(self, town: Town, isStartingTown=False):
        self.Towns.append(town)
        self.Map[town.Y][town.X] = town
        if isStartingTown:
            self.StartingTown = town

    def addWilds(self, wilds: Wilds):
        self.Wilds.append(wilds)
        self.Map[wilds.Y][wilds.X] = wilds

    def addActor(self, actor, space=None):
        if isinstance(actor, actors.PlayerCharacter):
            actor.Location = self.StartingTown
            self.Users.append(actor)
        elif space and (0 < space.X < self.Width - 1) and (0 < space.Y < self.Height - 1):
            actor.Location = space
