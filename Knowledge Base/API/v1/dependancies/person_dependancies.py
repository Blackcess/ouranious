from application.services.person_service import PersonService
from infrastructure.database.connection import DatabaseManager
from repositories.person_repository import PersonRepository
from API.v1.dependancies.identity_resolution_dependancies import get_identity_resolution_service

def get_person_service() -> PersonService:
    person_repo = PersonRepository()
    database_manager = DatabaseManager()

    return PersonService(
        person_repository=person_repo,
        database_manager=database_manager,
        identity_resolution_service=get_identity_resolution_service(),
    )

