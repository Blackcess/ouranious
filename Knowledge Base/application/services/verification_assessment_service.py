"""Application operations for immutable verification-assessment history."""

from uuid import UUID

from domain_models.Provenance.claim import Claim, ClaimStatus
from domain_models.Provenance.verification_assessment import VerificationAssessment
from infrastructure.database.connection import DatabaseManager
from repositories.claim_repository import ClaimRepository
from repositories.utils.errors import RepositoryNotFoundError
from repositories.verification_assessment_repository import (
    VerificationAssessmentRepository,
)


class VerificationAssessmentService:
    """Records assessment events without inferring claim-status transitions."""

    def __init__(
        self,
        *,
        assessment_repository: VerificationAssessmentRepository,
        claim_repository: ClaimRepository,
        database_manager: DatabaseManager,
    ):
        self._assessment_repository = assessment_repository
        self._claim_repository = claim_repository
        self._database_manager = database_manager

    def create(self, assessment: VerificationAssessment) -> VerificationAssessment:
        """Append one assessment event; never overwrite prior assessments."""
        with self._database_manager.transaction() as connection:
            self._assessment_repository.create(assessment, connection=connection)
        return assessment

    def create_and_transition_claim(
        self,
        assessment: VerificationAssessment,
        *,
        new_status: ClaimStatus,
    ) -> tuple[VerificationAssessment, Claim]:
        """Atomically record an assessment and an explicitly requested status.

        No mapping from assessment outcome to claim status is assumed. The
        caller selects the status, and Claim.transition_to enforces its allowed
        lifecycle before either write is committed.
        """
        with self._database_manager.transaction() as connection:
            claim = self._claim_repository.get_by_reference(
                assessment.claim_reference, connection=connection
            )
            if claim is None:
                raise RepositoryNotFoundError(
                    f"Claim {assessment.claim_reference} does not exist."
                )
            claim.transition_to(new_status)
            self._assessment_repository.create(assessment, connection=connection)
            self._claim_repository.update(claim, connection=connection)
        return assessment, claim

    def get_by_reference(self, reference: UUID) -> VerificationAssessment | None:
        with self._database_manager.connection() as connection:
            return self._assessment_repository.get_by_reference(
                reference, connection=connection
            )

    def get_by_claim_reference(
        self, claim_reference: UUID
    ) -> list[VerificationAssessment]:
        with self._database_manager.connection() as connection:
            return self._assessment_repository.get_by_claim_reference(
                claim_reference, connection=connection
            )
