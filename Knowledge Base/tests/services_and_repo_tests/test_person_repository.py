from domain_models.Identity_model.identity import (
    IdentityKind,
    IdentityRepresentations,
    LifecycleState,
)
from domain_models.Identity_model.Person_model.person import Person

from infrastructure.database.connection import DatabaseManager
from repositories.person_repository import PersonRepository


def test_person_repository_round_trip():

    database_manager = DatabaseManager()
    person_repository = PersonRepository()

    person = Person(
        representations=IdentityRepresentations(
            canonical_name="Strive Masiyiwa",
            aliases={
                "Strive",
                "S. Masiyiwa",
            },
        ),
        lifecycle_state=LifecycleState.CANONICAL,
    )

    # Persist.
    with database_manager.transaction() as connection:
        person_repository.save(
            person,
            connection=connection,
        )

    # Retrieve.
    with database_manager.connection() as connection:
        retrieved = person_repository.get_by_id(
            person.reference,
            connection=connection,
        )

    assert retrieved is not None

    # Reference.
    assert retrieved.reference == person.reference

    # Identity kind.
    assert retrieved.kind == IdentityKind.PERSON

    # Lifecycle state.
    assert retrieved.lifecycle_state == LifecycleState.CANONICAL

    # Canonical name.
    assert (
        retrieved.representations.canonical_name
        == "Strive Masiyiwa"
    )

    # Aliases.
    assert retrieved.representations.aliases == {
        "Strive",
        "S. Masiyiwa",
    }

    print("Test Passed")

test_person_repository_round_trip()