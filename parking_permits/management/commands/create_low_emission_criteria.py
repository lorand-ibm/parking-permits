from datetime import date, datetime

from django.conf import settings
from django.core.management.base import BaseCommand
from django.db import transaction

from parking_permits.models.vehicle import (
    EmissionType,
    LowEmissionCriteria,
    VehiclePowerType,
)

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


class Command(BaseCommand):
    help = "Create test low emission criteria"

    def add_arguments(self, parser):
        parser.add_argument("--year", type=int, default=datetime.now().year)

    @transaction.atomic
    def handle(self, *args, **options):
        if not settings.DEBUG:
            self.stdout.write("Cannot create test data in production environment")
            return

        start_date = date(options["year"], 1, 1)
        end_date = date(options["year"], 12, 31)
        for (power_type, emission_criteria) in LOW_EMISSION_CRITERIA.items():
            LowEmissionCriteria.objects.get_or_create(
                power_type=power_type,
                start_date=start_date,
                end_date=end_date,
                defaults={
                    "nedc_max_emission_limit": emission_criteria.get(EmissionType.NEDC),
                    "wltp_max_emission_limit": emission_criteria.get(EmissionType.WLTP),
                    "euro_min_class_limit": emission_criteria.get(EmissionType.EURO),
                },
            )
        self.stdout.write("Test LowEmissionCriteria created")
