import jwt
from django.conf import settings
from jwt.exceptions import InvalidTokenError


class MissingAuthorizationToken(Exception):
    pass


def get_auth_token(request):
    """
    Authorization is a bearer token and there for it should have
    a format of Bearer <TOKEN>
    """
    authorization = request.headers.get("Authorization")
    if not authorization:
        raise MissingAuthorizationToken("Authorization token is missing.")
    auth_parts = authorization.split()
    if len(auth_parts) == 1:
        raise MissingAuthorizationToken("Authorization token is missing.")
    return auth_parts[1]


def attach_token(func):
    def wrapper(_, info, *args):
        token = get_auth_token(request=info.context["request"])
        decoded = jwt.decode(token, options={"verify_signature": False})
        user = func(_, info, *args)
        user.token = jwt.encode(
            {"id": user.pk, "exp": decoded.get("exp")},
            settings.JWT_SECRET,
            algorithm="HS256",
        )
        return user

    return wrapper


def authenticate_parking_permit_token(func):
    def wrapper(_, info, *args, **kwargs):
        token = get_auth_token(request=info.context["request"])
        try:
            payload = jwt.decode(token, settings.JWT_SECRET, algorithms=["HS256"])
        except InvalidTokenError:
            raise InvalidTokenError("Invalid parking permit authorization token.")
        kwargs["customer_id"] = payload.get("id")
        return func(_, info, *args, **kwargs)

    return wrapper
