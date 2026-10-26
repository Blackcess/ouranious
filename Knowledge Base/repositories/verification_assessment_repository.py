"""Append-only persistence for verification assessment history."""

from datetime import timezone
from uuid import UUID

from pymysql.connections import Connection
from pymysql.err import IntegrityError

from domain_models.Provenance.verification_assessment import (
    AssessmentOutcome,
    VerificationAssessment,
)
from repositories.utils.errors import RepositoryIntegrityError, translate_integrity_error


def _uuid_bytes(reference: UUID) -> bytes:
    if not isinstance(reference, UUID):
        raise TypeError("reference must be a UUID")
    return reference.bytes


def _from_row(row) -> VerificationAssessment:
    try:
        assessed_at = row["assessed_at"]
        if assessed_at.tzinfo is None:
            assessed_at = assessed_at.replace(tzinfo=timezone.utc)
        else:
            assessed_at = assessed_at.astimezone(timezone.utc)
        return VerificationAssessment(
            claim_reference=UUID(bytes=row["claim_id"]),
            outcome=AssessmentOutcome(row["outcome"]),
            rationale=row["rationale"],
            assessed_by=row["assessed_by"],
            reference=UUID(bytes=row["assessment_id"]),
            assessed_at=assessed_at,
            review_process=row["review_process"],
        )
    except (ValueError, TypeError, KeyError, AttributeError) as exc:
        raise RepositoryIntegrityError("Invalid persisted verification assessment.") from exc


class VerificationAssessmentRepository:
    """Creates and reads assessments; existing events are never updated/deleted."""

    def create(self, assessment: VerificationAssessment, *, connection: Connection) -> None:
        if not isinstance(assessment, VerificationAssessment):
            raise TypeError("assessment must be a VerificationAssessment")
        assessed_at = assessment.assessed_at.astimezone(timezone.utc).replace(tzinfo=None)
        try:
            with connection.cursor() as cursor:
                cursor.execute(
                    """INSERT INTO verification_assessments
                       (assessment_id, claim_id, outcome, rationale, assessed_by, assessed_at, review_process)
                       VALUES (%s, %s, %s, %s, %s, %s, %s)""",
                    (
                        assessment.reference.bytes,
                        assessment.claim_reference.bytes,
                        assessment.outcome.value,
                        assessment.rationale,
                        assessment.assessed_by,
                        assessed_at,
                        assessment.review_process,
                    ),
                )
        except IntegrityError as exc:
            raise translate_integrity_error("Creating verification assessment", exc) from exc

    def get_by_reference(self, reference: UUID, *, connection: Connection) -> VerificationAssessment | None:
        assessment_id = _uuid_bytes(reference)
        with connection.cursor() as cursor:
            cursor.execute(
                """SELECT assessment_id, claim_id, outcome, rationale, assessed_by,
                          assessed_at, review_process
                   FROM verification_assessments WHERE assessment_id = %s""",
                (assessment_id,),
            )
            row = cursor.fetchone()
        return None if row is None else _from_row(row)

    def get_by_claim_reference(self, claim_reference: UUID, *, connection: Connection) -> list[VerificationAssessment]:
        claim_id = _uuid_bytes(claim_reference)
        with connection.cursor() as cursor:
            cursor.execute(
                """SELECT assessment_id, claim_id, outcome, rationale, assessed_by,
                          assessed_at, review_process
                   FROM verification_assessments
                   WHERE claim_id = %s
                   ORDER BY assessed_at, assessment_id""",
                (claim_id,),
            )
            rows = cursor.fetchall()
        return [_from_row(row) for row in rows]
