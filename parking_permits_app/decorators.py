from functools import wraps

from django.core.exceptions import PermissionDenied
from helusers.oidc import AuthenticationError, RequestJWTAuthentication


def user_passes_test(test_func):
    def decorator(f):
        @wraps(f)
        def wrapper(obj, info, *args, **kwargs):
            request = info.context["request"]
            try:
                auth = RequestJWTAuthentication().authenticate(request)
            except AuthenticationError as e:
                raise PermissionDenied(e)

            if test_func(auth.user):
                return f(obj, info, *args, **kwargs)
            raise PermissionDenied()

        return wrapper

    return decorator


is_login = user_passes_test(lambda u: u.is_authenticated)
is_ad_admin = user_passes_test(lambda u: u.is_ad_admin)
