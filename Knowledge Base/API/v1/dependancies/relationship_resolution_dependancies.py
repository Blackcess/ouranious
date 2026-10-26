"""FastAPI dependency factory for relationship duplicate resolution."""

from application.services.identity_resolver import IdentityResolver
from application.services.relationship_resolution_service import (
    RelationshipResolutionService,
)
from infrastructure.database.connection import DatabaseManager
from repositories.industry_repository import IndustryRepository
from repositories.organisation_repository import OrganisationRepository
from repositories.person_repository import PersonRepository
from repositories.place_repository import PlaceRepository
from repositories.product_repository import ProductRepository
from repositories.relationship_repository import RelationshipRepository
from repositories.technology_repository import TechnologyRepository


def get_relationship_resolution_service() -> RelationshipResolutionService:
    """Build relationship resolution with persisted endpoint validation."""

    person_repository = PersonRepository()
    organisation_repository = OrganisationRepository()
    place_repository = PlaceRepository()
    industry_repository = IndustryRepository()
    product_repository = ProductRepository()
    technology_repository = TechnologyRepository()

    identity_resolver = IdentityResolver(
        person_repository=person_repository,
        organisation_repository=organisation_repository,
        place_repository=place_repository,
        industry_repository=industry_repository,
        product_repository=product_repository,
        technology_repository=technology_repository,
        database_manager=DatabaseManager(),
    )

    relationship_repository = RelationshipRepository(
        person_repository=person_repository,
        organisation_repository=organisation_repository,
        place_repository=place_repository,
        industry_repository=industry_repository,
        product_repository=product_repository,
        technology_repository=technology_repository,
    )

    return RelationshipResolutionService(
        relationship_repository=relationship_repository,
        identity_resolver=identity_resolver,
        require_persisted_endpoints=True,
    )
