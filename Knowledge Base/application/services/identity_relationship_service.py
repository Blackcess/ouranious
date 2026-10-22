from uuid import UUID

from domain_models.Identity_model.identity import Identity
from domain_models.relationship_models.relationship import Relationship, RelationshipReference

from domain_models.relationship_models.relationship_types.relationship_types import RelationshipType
from repositories.relationship_repository import RelationshipRepository
from infrastructure.database.connection import DatabaseManager


class RelationshipService:

    def __init__(
        self,
        *,
        relationship_repository: RelationshipRepository,
        database_manager: DatabaseManager,
    ):
        self._relationship_repository = relationship_repository
        self._database_manager = database_manager

    def create(
        self,
        *,
        source: Identity,
        target: Identity,
        relationship_type: RelationshipType,
        properties: object | None = None,
    ) -> Relationship:
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

        # 2. Persist the relationship atomically.
        return self._persist_relationship(relationship)

    def _persist_relationship(
        self,
        relationship: Relationship,
    ) -> Relationship:
        """
        Persist a Relationship atomically.

        The repository performs persistence while this service owns
        the transaction boundary.
        """

        with self._database_manager.transaction() as connection:
            self._relationship_repository.save(
                relationship,
                connection=connection,
            )

        return relationship

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