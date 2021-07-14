from enum import Enum

from django.utils.translation import gettext_lazy as _


class Zone(Enum):
    A = _("Zone A")
    B = _("Zone B")
    C = _("Zone C")
    D = _("Zone D")
    E = _("Zone E")
    F = _("Zone F")
    H = _("Zone H")
    I = _("Zone I")
    J = _("Zone J")
    K = _("Zone K")
    L = _("Zone L")
    M = _("Zone M")
    N = _("Zone N")
    O = _("Zone O")
    P = _("Zone P")


class VehicleCategory(Enum):
    M1 = _("M1")
    M2 = _("M2")
    N1 = _("N1")
    N2 = _("N2")
    L3e = _("L3e")
    L4e = _("L4e")
    L5e = _("L5e")
    L6e = _("L6e")


class ContractType(Enum):
    FIXED_PERIOD = _("Fixed period")
    OPEN_ENDED = _("Open ended")


class VehicleType(Enum):
    BENSIN = _("Bensin")
    DIESEL = _("Diesel")
    BIFUEL = _("Bifuel")


class EmissionType(Enum):
    EURO = _("EURO")
    NEDC = _("NEDC")
    WLTP = _("WLTP")


LOW_EMISSION_DISCOUNT = 50
SECONDARY_VEHICLE_PRICE_INCREASE = 50
VAT_PERCENTAGE = 24
