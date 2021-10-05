from ariadne import format_error
from django.core.exceptions import PermissionDenied


def error_formatter(error, debug):
    formatted = format_error(error, debug)
    if isinstance(error.original_error, PermissionDenied):
        formatted["message"] = "Forbidden"
    else:
        formatted["message"] = "Internal Server Error"
    return formatted
