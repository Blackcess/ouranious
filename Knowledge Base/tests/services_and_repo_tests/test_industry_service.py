from domain_models.Identity_model.identity import (
    IdentityKind,
    LifecycleState,
)

from infrastructure.database.connection import DatabaseManager
from repositories.industry_repository import IndustryRepository
from application.services.industry_service import IndustryCreationService


def test_industry_creation_service_round_trip():

    database_manager = DatabaseManager()
    industry_repository = IndustryRepository()

    industry_service = IndustryCreationService(
        industry_repository=industry_repository,
        database_manager=database_manager,
    )

    industry = industry_service.create(
        canonical_name="Financial Technology",
        aliases={
            "Fintech",
            "Financial Tech",
        },
    )

    retrieved = industry_service.get_by_id(
        industry.reference,
    )

    assert retrieved is not None

    # Identity reference.
    assert retrieved.reference == industry.reference

    # Identity kind.
    assert retrieved.kind == IdentityKind.INDUSTRY

    # Lifecycle state.
    assert retrieved.lifecycle_state == LifecycleState.CANONICAL

    # Canonical name.
    assert (
        retrieved.representations.canonical_name
        == "Financial Technology"
    )

    # Aliases.
    assert retrieved.representations.aliases == {
        "Fintech",
        "Financial Tech",
    }

    print("Test Passed")

test_industry_creation_service_round_trip()