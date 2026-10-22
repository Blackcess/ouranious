from domain_models.Identity_model.identity import (
    IdentityKind,
    LifecycleState,
    IdentityRepresentations,
)
from domain_models.Identity_model.Industry_model.industry import Industry

from infrastructure.database.connection import DatabaseManager
from repositories.industry_repository import IndustryRepository


def test_industry_repository_round_trip():

    database_manager = DatabaseManager()
    industry_repository = IndustryRepository()

    industry = Industry(
        representations=IdentityRepresentations(
            canonical_name="Financial Technology",
            aliases={
                "Fintech",
                "Financial Tech",
            },
        ),
        lifecycle_state=LifecycleState.CANONICAL,
    )

    with database_manager.transaction() as connection:
        industry_repository.save(
            industry,
            connection=connection,
        )

    with database_manager.connection() as connection:
        retrieved = industry_repository.get_by_id(
            industry.reference,
            connection=connection,
        )

    assert retrieved is not None

    assert retrieved.reference == industry.reference
    assert retrieved.kind == IdentityKind.INDUSTRY
    assert retrieved.lifecycle_state == LifecycleState.CANONICAL

    assert (
        retrieved.representations.canonical_name
        == "Financial Technology"
    )

    assert retrieved.representations.aliases == {
        "Fintech",
        "Financial Tech",
    }

    print("Test Passed")

test_industry_repository_round_trip()