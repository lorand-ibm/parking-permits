from ariadne import QueryType
from django.contrib.auth import get_user_model

query = QueryType()

schema_bindables = [
    query,
]


@query.field("admin_email")
def resolve_admin_email(*args):
    return get_user_model().objects.get(username="admin").email
