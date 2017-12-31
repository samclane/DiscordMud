from enum import Enum


class Space:
    X = None
    Y = None

    def __init__(self, x, y):
        self.X = x
        self.Y = y


class IndustryType(Enum):
    Mining = 1
    Farming = 2
    Smithing = 3
    Woodworking = 4


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

    def __init__(self, x, y, name, events):
        super().__init__(x, y)
        self.Name = name
        self.Events = events


class World:
    Width = 0
    Height = 0
    Map = [[Space(x, y) for x in range(Width)] for y in range(Height)]
    Towns = set()
    Wilds = set()

    def __init__(self, width, height):
        self.Width = width
        self.Height = height
        self.Map = [[Space(x, y) for x in range(width)] for y in range(height)]

    def addTown(self, town: Town):
        self.Towns.add(town)
        self.Map[town.X][town.Y] = town

    def addWilds(self, wilds: Wilds):
        self.Wilds.add(wilds)
        self.Map[wilds.X][wilds.Y] = Wilds

