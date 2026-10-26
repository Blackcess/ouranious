from __future__ import annotations

import pytest

from application.services.identity_relationship_service import RelationshipService
from application.services.identity_resolution_service import IdentityResolutionService
from application.services.identity_resolver import IdentityResolver
from application.services.organisation_service import OrganisationService
from application.services.person_service import PersonService
from application.services.place_service import PlaceService
from application.services.industry_service import IndustryService
from application.services.product_service import ProductService
from application.services.relationship_resolution_service import (
    RelationshipResolutionService,
)
from application.services.technology_service import TechnologyService
from domain_models.Identity_model.identity import IdentityKind
from infrastructure.database.connection import DatabaseManager
from repositories.industry_repository import IndustryRepository
from repositories.organisation_repository import OrganisationRepository
from repositories.person_repository import PersonRepository
from repositories.place_repository import PlaceRepository
from repositories.product_repository import ProductRepository
from repositories.relationship_repository import RelationshipRepository
from repositories.technology_repository import TechnologyRepository


_RELATIONSHIP_PROPERTY_TABLES = (
    "relationship_investment_properties",
    "relationship_acquisition_properties",
    "relationship_founder_properties",
    "relationship_headquarters_properties",
    "relationship_industry_participation_properties",
    "relationship_leadership_properties",
    "relationship_market_presence_properties",
    "relationship_ownership_properties",
    "relationship_partnership_properties",
    "relationship_product_availability_properties",
    "relationship_product_development_properties",
    "relationship_product_offering_properties",
    "relationship_product_technology_properties",
    "relationship_residence_properties",
    "relationship_technology_adoption_properties",
)


@pytest.fixture
def database_manager():
    return DatabaseManager()


@pytest.fixture
def service_environment(database_manager):
    repositories = {
        IdentityKind.PERSON: PersonRepository(),
        IdentityKind.ORGANISATION: OrganisationRepository(),
        IdentityKind.PLACE: PlaceRepository(),
        IdentityKind.INDUSTRY: IndustryRepository(),
        IdentityKind.PRODUCT: ProductRepository(),
        IdentityKind.TECHNOLOGY: TechnologyRepository(),
    }
    identity_resolution = IdentityResolutionService(
        person_repository=repositories[IdentityKind.PERSON],
        organisation_repository=repositories[IdentityKind.ORGANISATION],
        place_repository=repositories[IdentityKind.PLACE],
        industry_repository=repositories[IdentityKind.INDUSTRY],
        product_repository=repositories[IdentityKind.PRODUCT],
        technology_repository=repositories[IdentityKind.TECHNOLOGY],
    )
    identity_resolver = IdentityResolver(
        person_repository=repositories[IdentityKind.PERSON],
        organisation_repository=repositories[IdentityKind.ORGANISATION],
        place_repository=repositories[IdentityKind.PLACE],
        industry_repository=repositories[IdentityKind.INDUSTRY],
        product_repository=repositories[IdentityKind.PRODUCT],
        technology_repository=repositories[IdentityKind.TECHNOLOGY],
        database_manager=database_manager,
    )
    relationship_repository = RelationshipRepository(
        person_repository=repositories[IdentityKind.PERSON],
        organisation_repository=repositories[IdentityKind.ORGANISATION],
        place_repository=repositories[IdentityKind.PLACE],
        industry_repository=repositories[IdentityKind.INDUSTRY],
        product_repository=repositories[IdentityKind.PRODUCT],
        technology_repository=repositories[IdentityKind.TECHNOLOGY],
    )
    relationship_resolution = RelationshipResolutionService(
        relationship_repository=relationship_repository,
        identity_resolver=identity_resolver,
        require_persisted_endpoints=True,
    )

    created_identity_ids: list[bytes] = []
    created_relationship_ids: list[bytes] = []

    def track_identity(identity):
        created_identity_ids.append(identity.reference.value.bytes)

    def track_relationship(relationship):
        created_relationship_ids.append(relationship.get_reference().value.bytes)

    services = {
        "person": PersonService(
            person_repository=repositories[IdentityKind.PERSON],
            database_manager=database_manager,
            identity_resolution_service=identity_resolution,
        ),
        "organisation": OrganisationService(
            organisation_repository=repositories[IdentityKind.ORGANISATION],
            database_manager=database_manager,
            identity_resolution_service=identity_resolution,
        ),
        "place": PlaceService(
            place_repository=repositories[IdentityKind.PLACE],
            database_manager=database_manager,
            identity_resolution_service=identity_resolution,
        ),
        "industry": IndustryService(
            industry_repository=repositories[IdentityKind.INDUSTRY],
            database_manager=database_manager,
            identity_resolution_service=identity_resolution,
        ),
        "product": ProductService(
            product_repository=repositories[IdentityKind.PRODUCT],
            database_manager=database_manager,
            identity_resolution_service=identity_resolution,
        ),
        "technology": TechnologyService(
            technology_repository=repositories[IdentityKind.TECHNOLOGY],
            database_manager=database_manager,
            identity_resolution_service=identity_resolution,
        ),
        "relationship": RelationshipService(
            relationship_repository=relationship_repository,
            database_manager=database_manager,
            relationship_resolution_service=relationship_resolution,
        ),
        "organisation": OrganisationService(
            organisation_repository=repositories[IdentityKind.ORGANISATION],
            database_manager=database_manager,
            identity_resolution_service=identity_resolution,
        ),
    }
    services["_created_identity_ids"] = created_identity_ids
    services["_created_relationship_ids"] = created_relationship_ids
    services["track_identity"] = track_identity
    services["track_relationship"] = track_relationship

    yield services

    if created_relationship_ids or created_identity_ids:
        with database_manager.transaction() as connection:
            with connection.cursor() as cursor:
                if created_relationship_ids:
                    marks = ", ".join(["%s"] * len(created_relationship_ids))
                    for table in _RELATIONSHIP_PROPERTY_TABLES:
                        cursor.execute(
                            f"DELETE FROM {table} WHERE relationship_id IN ({marks})",
                            created_relationship_ids,
                        )
                    cursor.execute(
                        f"DELETE FROM relationships WHERE relationship_id IN ({marks})",
                        created_relationship_ids,
                    )
                if created_identity_ids:
                    marks = ", ".join(["%s"] * len(created_identity_ids))
                    for table, column in (
                        ("startup_models", "organisation_id"),
                        ("investor_models", "organisation_id"),
                        ("accelerator_programmes", "accelerator_id"),
                        ("organisation_classifications", "organisation_id"),
                        ("organisations", "identity_id"),
                        ("places", "identity_id"),
                        ("identity_aliases", "identity_id"),
                        ("identities", "identity_id"),
                    ):
                        cursor.execute(
                            f"DELETE FROM {table} WHERE {column} IN ({marks})",
                            created_identity_ids,
                        )
