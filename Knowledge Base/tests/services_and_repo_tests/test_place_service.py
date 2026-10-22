from domain_models.Identity_model.identity import (
    IdentityKind,
    LifecycleState,
)
from domain_models.Identity_model.Place_model.place import PlaceKind

from infrastructure.database.connection import DatabaseManager
from repositories.place_repository import PlaceRepository
from application.services.place_service import PlaceCreationService


def test_place_creation_service_round_trip():

    database_manager = DatabaseManager()
    place_repository = PlaceRepository()

    place_service = PlaceCreationService(
        place_repository=place_repository,
        database_manager=database_manager,
    )

    # Create and persist through the service.
    place = place_service.create(
        canonical_name="Harare",
        place_kind=PlaceKind.CITY,
        aliases={
            "Harare City",
            "Salisbury",
        },
    )

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
        == "Harare"
    )

    # Aliases.
    assert retrieved.representations.aliases == {
        "Harare City",
        "Salisbury",
    }

    # Place-specific data.
    assert retrieved.get_place_kind() == PlaceKind.CITY

test_place_creation_service_round_trip()