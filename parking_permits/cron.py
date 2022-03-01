import logging

from django.utils import timezone

from parking_permits.models import Customer, ParkingPermit
from parking_permits.models.parking_permit import ParkingPermitStatus

logger = logging.getLogger("db")


def automatic_expiration_of_permits():
    ParkingPermit.objects.filter(
        end_time__lt=timezone.now(), status=ParkingPermitStatus.VALID
    ).update(status=ParkingPermitStatus.CLOSED)


def automatic_remove_obsolete_customer_data():
    logger.info("Automatically removing obsolte customer data started...")
    qs = Customer.objects.all()
    count = 0
    for customer in qs:
        if customer.can_be_deleted:
            customer.delete_all_data()
            count += 1
    logger.info(
        "Automatically removing obsolte customer data completed. "
        f"{count} customers are removed."
    )
