from uuid import UUID

from domain_models.Identity_model.identity import (
    IdentityRepresentations,
    IdentityReference,
    LifecycleState,
)
from domain_models.Identity_model.Place_model.place import Place, PlaceKind

from repositories.place_repository import PlaceRepository
from infrastructure.database.connection import DatabaseManager
from application.services.create_orchestration import resolve_and_create_identity
from application.services.identity_resolution_service import IdentityResolutionService
from application.resolution.create_result import CreateResult
from application.resolution.identity.contracts import IdentityResolutionResult


class PlaceService:

    def __init__(
        self,
        *,
        place_repository: PlaceRepository,
        database_manager: DatabaseManager,
        identity_resolution_service: IdentityResolutionService,
    ):
        self._place_repository = place_repository
        self._database_manager = database_manager
        self._identity_resolution_service = identity_resolution_service

    def create(
        self,
        *,
        canonical_name: str,
        place_kind: PlaceKind,
        aliases: set[str] | None = None,
        lifecycle_state: LifecycleState = LifecycleState.CANONICAL,
        allow_possible_duplicate: bool = False,
    ) -> CreateResult[Place, IdentityResolutionResult]:
        """
        Create and persist a Place.

        Returns the persisted Place including its generated
        IdentityReference.
        """

        # 1. Construct the Place domain object.
        place = Place(
            representations=IdentityRepresentations(
                canonical_name=canonical_name,
                aliases=set(aliases or ()),
            ),
            lifecycle_state=lifecycle_state,
            place_kind=place_kind,
        )

        # 2. Persist the Place atomically.
        return resolve_and_create_identity(
            place,
            repository=self._place_repository,
            database_manager=self._database_manager,
            resolver=self._identity_resolution_service,
            allow_possible_duplicate=allow_possible_duplicate,
        )

    def get_by_id(
        self,
        reference: IdentityReference | UUID,
    ) -> Place | None:
        """
        Retrieve a Place by its identity reference.
        """

        with self._database_manager.connection() as connection:
            return self._place_repository.get_by_id(
                reference,
                connection=connection,
            )
