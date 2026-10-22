from uuid import UUID

from pymysql.connections import Connection

from domain_models.Identity_model.identity import (
    IdentityKind,
    IdentityReference,
    IdentityRepresentations,
    LifecycleState,
)
from domain_models.Identity_model.Place_model.place import Place, PlaceKind

from repositories.utils.errors import RepositoryIntegrityError
from repositories.utils.candidate_page import CandidatePage
from repositories.utils.identity_candidate_search import find_identity_candidate_ids


class PlaceRepository:

    def find_candidates(
        self,
        identity: Place,
        *,
        exclude_reference: UUID | IdentityReference | None = None,
        include_retired: bool = False,
        limit: int = 100,
        connection: Connection,
    ) -> CandidatePage[Place]:
        """Return bounded same-kind candidates for exact/normalized names."""

        if not isinstance(identity, Place):
            raise TypeError("PlaceRepository requires a Place identity.")

        id_page = find_identity_candidate_ids(
            kind=IdentityKind.PLACE,
            canonical_name=identity.representations.canonical_name,
            aliases=identity.representations.aliases,
            exclude_reference=exclude_reference,
            include_retired=include_retired,
            limit=limit,
            connection=connection,
        )
        candidates = tuple(
            candidate
            for identity_id in id_page.items
            if (
                candidate := self.get_by_id(
                    UUID(bytes=identity_id),
                    connection=connection,
                )
            ) is not None
        )
        return CandidatePage(candidates, truncated=id_page.truncated)

    def save(
        self,
        place: Place,
        *,
        connection: Connection,
    ) -> None:

        if place.kind != IdentityKind.PLACE:
            raise ValueError(
                "PlaceRepository can only persist PLACE identities."
            )

        identity_id = place.reference.value.bytes

        with connection.cursor() as cursor:

            cursor.execute(
                """
                INSERT INTO identities (
                    identity_id,
                    kind,
                    lifecycle_state,
                    canonical_name
                )
                VALUES (%s, %s, %s, %s)
                """,
                (
                    identity_id,
                    place.kind.value,
                    place.lifecycle_state.value,
                    place.representations.canonical_name,
                ),
            )

            for alias in place.representations.aliases:
                cursor.execute(
                    """
                    INSERT INTO identity_aliases (
                        identity_id,
                        alias
                    )
                    VALUES (%s, %s)
                    """,
                    (
                        identity_id,
                        alias,
                    ),
                )

            cursor.execute(
                """
                INSERT INTO places (
                    identity_id,
                    place_kind
                )
                VALUES (%s, %s)
                """,
                (
                    identity_id,
                    place.get_place_kind().value,
                ),
            )

    def get_by_id(
        self,
        reference: UUID | IdentityReference,
        *,
        connection: Connection,
    ) -> Place | None:

        if isinstance(reference, IdentityReference):
            identity_id = reference.value.bytes
        else:
            identity_id = reference.bytes

        with connection.cursor() as cursor:

            cursor.execute(
                """
                SELECT
                    identity_id,
                    kind,
                    lifecycle_state,
                    canonical_name
                FROM identities
                WHERE identity_id = %s
                """,
                (identity_id,),
            )

            identity_row = cursor.fetchone()

            if identity_row is None:
                return None

            if identity_row["kind"] != IdentityKind.PLACE.value:
                return None

            cursor.execute(
                """
                SELECT alias
                FROM identity_aliases
                WHERE identity_id = %s
                """,
                (identity_id,),
            )

            aliases = {
                row["alias"]
                for row in cursor.fetchall()
            }

            cursor.execute(
                """
                SELECT place_kind
                FROM places
                WHERE identity_id = %s
                """,
                (identity_id,),
            )

            place_row = cursor.fetchone()

            if place_row is None:
                raise RepositoryIntegrityError(
                    f"PLACE identity {identity_row['identity_id']!r} "
                    "has no corresponding places row."
                )

        try:
            place_kind = PlaceKind(place_row["place_kind"])
            lifecycle_state = LifecycleState(
                identity_row["lifecycle_state"]
            )
            identity_reference = IdentityReference(
                UUID(bytes=identity_row["identity_id"])
            )

        except (ValueError, TypeError) as exc:
            raise RepositoryIntegrityError(
                "Invalid persisted PLACE identity state."
            ) from exc

        return Place(
            representations=IdentityRepresentations(
                canonical_name=identity_row["canonical_name"],
                aliases=aliases,
            ),
            reference=identity_reference,
            lifecycle_state=lifecycle_state,
            place_kind=place_kind,
        )
