from application.services.identity_relationship_service import RelationshipService
from repositories.relationship_repository import RelationshipRepository
from infrastructure.database.connection import DatabaseManager
from API.v1.dependancies.relationship_resolution_dependancies import get_relationship_resolution_service

def get_relationship_service(
)->RelationshipService:

    relationship_repo = RelationshipRepository()
    database_manager = DatabaseManager()

    return RelationshipService(
        relationship_repository= relationship_repo,
        database_manager=database_manager,
        relationship_resolution_service=get_relationship_resolution_service(),
    )
