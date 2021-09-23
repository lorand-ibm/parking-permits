from ariadne import (
    MutationType,
    QueryType,
    convert_kwargs_to_snake_case,
    load_schema_from_path,
    snake_case_fallback_resolvers,
)
from ariadne.contrib.federation import FederatedObjectType
from django.core.exceptions import ObjectDoesNotExist
from django.db.models import Q

from project.settings import BASE_DIR

from . import constants
from .jwt import attach_token, authenticate_parking_permit_token
from .mock_vehicle import get_mock_vehicle
from .models import Address, Customer, ParkingPermit, ParkingZone, Vehicle
from .services.hel_profile import HelsinkiProfile
from .services.talpa import resolve_price_response

helsinki_profile_query = load_schema_from_path(
    BASE_DIR / "parking_permits_app" / "schema" / "helsinki_profile.graphql"
)


query = QueryType()
mutation = MutationType()
address_node = FederatedObjectType("AddressNode")
profile_node = FederatedObjectType("ProfileNode")

schema_bindables = [query, mutation, address_node, snake_case_fallback_resolvers]


@query.field("getPermits")
@authenticate_parking_permit_token
@convert_kwargs_to_snake_case
def resolve_customer_permits(obj, info, customer_id):
    try:
        permits = ParkingPermit.objects.filter(customer__pk=customer_id).order_by(
            "start_time"
        )
        payload = {
            "success": True,
            "permits": map(resolve_prices_and_low_emission, permits),
        }
    except AttributeError:
        payload = {
            "success": False,
            "errors": ["Permits item matching {id} not found"],
        }

    return payload


@query.field("profile")
@attach_token
def resolve_user_profile(_, info, *args):
    profile = HelsinkiProfile(info.context["request"])
    customer = profile.get_customer()
    primary_address, other_address = profile.get_addresses()

    primary_obj, _ = Address.objects.update_or_create(
        id=primary_address.get("id"), defaults=primary_address
    )

    other_obj, _ = Address.objects.update_or_create(
        id=other_address.get("id"), defaults=other_address
    )

    for obj in [primary_obj, other_obj]:
        obj.zone.price = obj.zone.get_current_price()
    customer_obj, _ = Customer.objects.update_or_create(
        id=customer.get("id"),
        defaults={
            **customer,
            **{"primary_address": primary_obj, "other_address": other_obj},
        },
    )

    return customer_obj


@mutation.field("deleteParkingPermit")
@authenticate_parking_permit_token
@convert_kwargs_to_snake_case
def resolve_delete_parking_permit(obj, info, permit_id, customer_id):
    try:
        permit = ParkingPermit.objects.get(id=permit_id, customer__id=customer_id)
        if permit.primary_vehicle:
            other_permit = (
                ParkingPermit.objects.filter(
                    customer=permit.customer,
                    status=constants.ParkingPermitStatus.DRAFT.value,
                )
                .exclude(id=permit.id)
                .first()
            )
            other_permit.primary_vehicle = True
            other_permit.save(update_fields=["primary_vehicle"])
        permit.delete()
        return {"success": True}
    except ObjectDoesNotExist:
        return {
            "success": False,
            "errors": [f"Permit item matching {permit_id} not found"],
        }


@mutation.field("createParkingPermit")
@authenticate_parking_permit_token
@convert_kwargs_to_snake_case
def resolve_create_parking_permit(obj, info, customer_id, zone_id, registration):
    customer = Customer.objects.get(id=customer_id)

    try:
        permit = ParkingPermit.objects.get(
            Q(vehicle__registration_number__iexact=registration),
            Q(vehicle__owner=customer) | Q(vehicle__holder=customer),
        )
    except ObjectDoesNotExist:
        customer_vehicles = Vehicle.objects.filter(
            Q(owner=customer) | Q(holder=customer),
        ).exclude(registration_number__iexact=registration)
        permit = ParkingPermit.objects.create(
            customer=customer,
            parking_zone=ParkingZone.objects.get(id=zone_id),
            primary_vehicle=len(customer_vehicles) == 0,
            vehicle=get_mock_vehicle(customer, registration),
        )
    return {"success": True, "permit": resolve_prices_and_low_emission(permit)}


@mutation.field("updateParkingPermit")
@authenticate_parking_permit_token
@convert_kwargs_to_snake_case
def resolve_update_parking_permit(obj, info, customer_id, permit_id, input):
    permit, _ = ParkingPermit.objects.update_or_create(
        id=permit_id, customer_id=customer_id, defaults=input
    )

    if "primary_vehicle" in input.keys():
        other_permit = (
            ParkingPermit.objects.filter(
                customer=permit.customer,
                status=constants.ParkingPermitStatus.DRAFT.value,
            )
            .exclude(id=permit_id)
            .first()
        )
        if other_permit:
            other_permit.primary_vehicle = not input.get("primary_vehicle")
            other_permit.save(update_fields=["primary_vehicle"])

    return {"success": True, "permit": resolve_prices_and_low_emission(permit)}


def resolve_prices_and_low_emission(permit):
    permit.prices = resolve_price_response(permit.get_total_price())
    vehicle = permit.vehicle
    vehicle.is_low_emission = vehicle.is_low_emission()
    return permit
