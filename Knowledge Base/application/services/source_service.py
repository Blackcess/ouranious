"""Application operations for provenance sources."""

from uuid import UUID

from domain_models.Provenance.source import Source, SourceReference
from infrastructure.database.connection import DatabaseManager
from repositories.source_repository import SourceRepository


class SourceService:
    """Owns transaction boundaries for standalone source operations."""

    def __init__(
        self,
        *,
        source_repository: SourceRepository,
        database_manager: DatabaseManager,
    ):
        self._source_repository = source_repository
        self._database_manager = database_manager

    def create(self, source: Source) -> Source:
        """Persist and return a source. Duplicate references raise a conflict."""
        with self._database_manager.transaction() as connection:
            self._source_repository.create(source, connection=connection)
        return source

    def get_by_reference(self, reference: UUID | SourceReference) -> Source | None:
        with self._database_manager.connection() as connection:
            return self._source_repository.get_by_reference(
                reference, connection=connection
            )

    def exists(self, reference: UUID | SourceReference) -> bool:
        with self._database_manager.connection() as connection:
            return self._source_repository.exists(reference, connection=connection)
