from enum import Enum


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
        super().__init__(x, y)
        self.Name = name
        self.Population = population
        self.Industry = industry


class Wilds(Space):
    Name: str = None
    Events: [] = []

    def __init__(self, x, y, name):
        super().__init__(x, y)
        self.Name = name


class World:
    Width = 0
    Height = 0
    Map = [[Space(x, y) for x in range(Width)] for y in range(Height)]
    Towns = []
    Wilds = []

    def __init__(self, width, height):
        self.Width = width
        self.Height = height
        self.Map = [[Space(x, y) for x in range(width)] for y in range(height)]

    def addTown(self, town: Town):
        self.Towns.append(town)
        self.Map[town.X][town.Y] = town

    def addWilds(self, wilds: Wilds):
        self.Wilds.append(wilds)
        self.Map[wilds.X][wilds.Y] = wilds


