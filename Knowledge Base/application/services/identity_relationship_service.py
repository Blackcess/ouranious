from uuid import UUID

from domain_models.Identity_model.identity import Identity
from domain_models.relationship_models.relationship import Relationship, RelationshipReference

from domain_models.relationship_models.relationship_types.relationship_types import RelationshipType
from repositories.relationship_repository import RelationshipRepository
from infrastructure.database.connection import DatabaseManager
from application.services.create_orchestration import resolve_and_create_relationship
from application.services.relationship_resolution_service import (
    RelationshipResolutionService,
)
from application.resolution.create_result import CreateResult
from application.resolution.relationship.contracts import RelationshipResolutionResult


class RelationshipService:

    def __init__(
        self,
        *,
        relationship_repository: RelationshipRepository,
        database_manager: DatabaseManager,
        relationship_resolution_service: RelationshipResolutionService,
    ):
        self._relationship_repository = relationship_repository
        self._database_manager = database_manager
        self._relationship_resolution_service = relationship_resolution_service

    def create(
        self,
        *,
        source: Identity,
        target: Identity,
        relationship_type: RelationshipType,
        properties: object | None = None,
        allow_possible_duplicate: bool = False,
    ) -> CreateResult[Relationship, RelationshipResolutionResult]:
        """
        Create and persist a Relationship.

        The Relationship domain model is responsible for validating
        the relationship type, endpoint compatibility, and properties.

        The service owns the transaction boundary.
        """

        # 1. Construct the Relationship domain object.
        relationship = Relationship(
            source=source,
            target=target,
            type=relationship_type,
            properties=properties,
        )

        return resolve_and_create_relationship(
            relationship,
            repository=self._relationship_repository,
            database_manager=self._database_manager,
            resolver=self._relationship_resolution_service,
            allow_possible_duplicate=allow_possible_duplicate,
        )

    def get_by_id(
        self,
        reference: RelationshipReference | UUID,
    ) -> Relationship | None:
        """
        Retrieve a Relationship by its reference.
        """

        with self._database_manager.connection() as connection:
            return self._relationship_repository.get_by_id(
                reference,
                connection=connection,
            )
