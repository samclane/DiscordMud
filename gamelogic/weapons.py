from gamelogic.items import Equipment


# Remember: def func(a, b, kw1=None, *args, **kwargs):


class AmmoType:
    Thrown = 0
    Bullet = 1


class Caliber:
    BB = 0


class Weapon(Equipment):
    BaseDamage: int

    def __init__(self, base_damage, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.BaseDamage = base_damage


class RangedWeapon(Weapon):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)


class ProjectileWeapon(RangedWeapon):
    AmmoType: int

    def __init__(self, ammo_type, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.AmmoType = ammo_type


class Firearm(ProjectileWeapon):
    Caliber: int

    def __init__(self, caliber, *args, **kwargs):
        super().__init__(AmmoType.Bullet, *args, **kwargs)
        self.Caliber = caliber


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
