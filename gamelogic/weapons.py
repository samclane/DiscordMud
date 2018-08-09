from gamelogic.items import Equipment


# Remember: def func(a, b, kw1=None, *args, **kwargs):


class ProjectileType:
    Thrown = 0
    Bullet = 1
    Rocket = 2


class Caliber:
    BB = 0
    MM_9 = 1  # Pistol & SMG
    MM_762 = 2  # AK47
    IN_577 = 3  # Rifles


class FiringAction:
    SingleShot = 0
    BoltAction = 1
    SemiAutomatic = 2
    BurstFireOnly = 3
    FullyAutomatic = 4


class Weapon(Equipment):
    _baseDamage: int

    def __init__(self, base_damage: int, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if base_damage < 0:
            raise ValueError("base_damage must be 0 or greater.")
        self._baseDamage = base_damage

    @property
    def damage(self):
        return self._baseDamage


class RangedWeapon(Weapon):
    Range: int

    def __init__(self, range_: int = 1, range_falloff=1, *args, **kwargs):
        """
        Any weapon that can strike >1 squares away from the player.

        :param range_: Number of squares away that can be targeted.
        :param range_falloff: Percent of damage that is lost per-square away
        :param args: Weapon args
        :param kwargs: Weapon kwargs
        """
        super().__init__(*args, **kwargs)
        if range_ < 1:
            raise ValueError("Range must be 1 or greater.")
        self.Range = range_
        if not (0 <= range_falloff <= 1):
            raise ValueError("RangeFalloff must be between 0 and 1")
        self.RangeFalloff = range_falloff

    def calcDamage(self, distance: int) -> int:
        damage = self.damage * (distance * (1 - self.RangeFalloff))
        return int(damage)


class ProjectileWeapon(RangedWeapon):
    AmmoType: int
    Capacity: int

    def __init__(self, projectile_type: int, capacity: int = 1, *args, **kwargs):
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
    Action: int
    BurstSize: int

    def __init__(self, caliber: int, action=FiringAction.SingleShot, burst_size=1, *args, **kwargs):
        super().__init__(ProjectileType.Bullet, *args, **kwargs)
        self.Caliber = caliber
        self.Action = action
        if self.Action < FiringAction.BurstFireOnly and burst_size > 1:
            raise ValueError("Firing action must be BurstFireOnly or FullyAutomatic to have a burst > 1")
        if self.isSingleShot:
            self.Action = FiringAction.SingleShot
        self.BurstSize = burst_size

    def fire(self):
        self._currentCapacity -= self.BurstSize

    @property
    def damage(self):
        return super().damage * self.BurstSize


class Pistol(Firearm):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)


class Rifle(Firearm):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)


class Shotgun(Firearm):
    PelletCount: int

    def __init__(self, pellet_count: int = 2, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if pellet_count < 2:
            raise ValueError("Must have at least 2 pellets per shot.")
        self.PelletCount = pellet_count

    @property
    def damage(self):
        return super().damage * self.PelletCount


class MeleeWeapon(Weapon):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)


class BladedWeapon(MeleeWeapon):
    BleedChance: float
    BleedFactor: float

    def __init__(self, bleed_chance: float, bleed_factor: float, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if not (0 <= bleed_chance <= 1):
            raise ValueError("BleedChance must be between 0 and 1.")
        self.BleedChance = bleed_chance
        if not (0 <= bleed_factor <= 1):
            raise ValueError("BleedFactor must be between 0 and 1.")
        self.BleedFactor = bleed_factor


class Knife(BladedWeapon):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)


class Machete(BladedWeapon):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)


class BluntWeapon(MeleeWeapon):
    CrippleChance: float

    def __init__(self, cripple_chance: float, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if not (0 <= cripple_chance <= 1):
            raise ValueError("CrippleChance must be between 0 and 1.")
        self.CrippleChance = cripple_chance


class Hammer(BluntWeapon):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
