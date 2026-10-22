from application.services.organisation_service import OrganisationService
from repositories.organisation_repository import (
    OrganisationRepository,
)
from infrastructure.database.connection import DatabaseManager


def get_organisation_service() -> OrganisationService:
    database_manager = DatabaseManager()
    organisation_repository = OrganisationRepository()

    return OrganisationService(
        organisation_repository=organisation_repository,
        database_manager=database_manager,
    )