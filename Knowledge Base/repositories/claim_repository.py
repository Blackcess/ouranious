"""Persistence for claims and their one-to-one typed propositions."""

from datetime import timezone
from uuid import UUID

from pymysql.connections import Connection
from pymysql.err import IntegrityError

from application.persistence.typed_value_codec import ValueCodecError, dumps, loads
from domain_models.Identity_model.identity import IdentityKind, IdentityReference
from domain_models.Provenance.claim import Claim, ClaimStatus
from domain_models.Provenance.propositions import (
    IdentityAttributeProposition,
    IdentityProposalProposition,
    Proposition,
    RelationshipPropertyProposition,
    RelationshipProposition,
)
from domain_models.Provenance.source import SourceReference
from domain_models.relationship_models.relationship import RelationshipReference
from domain_models.relationship_models.relationship_types.relationship_types import RelationshipType
from repositories.utils.errors import (
    RepositoryConflictError,
    RepositoryIntegrityError,
    RepositoryNotFoundError,
    RepositoryReferenceError,
    translate_integrity_error,
)


_PROPOSITION_TAGS = {
    IdentityAttributeProposition: "identity_attribute",
    RelationshipProposition: "relationship",
    RelationshipPropertyProposition: "relationship_property",
    IdentityProposalProposition: "identity_proposal",
}
_SUBTYPE_TABLES = {
    "identity_attribute": "identity_attribute_propositions",
    "relationship": "relationship_propositions",
    "relationship_property": "relationship_property_propositions",
    "identity_proposal": "identity_proposal_propositions",
}


def _uuid_bytes(reference: UUID) -> bytes:
    if not isinstance(reference, UUID):
        raise TypeError("reference must be a UUID")
    return reference.bytes


def _as_utc(value):
    if value.tzinfo is None or value.utcoffset() is None:
        return value.replace(tzinfo=timezone.utc)
    return value.astimezone(timezone.utc)


def _json_value(value):
    try:
        return loads(value)
    except ValueCodecError as exc:
        raise RepositoryIntegrityError("Invalid typed value stored in claim proposition.") from exc


