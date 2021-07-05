from parking_permits_app.constants import LOW_EMISSION_DISCOUNT


def is_low_emission(
    euro_class=None,
    euro_class_min_limit=None,
    nedc_emission=None,
    nedc_emission_max_limit=None,
    wltp_emission=None,
    wltp_emission_max_limit=None,
):
    euro_compliant = euro_class >= euro_class_min_limit if euro_class else False
    nedc_compliant = (
        nedc_emission <= nedc_emission_max_limit if nedc_emission else False
    )
    wltp_compliant = (
        wltp_emission <= wltp_emission_max_limit if wltp_emission else False
    )

    return euro_compliant and (nedc_compliant or wltp_compliant)


def apply_low_emission_discount(price=None):
    return (price / 100) * LOW_EMISSION_DISCOUNT
