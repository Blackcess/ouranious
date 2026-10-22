from domain_models.Identity_model.identity import (
    IdentityKind,
    LifecycleState,
)

from infrastructure.database.connection import DatabaseManager
from repositories.technology_repository import TechnologyRepository
from application.services.technology_service import TechnologyCreationService


def test_technology_creation_service_round_trip():

    database_manager = DatabaseManager()
    technology_repository = TechnologyRepository()

    technology_service = TechnologyCreationService(
        technology_repository=technology_repository,
        database_manager=database_manager,
    )

    technology = technology_service.create(
        canonical_name="React",
        aliases={
            "React.js",
            "ReactJS",
        },
    )

    retrieved = technology_service.get_by_id(
        technology.reference,
    )

    assert retrieved is not None

    assert retrieved.reference == technology.reference
    assert retrieved.kind == IdentityKind.TECHNOLOGY
    assert retrieved.lifecycle_state == LifecycleState.CANONICAL

    assert (
        retrieved.representations.canonical_name
        == "React"
    )

    assert retrieved.representations.aliases == {
        "React.js",
        "ReactJS",
    }

    print("Test Passed")

test_technology_creation_service_round_trip()