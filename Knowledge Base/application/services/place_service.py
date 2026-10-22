from uuid import UUID

from domain_models.Identity_model.identity import (
    IdentityRepresentations,
    IdentityReference,
    LifecycleState,
)
from domain_models.Identity_model.Place_model.place import Place, PlaceKind

from repositories.place_repository import PlaceRepository
from infrastructure.database.connection import DatabaseManager


class PlaceService:

    def __init__(
        self,
        *,
        place_repository: PlaceRepository,
        database_manager: DatabaseManager,
    ):
        self._place_repository = place_repository
        self._database_manager = database_manager

    def create(
        self,
        *,
        canonical_name: str,
        place_kind: PlaceKind,
        aliases: set[str] | None = None,
        lifecycle_state: LifecycleState = LifecycleState.CANONICAL,
    ) -> Place:
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
        return self._persist_place(place)

    def _persist_place(
        self,
        place: Place,
    ) -> Place:
        """
        Persist a Place atomically.

        The repository performs persistence while this service
        owns the transaction boundary.
        """

        with self._database_manager.transaction() as connection:
            self._place_repository.save(
                place,
                connection=connection,
            )

        return place

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