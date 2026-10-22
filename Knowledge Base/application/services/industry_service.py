from uuid import UUID

from domain_models.Identity_model.identity import (
    IdentityReference,
    IdentityRepresentations,
    LifecycleState,
)
from domain_models.Identity_model.Industry_model.industry import Industry

from repositories.industry_repository import IndustryRepository
from infrastructure.database.connection import DatabaseManager


class IndustryService:

    def __init__(
        self,
        *,
        industry_repository: IndustryRepository,
        database_manager: DatabaseManager,
    ):
        self._industry_repository = industry_repository
        self._database_manager = database_manager

    def create(
        self,
        *,
        canonical_name: str,
        aliases: set[str] | None = None,
        lifecycle_state: LifecycleState = LifecycleState.CANONICAL,
    ) -> Industry:
        """
        Create and persist an Industry.

        Returns the persisted Industry including its generated
        IdentityReference.
        """

        industry = Industry(
            representations=IdentityRepresentations(
                canonical_name=canonical_name,
                aliases=set(aliases or ()),
            ),
            lifecycle_state=lifecycle_state,
        )

        return self._persist_industry(industry)

    def _persist_industry(
        self,
        industry: Industry,
    ) -> Industry:
        """
        Persist an Industry atomically.
        """

        with self._database_manager.transaction() as connection:
            self._industry_repository.save(
                industry,
                connection=connection,
            )

        return industry

    def get_by_id(
        self,
        reference: IdentityReference | UUID,
    ) -> Industry | None:
        """
        Retrieve an Industry by identity reference.
        """

        with self._database_manager.connection() as connection:
            return self._industry_repository.get_by_id(
                reference,
                connection=connection,
            )