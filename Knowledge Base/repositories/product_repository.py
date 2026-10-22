from uuid import UUID

from pymysql.connections import Connection

from domain_models.Identity_model.identity import (
    IdentityKind,
    IdentityReference,
    IdentityRepresentations,
    LifecycleState,
)
from domain_models.Identity_model.Product_model.product import Product

from repositories.utils.errors import RepositoryIntegrityError
from repositories.utils.candidate_page import CandidatePage
from repositories.utils.identity_candidate_search import find_identity_candidate_ids


class ProductRepository:

    def find_candidates(
        self,
        identity: Product,
        *,
        exclude_reference: UUID | IdentityReference | None = None,
        include_retired: bool = False,
        limit: int = 100,
        connection: Connection,
    ) -> CandidatePage[Product]:
        """Return bounded same-kind candidates for exact/normalized names."""

        if not isinstance(identity, Product):
            raise TypeError("ProductRepository requires a Product identity.")

        id_page = find_identity_candidate_ids(
            kind=IdentityKind.PRODUCT,
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
        product: Product,
        *,
        connection: Connection,
    ) -> None:

        if product.kind != IdentityKind.PRODUCT:
            raise ValueError(
                "ProductRepository can only persist PRODUCT identities."
            )

        identity_id = product.reference.value.bytes

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
                    product.kind.value,
                    product.lifecycle_state.value,
                    product.representations.canonical_name,
                ),
            )

            for alias in product.representations.aliases:
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

    def get_by_id(
        self,
        reference: UUID | IdentityReference,
        *,
        connection: Connection,
    ) -> Product | None:

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

            if identity_row["kind"] != IdentityKind.PRODUCT.value:
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

        try:
            identity_reference = IdentityReference(
                UUID(bytes=identity_row["identity_id"])
            )

            lifecycle_state = LifecycleState(
                identity_row["lifecycle_state"]
            )

        except (ValueError, TypeError) as exc:
            raise RepositoryIntegrityError(
                "Invalid persisted PRODUCT identity state."
            ) from exc

        return Product(
            representations=IdentityRepresentations(
                canonical_name=identity_row["canonical_name"],
                aliases=aliases,
            ),
            reference=identity_reference,
            lifecycle_state=lifecycle_state,
        )
