from ariadne import format_error
from django.core.exceptions import PermissionDenied

from parking_permits_app.exceptions import ParkingPermitBaseException


def error_formatter(error, debug):
    formatted = format_error(error, debug)
    if isinstance(error.original_error, ParkingPermitBaseException):
        formatted["message"] = str(error.original_error)
    elif isinstance(error.original_error, PermissionDenied):
        formatted["message"] = "Forbidden"
    else:
        formatted["message"] = "Internal Server Error"
    return formatted
