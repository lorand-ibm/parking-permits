import logging
from datetime import date
from importlib import import_module

from django.core.management.base import BaseCommand
from django.db import transaction

from parking_permits.models.vehicle import EmissionType, LowEmissionCriteria

logger = logging.getLogger(__name__)


class Command(BaseCommand):
    help = "Usage: python manage.py create_low_emission_criteria --year 2021 --data-module parking_permits.data.2021"  # noqa

    def add_arguments(self, parser):
        parser.add_argument("--year", type=int, required=True)
        parser.add_argument("--data-module", type=str, required=True)

    @transaction.atomic
    def handle(self, *args, **options):
        data_module = import_module(options.get("data_module"))

        for (
            power_type,
            emission_criteria,
        ) in data_module.LOW_EMISSION_CRITERIA.items():
            obj, created = LowEmissionCriteria.objects.get_or_create(
                power_type=power_type,
                nedc_max_emission_limit=emission_criteria.get(EmissionType.NEDC),
                wltp_max_emission_limit=emission_criteria.get(EmissionType.WLTP),
                euro_min_class_limit=emission_criteria.get(EmissionType.EURO),
                start_date=date(day=1, month=1, year=options.get("year")),
                end_date=date(day=31, month=12, year=options.get("year")),
            )

            if created:
                logger.info(f"{obj.power_type} emission criteria created")
            else:
                logger.info(f"{obj.power_type} emission criteria already exists")
