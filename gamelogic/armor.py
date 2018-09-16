from gamelogic.items import Armor, HeadArmor, ChestArmor, LegArmor, FootArmor, MainHandEquipment, OffHandEquipment, \
    FullyImplemented
from random import random


class Helmet(HeadArmor):
    def __init__(self, coverage: float = 0., *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.Coverage = coverage  # Pct. of head the helmet covers. [0, 1]

    @property
    def ArmorCount(self):
        # Determine if the bullet hits or misses
        return self._ArmorCount if random.random() <= self.Coverage else 0

    @ArmorCount.setter
    def ArmorCount(self, val):
        self._ArmorCount = val


class SSh68(Helmet, FullyImplemented):
    """
    Based on the Soviet SSh-68 helmet
    """
    Name: str = "SSh-68"

    def __init__(self):
        super().__init__(coverage=.50,
                         armor_count=1,
                         name=self.Name,
                         weightlb=3.31)


ImplementedArmorList: list = FullyImplemented.__subclasses__()

ImplementedArmorDict: dict = {cls.Name: cls for cls in FullyImplemented.__subclasses__()}
