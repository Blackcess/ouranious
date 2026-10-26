from application.services.organisation_service import OrganisationService
from repositories.organisation_repository import (
    OrganisationRepository,
)
from infrastructure.database.connection import DatabaseManager
from API.v1.dependancies.identity_resolution_dependancies import get_identity_resolution_service


def get_organisation_service() -> OrganisationService:
    database_manager = DatabaseManager()
    organisation_repository = OrganisationRepository()

    return OrganisationService(
        organisation_repository=organisation_repository,
        database_manager=database_manager,
        identity_resolution_service=get_identity_resolution_service(),
    )
