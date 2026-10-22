"""FastAPI dependency factory for identity duplicate resolution."""

from application.services.identity_resolution_service import IdentityResolutionService
from infrastructure.database.connection import DatabaseManager
from repositories.industry_repository import IndustryRepository
from repositories.organisation_repository import OrganisationRepository
from repositories.person_repository import PersonRepository
from repositories.place_repository import PlaceRepository
from repositories.product_repository import ProductRepository
from repositories.technology_repository import TechnologyRepository


def get_identity_resolution_service() -> IdentityResolutionService:
    """Build the resolver with the six repositories used by the application."""

    return IdentityResolutionService(
        person_repository=PersonRepository(),
        organisation_repository=OrganisationRepository(),
        place_repository=PlaceRepository(),
        industry_repository=IndustryRepository(),
        product_repository=ProductRepository(),
        technology_repository=TechnologyRepository(),
        database_manager=DatabaseManager(),
    )
