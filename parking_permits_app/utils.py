def apply_ordering(queryset, order_by):
    fields = order_by["order_fields"]
    direction = order_by["order_direction"]
    if direction == "DESC":
        fields = [f"-{field}" for field in fields]
    return queryset.order_by(*fields)
