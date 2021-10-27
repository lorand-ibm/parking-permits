from ariadne import (
    ObjectType,
    QueryType,
    convert_kwargs_to_snake_case,
    snake_case_fallback_resolvers,
)

from parking_permits_app.models import ParkingPermit

from .decorators import is_ad_admin
from .paginator import QuerySetPaginator
from .reversion import get_obj_changelogs
from .utils import apply_filtering, apply_ordering

query = QueryType()
PermitDetail = ObjectType("PermitDetailNode")
schema_bindables = [query, PermitDetail, snake_case_fallback_resolvers]


@query.field("permits")
@is_ad_admin
@convert_kwargs_to_snake_case
def resolve_permits(_, info, page_input, order_by=None, search_items=None):
    permits = ParkingPermit.objects.all()
    if order_by:
        permits = apply_ordering(permits, order_by)
    if search_items:
        permits = apply_filtering(permits, search_items)
    paginator = QuerySetPaginator(permits, page_input)
    return {
        "page_info": paginator.page_info,
        "objects": paginator.object_list,
    }


@query.field("permitDetail")
@is_ad_admin
@convert_kwargs_to_snake_case
def resolve_permit_detail(_, info, permit_id):
    return ParkingPermit.objects.get(identifier=permit_id)


@PermitDetail.field("changeLogs")
def resolve_permit_detail_history(permit, info):
    return get_obj_changelogs(permit)
