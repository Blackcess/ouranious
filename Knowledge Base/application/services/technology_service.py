from uuid import UUID

from domain_models.Identity_model.identity import (
    IdentityReference,
    IdentityRepresentations,
    LifecycleState,
)
from domain_models.Identity_model.Technology_model.technology import Technology

from repositories.technology_repository import TechnologyRepository
from infrastructure.database.connection import DatabaseManager


class TechnologyService:

    def __init__(
        self,
        *,
        technology_repository: TechnologyRepository,
        database_manager: DatabaseManager,
    ):
        self._technology_repository = technology_repository
        self._database_manager = database_manager

    def create(
        self,
        *,
        canonical_name: str,
        aliases: set[str] | None = None,
        lifecycle_state: LifecycleState = LifecycleState.CANONICAL,
    ) -> Technology:
        """
        Create and persist a Technology.

        Returns the persisted Technology including its generated
        IdentityReference.
        """

        technology = Technology(
            representations=IdentityRepresentations(
                canonical_name=canonical_name,
                aliases=set(aliases or ()),
            ),
            lifecycle_state=lifecycle_state,
        )

        return self._persist_technology(technology)

    def _persist_technology(
        self,
        technology: Technology,
    ) -> Technology:
        """
        Persist a Technology atomically.
        """

        with self._database_manager.transaction() as connection:
            self._technology_repository.save(
                technology,
                connection=connection,
            )

        return technology

    def get_by_id(
        self,
        reference: IdentityReference | UUID,
    ) -> Technology | None:
        """
        Retrieve a Technology by identity reference.
        """

        with self._database_manager.connection() as connection:
            return self._technology_repository.get_by_id(
                reference,
                connection=connection,
            )