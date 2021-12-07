from decimal import Decimal

from parking_permits.models.vehicle import EmissionType, VehiclePowerType

ZONE_MONTHLY_PRICES = {
    "A": Decimal("30.00"),
    "B": Decimal("30.00"),
    "C": Decimal("30.00"),
    "D": Decimal("30.00"),
    "E": Decimal("30.00"),
    "F": Decimal("30.00"),
    "H": Decimal("30.00"),
    "I": Decimal("30.00"),
    "J": Decimal("30.00"),
    "K": Decimal("30.00"),
    "L": Decimal("30.00"),
    "M": Decimal("15.00"),
    "N": Decimal("15.00"),
    "O": Decimal("15.00"),
    "P": Decimal("15.00"),
}

LOW_EMISSION_CRITERIA = {
    VehiclePowerType.BENSIN: {
        EmissionType.EURO: 6,
        EmissionType.NEDC: 95,
        EmissionType.WLTP: 126,
    },
    VehiclePowerType.DIESEL: {
        EmissionType.EURO: 6,
        EmissionType.NEDC: 50,
        EmissionType.WLTP: 70,
    },
    VehiclePowerType.BIFUEL: {
        EmissionType.EURO: 6,
        EmissionType.NEDC: 150,
        EmissionType.WLTP: 180,
    },
}
