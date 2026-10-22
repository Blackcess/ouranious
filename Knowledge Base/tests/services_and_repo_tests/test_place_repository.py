from domain_models.Identity_model.identity import (
    IdentityKind,
    IdentityRepresentations,
    LifecycleState,
)
from domain_models.Identity_model.Place_model.place import Place, PlaceKind

from infrastructure.database.connection import DatabaseManager
from repositories.place_repository import PlaceRepository


def test_place_repository_round_trip():
    database_manager = DatabaseManager()
    place_repository = PlaceRepository()

    place = Place(
        representations=IdentityRepresentations(
            canonical_name="Harare",
            aliases={
                "Harare City",
                "Salisbury",
            },
        ),
        lifecycle_state=LifecycleState.CANONICAL,
        place_kind=PlaceKind.CITY,
    )

    # Persist the Place.
    with database_manager.transaction() as connection:
        place_repository.save(
            place,
            connection=connection,
        )

    # Retrieve the Place.
    with database_manager.connection() as connection:
        retrieved = place_repository.get_by_id(
            place.reference,
            connection=connection,
        )

    # Ensure the Place was retrieved.
    assert retrieved is not None

    # Identity reference.
    assert retrieved.reference == place.reference

    # Identity kind.
    assert retrieved.kind == IdentityKind.PLACE

    # Lifecycle state.
    assert retrieved.lifecycle_state == LifecycleState.CANONICAL

    # Canonical name.
    assert (
        retrieved.representations.canonical_name
        == "Harare"
    )

    # Aliases.
    assert retrieved.representations.aliases == {
        "Harare City",
        "Salisbury",
    }

    # Place-specific property.
    assert retrieved.get_place_kind() == PlaceKind.CITY
    print("TEST PASSED: test_place_repository_round_trip")

test_place_repository_round_trip()