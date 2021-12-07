import operator
from functools import reduce

from dateutil.relativedelta import relativedelta
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


def diff_months_floor(start_date, end_date):
    if start_date > end_date:
        return 0
    diff = relativedelta(end_date, start_date)
    return diff.months + diff.years * 12


def diff_months_ceil(start_date, end_date):
    if start_date > end_date:
        return 0
    diff = relativedelta(end_date, start_date)
    diff_months = diff.months + diff.years * 12
    if diff.days >= 0:
        diff_months += 1
    return diff_months


def get_end_time(start_time, diff_months):
    end_time = start_time + relativedelta(months=diff_months)
    return end_time.replace(hour=0, minute=0, second=0, microsecond=0)
