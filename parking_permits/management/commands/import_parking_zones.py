from django.core.management.base import BaseCommand

from ...importers import ParkingZoneImporter


class Command(BaseCommand):
    help = "Uses the ParkingZoneImporter to import parking zones."

    def handle(self, *args, **options):
        ParkingZoneImporter().import_parking_zones()