class ClaimRepository:
    """Claim persistence; canonical identities and relationships are untouched."""

    def get_by_reference_for_update(
        self, reference: UUID, *, connection: Connection
    ) -> Claim | None:
        """Load a Claim while holding its row lock through the transaction."""
        claim_id = _uuid_bytes(reference)
        with connection.cursor() as cursor:
            cursor.execute(
                "SELECT claim_id FROM claims WHERE claim_id = %s FOR UPDATE",
                (claim_id,),
            )
            row = cursor.fetchone()
        if row is None:
            return None
        return self.get_by_reference(reference, connection=connection)

    def create(self, claim: Claim, *, connection: Connection) -> None:
        if not isinstance(claim, Claim):
            raise TypeError("claim must be a Claim")
        proposition = claim.proposition
        tag = _PROPOSITION_TAGS.get(type(proposition))
        if tag is None:
            raise TypeError("Unsupported claim proposition type")
        claim_id = claim.reference.bytes
        created_at = claim.created_at.astimezone(timezone.utc).replace(tzinfo=None)
        try:
            with connection.cursor() as cursor:
                cursor.execute("SAVEPOINT provenance_claim_create")
                cursor.execute(
                    "INSERT INTO claims (claim_id, status, research_notes, created_at) VALUES (%s, %s, %s, %s)",
                    (claim_id, claim.status.value, claim.research_notes, created_at),
                )
                cursor.execute(
                    "INSERT INTO claim_propositions (claim_id, proposition_type) VALUES (%s, %s)",
                    (claim_id, tag),
                )
                self._insert_subtype(cursor, claim_id, tag, proposition)
                for source_ref in sorted(claim.source_references, key=lambda ref: str(ref.value)):
                    cursor.execute(
                        "INSERT INTO claim_sources (claim_id, source_id) VALUES (%s, %s)",
                        (claim_id, source_ref.value.bytes),
                    )
                cursor.execute("RELEASE SAVEPOINT provenance_claim_create")
        except Exception as exc:
            try:
                with connection.cursor() as cursor:
                    cursor.execute("ROLLBACK TO SAVEPOINT provenance_claim_create")
                    cursor.execute("RELEASE SAVEPOINT provenance_claim_create")
            except Exception:
                pass
            if isinstance(exc, IntegrityError):
                translated = translate_integrity_error("Creating claim", exc)
                if isinstance(translated, RepositoryReferenceError):
                    raise translated from exc
                if isinstance(translated, RepositoryConflictError):
                    raise translated from exc
                raise translated from exc
            raise

    def get_by_reference(self, reference: UUID, *, connection: Connection) -> Claim | None:
        claim_id = _uuid_bytes(reference)
        with connection.cursor() as cursor:
            cursor.execute(
                """SELECT c.claim_id, c.status, c.research_notes, c.created_at,
                          p.proposition_type
                   FROM claims c LEFT JOIN claim_propositions p ON p.claim_id = c.claim_id
                   WHERE c.claim_id = %s""",
                (claim_id,),
            )
            row = cursor.fetchone()
            if row is None:
                return None
            if row["proposition_type"] is None:
                raise RepositoryIntegrityError("Claim has no proposition discriminator.")
            proposition = self._read_proposition(cursor, claim_id, row["proposition_type"])
            cursor.execute("SELECT source_id FROM claim_sources WHERE claim_id = %s ORDER BY source_id", (claim_id,))
            source_references = {
                SourceReference(UUID(bytes=source_row["source_id"]))
                for source_row in cursor.fetchall()
            }
        try:
            return Claim(
                proposition=proposition,
                source_references=source_references,
                research_notes=row["research_notes"],
                reference=UUID(bytes=row["claim_id"]),
                status=ClaimStatus(row["status"]),
                created_at=_as_utc(row["created_at"]),
            )
        except (ValueError, TypeError, KeyError) as exc:
            if isinstance(exc, RepositoryIntegrityError):
                raise
            raise RepositoryIntegrityError("Invalid persisted claim record.") from exc

    def update(self, claim: Claim, *, connection: Connection) -> None:
        """Update mutable claim status, notes, and source links only."""
        if not isinstance(claim, Claim):
            raise TypeError("claim must be a Claim")
        claim_id = claim.reference.bytes
        with connection.cursor() as cursor:
            cursor.execute("SAVEPOINT provenance_claim_update")
            try:
                current = self.get_by_reference(claim.reference, connection=connection)
                if current is None:
                    raise RepositoryNotFoundError("Claim does not exist.")
                if current.status is not claim.status:
                    current.transition_to(claim.status)
                cursor.execute(
                    "UPDATE claims SET status = %s, research_notes = %s WHERE claim_id = %s",
                    (claim.status.value, claim.research_notes, claim_id),
                )
                cursor.execute("DELETE FROM claim_sources WHERE claim_id = %s", (claim_id,))
                for source_ref in claim.source_references:
                    cursor.execute(
                        "INSERT INTO claim_sources (claim_id, source_id) VALUES (%s, %s)",
                        (claim_id, source_ref.value.bytes),
                    )
                cursor.execute("RELEASE SAVEPOINT provenance_claim_update")
            except Exception as exc:
                cursor.execute("ROLLBACK TO SAVEPOINT provenance_claim_update")
                cursor.execute("RELEASE SAVEPOINT provenance_claim_update")
                if isinstance(exc, IntegrityError):
                    raise translate_integrity_error("Updating claim", exc) from exc
                raise

    def add_source(self, claim_reference: UUID, source_reference: SourceReference, *, connection: Connection) -> None:
        claim_id = _uuid_bytes(claim_reference)
        if not isinstance(source_reference, SourceReference):
            raise TypeError("source_reference must be a SourceReference")
        try:
            with connection.cursor() as cursor:
                cursor.execute(
                    """INSERT INTO claim_sources (claim_id, source_id) VALUES (%s, %s)
                       ON DUPLICATE KEY UPDATE claim_id = VALUES(claim_id)""",
                    (claim_id, source_reference.value.bytes),
                )
        except IntegrityError as exc:
            raise translate_integrity_error("Associating source with claim", exc) from exc

    def remove_source(self, claim_reference: UUID, source_reference: SourceReference, *, connection: Connection) -> None:
        claim_id = _uuid_bytes(claim_reference)
        if not isinstance(source_reference, SourceReference):
            raise TypeError("source_reference must be a SourceReference")
        with connection.cursor() as cursor:
            cursor.execute(
                "DELETE FROM claim_sources WHERE claim_id = %s AND source_id = %s",
                (claim_id, source_reference.value.bytes),
            )

    def _insert_subtype(self, cursor, claim_id: bytes, tag: str, proposition: Proposition) -> None:
        if tag == "identity_attribute":
            cursor.execute(
                "INSERT INTO identity_attribute_propositions (claim_id, identity_id, attribute_name, proposed_value) VALUES (%s, %s, %s, %s)",
                (claim_id, proposition.identity_reference.value.bytes, proposition.attribute_name, dumps(proposition.proposed_value)),
            )
        elif tag == "relationship":
            props = None if proposition.properties is None else dumps(proposition.properties)
            existing = proposition.existing_relationship_reference
            cursor.execute(
                """INSERT INTO relationship_propositions
                   (claim_id, source_identity_id, target_identity_id, relationship_type, existing_relationship_id, properties)
                   VALUES (%s, %s, %s, %s, %s, %s)""",
                (claim_id, proposition.source_reference.value.bytes, proposition.target_reference.value.bytes,
                 proposition.relationship_type.value, None if existing is None else existing.value.bytes, props),
            )
        elif tag == "relationship_property":
            cursor.execute(
                "INSERT INTO relationship_property_propositions (claim_id, relationship_id, property_name, proposed_value) VALUES (%s, %s, %s, %s)",
                (claim_id, proposition.relationship_reference.value.bytes, proposition.property_name, dumps(proposition.proposed_value)),
            )
        elif tag == "identity_proposal":
            cursor.execute(
                "INSERT INTO identity_proposal_propositions (claim_id, identity_kind, canonical_name, aliases, attributes) VALUES (%s, %s, %s, %s, %s)",
                (claim_id, proposition.identity_kind.value, proposition.canonical_name,
                 dumps(proposition.aliases), dumps(proposition.attributes)),
            )
        else:
            raise RepositoryIntegrityError(f"Unsupported proposition discriminator: {tag}")

    def _read_proposition(self, cursor, claim_id: bytes, tag: str) -> Proposition:
        table = _SUBTYPE_TABLES.get(tag)
        if table is None:
            raise RepositoryIntegrityError(f"Unknown proposition discriminator: {tag}")
        for other_tag, other_table in _SUBTYPE_TABLES.items():
            cursor.execute(f"SELECT 1 FROM {other_table} WHERE claim_id = %s", (claim_id,))
            exists = cursor.fetchone() is not None
            if other_tag == tag:
                if not exists:
                    raise RepositoryIntegrityError("Claim proposition subtype row is missing.")
            elif exists:
                raise RepositoryIntegrityError("Claim has mismatched proposition subtype rows.")
        cursor.execute(f"SELECT * FROM {table} WHERE claim_id = %s", (claim_id,))
        row = cursor.fetchone()
        if row is None:
            raise RepositoryIntegrityError("Claim proposition subtype row is missing.")
        try:
            if tag == "identity_attribute":
                return IdentityAttributeProposition(
                    IdentityReference(UUID(bytes=row["identity_id"])), row["attribute_name"], _json_value(row["proposed_value"])
                )
            if tag == "relationship":
                properties = None if row["properties"] is None else _json_value(row["properties"])
                existing_id = row["existing_relationship_id"]
                return RelationshipProposition(
                    IdentityReference(UUID(bytes=row["source_identity_id"])),
                    IdentityReference(UUID(bytes=row["target_identity_id"])),
                    RelationshipType(row["relationship_type"]),
                    properties,
                    None if existing_id is None else RelationshipReference(UUID(bytes=existing_id)),
                )
            if tag == "relationship_property":
                return RelationshipPropertyProposition(
                    RelationshipReference(UUID(bytes=row["relationship_id"])), row["property_name"], _json_value(row["proposed_value"])
                )
            if tag == "identity_proposal":
                aliases = _json_value(row["aliases"])
                attributes = _json_value(row["attributes"])
                if not isinstance(aliases, frozenset) or not isinstance(attributes, dict):
                    raise RepositoryIntegrityError("Identity proposal payload has invalid container types.")
                return IdentityProposalProposition(
                    IdentityKind(row["identity_kind"]), row["canonical_name"], aliases, attributes
                )
        except (ValueError, TypeError, KeyError, ValueCodecError) as exc:
            if isinstance(exc, RepositoryIntegrityError):
                raise
            raise RepositoryIntegrityError("Invalid persisted proposition subtype.") from exc
        raise RepositoryIntegrityError(f"Unknown proposition discriminator: {tag}")
