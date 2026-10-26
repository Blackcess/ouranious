"""Append-only persistence for Claim materialisation links."""

from datetime import timezone
from uuid import UUID

from pymysql.connections import Connection
from pymysql.err import IntegrityError

from domain_models.Provenance.materialisation import (
    ClaimMaterialisation,
    MaterialisationAction,
    MaterialisationOutcome,
    MaterialisationTargetKind,
)
from repositories.utils.errors import (
    RepositoryConflictError,
    RepositoryIntegrityError,
    translate_integrity_error,
)


class ClaimMaterialisationRepository:
    def create(
        self, materialisation: ClaimMaterialisation, *, connection: Connection
    ) -> None:
        if not isinstance(materialisation, ClaimMaterialisation):
            raise TypeError("materialisation must be a ClaimMaterialisation")
        is_identity = materialisation.target_kind is MaterialisationTargetKind.IDENTITY
        timestamp = materialisation.materialised_at.astimezone(
            timezone.utc
        ).replace(tzinfo=None)
        try:
            with connection.cursor() as cursor:
                cursor.execute(
                    """INSERT INTO claim_materialisations
                       (materialisation_id, claim_id, target_kind,
                        canonical_identity_id, canonical_relationship_id,
                        resolution_outcome, action, override_applied, materialised_at)
                       VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)""",
                    (
                        materialisation.reference.bytes,
                        materialisation.claim_reference.bytes,
                        materialisation.target_kind.value,
                        materialisation.target_reference.bytes if is_identity else None,
                        None if is_identity else materialisation.target_reference.bytes,
                        materialisation.outcome.value,
                        materialisation.action.value,
                        materialisation.override_applied,
                        timestamp,
                    ),
                )
        except IntegrityError as exc:
            translated = translate_integrity_error("Creating claim materialisation", exc)
            if isinstance(translated, RepositoryConflictError):
                raise translated from exc
            raise translated from exc

    def get_by_claim_reference(
        self, claim_reference: UUID, *, connection: Connection
    ) -> ClaimMaterialisation | None:
        if not isinstance(claim_reference, UUID):
            raise TypeError("claim_reference must be a UUID")
        with connection.cursor() as cursor:
            cursor.execute(
                """SELECT materialisation_id, claim_id, target_kind,
                          canonical_identity_id, canonical_relationship_id,
                          resolution_outcome, action, override_applied,
                          materialised_at
                   FROM claim_materialisations WHERE claim_id = %s""",
                (claim_reference.bytes,),
            )
            row = cursor.fetchone()
        if row is None:
            return None
        try:
            target_kind = MaterialisationTargetKind(row["target_kind"])
            target_bytes = (
                row["canonical_identity_id"]
                if target_kind is MaterialisationTargetKind.IDENTITY
                else row["canonical_relationship_id"]
            )
            materialised_at = row["materialised_at"]
            if materialised_at.tzinfo is None:
                materialised_at = materialised_at.replace(tzinfo=timezone.utc)
            else:
                materialised_at = materialised_at.astimezone(timezone.utc)
            return ClaimMaterialisation(
                reference=UUID(bytes=row["materialisation_id"]),
                claim_reference=UUID(bytes=row["claim_id"]),
                target_kind=target_kind,
                target_reference=UUID(bytes=target_bytes),
                outcome=MaterialisationOutcome(row["resolution_outcome"]),
                action=MaterialisationAction(row["action"]),
                override_applied=bool(row["override_applied"]),
                materialised_at=materialised_at,
            )
        except (ValueError, TypeError, KeyError, AttributeError) as exc:
            raise RepositoryIntegrityError(
                "Invalid persisted claim materialisation."
            ) from exc
