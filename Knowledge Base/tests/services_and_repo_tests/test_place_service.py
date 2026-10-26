from domain_models.Identity_model.identity import (
    IdentityKind,
    LifecycleState,
)
from domain_models.Identity_model.Place_model.place import PlaceKind
from uuid import uuid4


def test_place_creation_service_round_trip(service_environment):
    place_service = service_environment["place"]
    canonical_name = f"Harare {uuid4().hex}"
    aliases = {f"Harare City {uuid4().hex}", f"Salisbury {uuid4().hex}"}

    # Create and persist through the service.
    result = place_service.create(
        canonical_name=canonical_name,
        place_kind=PlaceKind.CITY,
        aliases=aliases,
    )
    place = result.entity
    service_environment["track_identity"](place)
    assert result.action.value == "created"

    # Retrieve through the service.
    retrieved = place_service.get_by_id(
        place.reference,
    )

    assert retrieved is not None

    # Identity reference.
    assert retrieved.reference == place.reference

    # Identity kind.
    assert retrieved.kind == IdentityKind.PLACE

    # Lifecycle state.
    assert retrieved.lifecycle_state == LifecycleState.CANONICAL

    # Canonical representation.
    assert (
        retrieved.representations.canonical_name
        == canonical_name
    )

    # Aliases.
    assert retrieved.representations.aliases == aliases

    # Place-specific data.
    assert retrieved.get_place_kind() == PlaceKind.CITY

