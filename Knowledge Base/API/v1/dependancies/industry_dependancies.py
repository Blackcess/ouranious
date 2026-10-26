
from application.services.industry_service import IndustryService
from infrastructure.database.connection import DatabaseManager
from repositories.industry_repository import IndustryRepository
from API.v1.dependancies.identity_resolution_dependancies import get_identity_resolution_service


def get_industry_service() -> IndustryService:
    industry_repo = IndustryRepository()
    database_manager = DatabaseManager()
    return IndustryService(
        industry_repository=industry_repo,
        database_manager=database_manager,
        identity_resolution_service=get_identity_resolution_service(),
    )
