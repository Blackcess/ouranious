
from application.services.technology_service import (
    TechnologyService,
)
from infrastructure.database.connection import DatabaseManager
from repositories.technology_repository import TechnologyRepository
from API.v1.dependancies.identity_resolution_dependancies import get_identity_resolution_service


def get_technology_service() -> TechnologyService:

    technology_repo = TechnologyRepository()
    database_manager = DatabaseManager()

    return TechnologyService(
        technology_repository=technology_repo,
        database_manager=database_manager,
        identity_resolution_service=get_identity_resolution_service(),
    )


