
from application.services.place_service import PlaceService
from repositories.place_repository import PlaceRepository
from infrastructure.database.connection import DatabaseManager


def get_place_service() -> PlaceService:

    place_repo = PlaceRepository()
    database_manager = DatabaseManager()

    return PlaceService(
        place_repository=place_repo,
        database_manager=database_manager,
    )
