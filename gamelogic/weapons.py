from gamelogic.items import Equipment


# Remember: def func(a, b, kw1=None, *args, **kwargs):


class ProjectileType:
    Thrown = 0
    Bullet = 1
    Rocket = 2


class Caliber:
    BB = 0
    MM_9 = 1


class Weapon(Equipment):
    BaseDamage: int

    def __init__(self, base_damage, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if base_damage < 0:
            raise ValueError("base_damage must be 0 or greater.")
        self.BaseDamage = base_damage


class RangedWeapon(Weapon):
    Range: int

    def __init__(self, range_=1, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if range_ < 1:
            raise ValueError("Range must be 1 or greater.")
        self.Range = range_


class ProjectileWeapon(RangedWeapon):
    AmmoType: int
    Capacity: int

    def __init__(self, projectile_type, capacity=1, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.AmmoType = projectile_type
        if capacity < 1:
            raise ValueError("Capacity must be 1 or greater.")
        self.Capacity = capacity
        self._currentCapacity = capacity

    @property
    def isSingleShot(self) -> bool:
        return self.Capacity == 1

    @property
    def currentCapacity(self) -> int:
        return self._currentCapacity

    @property
    def isEmpty(self) -> bool:
        return self.currentCapacity == 0

    def fire(self):
        self._currentCapacity -= 1

    def reload(self):
        self._currentCapacity = self.Capacity


class Firearm(ProjectileWeapon):
    Caliber: int

    def __init__(self, caliber, burst_size=1, *args, **kwargs):
        super().__init__(ProjectileType.Bullet, *args, **kwargs)
        self.Caliber = caliber
        self.BurstSize = burst_size

    def fire(self):
        self._currentCapacity -= self.BurstSize


class Pistol(Firearm):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)


class MeleeWeapon(Weapon):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)


class BladedWeapon(MeleeWeapon):
    BleedChance: float
    BleedFactor: float

    def __init__(self, bleed_chance: float, bleed_factor: float, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.BleedChance = bleed_chance
        self.BleedFactor = bleed_factor


class BluntWeapon(MeleeWeapon):
    CrippleChance: float

    def __init__(self, cripple_chance: float, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.CrippleChance = cripple_chance
