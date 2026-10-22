
from uuid import UUID

from domain_models.Identity_model.identity import (
    Identity,
    IdentityReference,
)

from repositories.person_repository import PersonRepository
from repositories.organisation_repository import OrganisationRepository
from repositories.place_repository import PlaceRepository
from repositories.industry_repository import IndustryRepository
from repositories.technology_repository import TechnologyRepository
from repositories.product_repository import ProductRepository

from infrastructure.database.connection import DatabaseManager


class IdentityResolver:
    def __init__(
        self,
        *,
        person_repository: PersonRepository,
        organisation_repository: OrganisationRepository,
        place_repository: PlaceRepository,
        industry_repository: IndustryRepository,
        technology_repository: TechnologyRepository,
        product_repository: ProductRepository,
        database_manager: DatabaseManager,
    ):
        self._repositories = (
            person_repository,
            organisation_repository,
            place_repository,
            industry_repository,
            technology_repository,
            product_repository,
        )
        self._database_manager = database_manager

    def get_by_id(
        self,
        identity_id: UUID | IdentityReference,
    ) -> Identity | None:
        """
        Resolve and reconstruct an identity using its UUID.

        Returns None if no identity repository recognizes the ID.
        Repository integrity errors propagate to the caller.
        """

        with self._database_manager.connection() as connection:
            for repository in self._repositories:
                identity = repository.get_by_id(
                    identity_id,
                    connection=connection,
                )

                if identity is not None:
                    return identity

        return None
