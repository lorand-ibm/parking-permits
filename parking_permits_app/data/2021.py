from decimal import Decimal

from parking_permits_app.constants import EmissionType, VehicleType, Zone

ZONE_MONTHLY_PRICES = {
    Zone.A.value: Decimal("30.00"),
    Zone.B.value: Decimal("30.00"),
    Zone.C.value: Decimal("30.00"),
    Zone.D.value: Decimal("30.00"),
    Zone.E.value: Decimal("30.00"),
    Zone.F.value: Decimal("30.00"),
    Zone.H.value: Decimal("30.00"),
    Zone.I.value: Decimal("30.00"),
    Zone.J.value: Decimal("30.00"),
    Zone.K.value: Decimal("30.00"),
    Zone.L.value: Decimal("30.00"),
    Zone.M.value: Decimal("15.00"),
    Zone.N.value: Decimal("15.00"),
    Zone.O.value: Decimal("15.00"),
    Zone.P.value: Decimal("15.00"),
}

LOW_EMISSION_CRITERIA = {
    VehicleType.BENSIN.value: {
        EmissionType.EURO.value: 6,
        EmissionType.NEDC.value: 95,
        EmissionType.WLTP.value: 126,
    },
    VehicleType.DIESEL.value: {
        EmissionType.EURO.value: 6,
        EmissionType.NEDC.value: 50,
        EmissionType.WLTP.value: 70,
    },
    VehicleType.BIFUEL.value: {
        EmissionType.EURO.value: 6,
        EmissionType.NEDC.value: 150,
        EmissionType.WLTP.value: 180,
    },
}
