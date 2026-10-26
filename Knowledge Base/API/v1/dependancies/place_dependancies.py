
from application.services.place_service import PlaceService
from repositories.place_repository import PlaceRepository
from infrastructure.database.connection import DatabaseManager
from API.v1.dependancies.identity_resolution_dependancies import get_identity_resolution_service


def get_place_service() -> PlaceService:

    place_repo = PlaceRepository()
    database_manager = DatabaseManager()

    return PlaceService(
        place_repository=place_repo,
        database_manager=database_manager,
        identity_resolution_service=get_identity_resolution_service(),
    )
