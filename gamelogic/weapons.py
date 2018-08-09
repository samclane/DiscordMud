from gamelogic.items import Equipment


class ProjectileType:
    Thrown = 0
    Bullet = 1
    Rocket = 2
    Grenade = 3
    Other = 4


class Caliber:
    BB = 0
    MM_9 = IN_38 = 1  # Pistol & SMG
    MM_762 = 2  # AK47
    IN_577 = 3  # Rifles
    IN_45 = 4


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

    def __init__(self, range_: int = 1, range_falloff: float = 1., *args, **kwargs):
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
        self._rangeFalloff = range_falloff

    def calcDamage(self, distance: int) -> int:
        damage = self.damage * (distance * (1 - self.RangeFalloff))
        return int(damage)

    @property
    def RangeFalloff(self) -> float:
        return self._rangeFalloff

    @RangeFalloff.setter
    def RangeFalloff(self, val: float):
        val = min(max(val, 0), 1)  # Clamp val between 0 and 1
        self._rangeFalloff = val


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
    _action: int
    BurstSize: int

    def __init__(self, caliber: int, action=FiringAction.SingleShot, burst_size=1, *args, **kwargs):
        super().__init__(ProjectileType.Bullet, *args, **kwargs)
        self.Caliber = caliber
        self._action = action
        if self.Action < FiringAction.BurstFireOnly and burst_size > 1:
            raise ValueError("Firing action must be BurstFireOnly or FullyAutomatic to have a burst > 1")
        if self.isSingleShot:
            self._action = FiringAction.SingleShot
        self.BurstSize = burst_size

    def fire(self):
        self._currentCapacity -= self.BurstSize

    @property
    def damage(self):
        return super().damage * self.BurstSize

    @property
    def Action(self):
        return self._action


class SelectiveFire(Firearm):

    def toggleAction(self):
        if self._action == FiringAction.SemiAutomatic:
            self._action = FiringAction.FullyAutomatic
        else:
            self._action = FiringAction.SemiAutomatic


class Pistol(Firearm):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)


class WeblyRevolver(Pistol):
    """
    Based on the Webly Mk. IV
    """

    def __init__(self):
        super().__init__(caliber=Caliber.IN_38,
                         action=FiringAction.SemiAutomatic,
                         capacity=6,
                         range_falloff=.5,
                         base_damage=10,
                         name="Webly Mk. IV Revolver",
                         weightlb=2.4)


class M1911(Pistol):
    """
    Based on the M1911
    """

    def __init__(self):
        super().__init__(caliber=Caliber.IN_45,
                         action=FiringAction.SemiAutomatic,
                         capacity=7,
                         range_falloff=.4,
                         base_damage=8,
                         name="M1911 Pistol",
                         weightlb=2.44)


class APS(Pistol, SelectiveFire):
    """
    Based on the Stechkin automatic pistol (APS)
    """

    def __init__(self):
        super().__init__(caliber=Caliber.MM_9,
                         action=FiringAction.SemiAutomatic,
                         capacity=20,
                         range_falloff=.7,
                         base_damage=4,
                         name="Stechkin Automatic Pistol",
                         weightlb=2.69)


class SMG(Firearm):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)


class PPSh41(SMG, SelectiveFire):
    """
    Based on the PPSh-41 (Shpagin machine pistol)
    """

    def __init__(self):
        super().__init__(caliber=Caliber.MM_762,
                         action=FiringAction.FullyAutomatic,
                         capacity=35,
                         range_falloff=.55,
                         base_damage=7,
                         name="PPSh-41 (Shpagin machine pistol)",
                         weightlb=8.0)


class OwenSMG(SMG):
    """
    Based on the Owen Machine Carbine (Australian)
    """

    def __init__(self):
        super().__init__(caliber=Caliber.MM_9,
                         action=FiringAction.FullyAutomatic,
                         capacity=33,
                         range_falloff=.7,
                         base_damage=4,
                         name="Owen Machine Carbine",
                         weightlb=9.33)


class Rifle(Firearm):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)


class AK47(Rifle, SelectiveFire):
    """
    Based on the AK-47
    """

    def __init__(self):
        super().__init__(caliber=Caliber.MM_762,
                         action=FiringAction.FullyAutomatic,
                         capacity=30,
                         range_falloff=.35,
                         base_damage=15,
                         name="AK-47",
                         weightlb=7.7)


class HKG3(Rifle, SelectiveFire):
    """
    Based on the Heckler & Koch G3
    """

    def __init__(self):
        super().__init__(caliber=Caliber.MM_762,
                         action=FiringAction.FullyAutomatic,
                         capacity=20,
                         range_falloff=.3,
                         base_damage=14,
                         name="Heckler & Koch G3",
                         weightlb=9.7)


class Jezail(Rifle):
    """
    Based on the Jezail Musket
    https://en.wikipedia.org/wiki/Jezail
    """

    def __init__(self):
        super().__init__(caliber=Caliber.BB,
                         action=FiringAction.SingleShot,
                         capacity=1,
                         range_falloff=.3,
                         base_damage=20,
                         name="Jezail Musket",
                         weightlb=12)

    # TODO Give 2x dmg bonus if PlayerCharacter is on a mountain and target is not


class MachineGun(Firearm):

    def __init__(self, mountable=False, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._mountable = mountable
        self._mounted = False

    @property
    def Mounted(self) -> bool:
        return self._mounted

    @property
    def Mountable(self) -> bool:
        return self._mountable

    @Mounted.setter
    def Mounted(self, new: bool):
        if not self.Mountable:
            raise AttributeError("Cannot change mounting status of unmountable MachineGun.")
        self._mounted = new
        if self.Mounted:
            self.RangeFalloff -= .1
        else:
            self.RangeFalloff += .1


class FNMinimi(MachineGun):
    """
    Based on the FN Minimi
    """

    def __init__(self):
        super().__init__(mountable=True,
                         caliber=Caliber.MM_762,
                         action=FiringAction.FullyAutomatic,
                         capacity=100,
                         range_falloff=.25,
                         base_damage=13,
                         name="FN Minimi",
                         weightlb=15.1)


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
