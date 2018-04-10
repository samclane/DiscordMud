from enum import Enum

import numpy

import events


class Space:
    X = None
    Y = None

    def __init__(self, x, y):
        self.X = x
        self.Y = y

    def __str__(self):
        return "({}, {})".format(self.X, self.Y)

    def __eq__(self, other):
        return self.X == other.X and self.Y == other.Y

    def __add__(self, other):
        return Space(self.X + other.X, self.Y + other.Y)

    def __hash__(self):
        return self.X + 100 * self.Y


class IndustryType(Enum):
    Mining = 1
    Farming = 2
    Smithing = 3
    Woodworking = 4


class CardinalDirection(Enum):
    NORTH = 0
    SOUTH = 1
    EAST = 2
    WEST = 3


class Town(Space):
    Name: str = None
    Population: int = 0
    Industry: IndustryType = None

    def __init__(self, x, y, name, population, industry=None):
        super(Town, self).__init__(x, y)
        self.Name = name
        self.Population = population
        self.Industry = industry


class Wilds(Space):
    Name: str = None
    Events: [] = []

    def __init__(self, x, y, name):
        super(Wilds, self).__init__(x, y)
        self.Name = name
        self.null_event = events.Event(1.0, "Null Event")
        self.Events.append(self.null_event)

    def addEvent(self, event):
        self.Events.append(event)
        self.null_event.Probability -= event.Probability

    def runEvent(self, pc):
        n = 1
        result = numpy.random.choice(self.Events, size=n, p=[event.Probability for event in self.Events])[0]
        result.run(pc)


class World:
    Width = 0
    Height = 0
    Map = [[Space(x, y) for x in range(Width)] for y in range(Height)]
    Towns = []
    Wilds = []
    Users = {}
    StartingTown: Town = None

    def __init__(self, width, height):
        self.Width = width
        self.Height = height
        self.Map = [[Space(x, y) for x in range(width)] for y in range(height)]

    def addTown(self, town: Town, isStartingTown=False):
        self.Towns.append(town)
        self.Map[town.Y][town.X] = town
        if isStartingTown:
            self.StartingTown = town

    def addWilds(self, wilds: Wilds):
        self.Wilds.append(wilds)
        self.Map[wilds.Y][wilds.X] = wilds
