from application.services.person_service import PersonService
from infrastructure.database.connection import DatabaseManager
from repositories.person_repository import PersonRepository

def get_person_service() -> PersonService:
    person_repo = PersonRepository()
    database_manager = DatabaseManager()

    return PersonService(
        person_repository=person_repo,
        database_manager=database_manager,
    )

