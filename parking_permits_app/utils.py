import operator
from functools import reduce

from django.db.models import Q


def apply_ordering(queryset, order_by):
    fields = order_by["order_fields"]
    direction = order_by["order_direction"]
    if direction == "DESC":
        fields = [f"-{field}" for field in fields]
    return queryset.order_by(*fields)


def apply_filtering(queryset, search_items):
    query = Q()
    for search_item in search_items:
        match_type = search_item["match_type"]
        fields = search_item["fields"]
        value = search_item["value"]
        search_item_query = reduce(
            operator.or_, [Q(**{f"{field}__{match_type}": value}) for field in fields]
        )
        query &= search_item_query
    return queryset.filter(query)
