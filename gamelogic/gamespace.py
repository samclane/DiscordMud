import random
from itertools import product
from math import sqrt

import numpy
from noise import pnoise3

from gamelogic import events, actors, items


class Terrain:
    id: int = 0
    isWalkable: bool = False

    def __str__(self):
        return self.__class__.__name__

    def __repr__(self):
        return str(self)


class SandTerrain(Terrain):
    id = 1
    isWalkable = True


class GrassTerrain(Terrain):
    id = 2
    isWalkable = True


class WaterTerrain(Terrain):
    id = 3
    isWalkable = False


class MountainTerrain(Terrain):
    id = 4
    isWalkable = True


class Space:
    X: int
    Y: int
    Terrain: Terrain

    def __init__(self, x: int, y: int, terrain: Terrain = Terrain()):
        self.X = x
        self.Y = y
        self.Terrain = terrain

    def __str__(self):
        return "({}, {})".format(self.X, self.Y)

    def __repr__(self):
        return str((self.X, self.Y, self.Terrain))

    def __eq__(self, other):
        return self.X == other.X and self.Y == other.Y

    def __add__(self, other) -> 'Space':
        if isinstance(other, Space):
            return Space(self.X + other.X, self.Y + other.Y, other.Terrain)
        else:
            return Space(self.X + int(other[0]), self.Y + int(other[1]), Terrain())

    def __iter__(self):
        yield self.X
        yield self.Y

    def __getitem__(self, item) -> int:
        if item == 0:
            return self.X
        if item == 1:
            return self.Y
        raise ValueError("Item should be either 0 or 1")

    def distance(self, other) -> float:
        if isinstance(other, Space):
            return sqrt(abs(self.X - other.X) ** 2 + abs(self.Y - other.Y) ** 2)
        else:
            return sqrt(abs(self.X - other[0]) ** 2 + abs(self.Y - other[1]) ** 2)


class IndustryType:
    Name: str = "Null"


class MiningIndustry(IndustryType):
    Name = "Mining"


class FarmingIndustry(IndustryType):
    Name = "Farming"


class SmithingIndustry(IndustryType):
    Name = "Smithing"


class WoodworkingIndustry(IndustryType):
    Name = "Woodworking"


class Town(Space):
    Name: str
    Population: int
    Industry: IndustryType

    def __init__(self, x, y, name, population, industry=None, terrain=None):
        super(Town, self).__init__(x, y)
        self.Name = name
        self.Population = population
        self.Industry = industry
        self.Terrain = terrain
        self.Store = items.Store()
        self.Underwater = isinstance(self.Terrain, WaterTerrain)

    def innEvent(self, pc) -> str:
        pc.HitPoints = pc.HitPointsMax
        return "Your hitpoints have been restored, {}".format(pc.Name)


class Wilds(Space):
    Name: str
    null_event: events.Event
    Events: list

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
    Name: str
    Width: int
    Height: int
    Map: [[Space]]

    def __init__(self, name: str, width: int, height: int):
        self.Name = name
        self.Width = width
        self.Height = height
        self.Map = [[Space(x, y, Terrain()) for x in range(width)] for y in
                    range(height)]
        self.Towns = []
        self.Wilds = []
        self.Players = []
        self.StartingTown: Town = None
        self.generateMap()

    def generateMap(self):
        resolution = 0.2 * (
                (self.Width + self.Height) / 2)  # I pulled this out of my butt. Gives us decently scaled noise.
        sand_slice = random.random()
        mountain_slice = random.random()
        water_threshold = .1  # Higher water-factor -> more water on map
        mountain_threshold = .7  # Lower mountain_thresh -> less mountains
        for x in range(self.Width):
            for y in range(self.Height):
                # Land and water pass
                self.Map[y][x] = Space(x, y, SandTerrain() if abs(
                    pnoise3(x / resolution, y / resolution, sand_slice)) > water_threshold else WaterTerrain())

                # Mountains pass
                if abs(pnoise3(x / resolution, y / resolution, mountain_slice)) > mountain_threshold and self.Map[y][
                    x].Terrain.isWalkable:
                    self.Map[y][x] = Space(x, y, MountainTerrain())

    def isSpaceValid(self, space: (int, int)) -> bool:
        return (0 < space.X < self.Width - 1) and (0 < space.Y < self.Height - 1) and space.Terrain.isWalkable

    def getAdjacentSpaces(self, space, sq_range: int = 1) -> [Space]:
        fov = list(range(-sq_range, sq_range + 1))
        steps = product(fov, repeat=2)
        coords = (tuple(c + d for c, d in zip(space, delta)) for delta in steps)
        return [self.Map[j][i] for i, j in coords if (0 <= i < self.Width) and (0 <= j < self.Height)]

    def addTown(self, town: Town, isStartingTown=False):
        self.Towns.append(town)
        town.Terrain = self.Map[town.Y][town.X].Terrain
        self.Map[town.Y][town.X] = town
        if isStartingTown:
            self.StartingTown = town

    def addWilds(self, wilds: Wilds):
        self.Wilds.append(wilds)
        wilds.Terrain = self.Map[wilds.Y][wilds.X].Terrain
        self.Map[wilds.Y][wilds.X] = wilds

    def addActor(self, actor, space=None):
        if isinstance(actor, actors.PlayerCharacter):
            actor.Location = self.StartingTown
            self.Players.append(actor)
        elif space and self.isSpaceValid(space):
            actor.Location = space
