
# domain_models/provenance/verification_assessment.py

from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum
from uuid import UUID, uuid4


class AssessmentOutcome(Enum):
    ACCEPT = "accept"
    REJECT = "reject"
    REQUEST_MORE_RESEARCH = "request_more_research"
    FLAG_DISPUTE = "flag_dispute"


@dataclass(frozen=True)
class VerificationAssessment:
    claim_reference: UUID
    outcome: AssessmentOutcome
    rationale: str
    assessed_by: str
    reference: UUID = field(default_factory=uuid4)
    assessed_at: datetime = field(
        default_factory=lambda: datetime.now(timezone.utc)
    )
    review_process: str | None = None

    def __post_init__(self) -> None:
        if not isinstance(self.claim_reference, UUID):
            raise TypeError("claim_reference must be a UUID")

        if not isinstance(self.reference, UUID):
            raise TypeError("reference must be a UUID")

        if not isinstance(self.outcome, AssessmentOutcome):
            raise TypeError(
                "outcome must be an AssessmentOutcome"
            )

        if (
            not isinstance(self.rationale, str)
            or not self.rationale.strip()
        ):
            raise ValueError("rationale cannot be empty")

        if (
            not isinstance(self.assessed_by, str)
            or not self.assessed_by.strip()
        ):
            raise ValueError("assessed_by cannot be empty")

        if not isinstance(self.assessed_at, datetime):
            raise TypeError("assessed_at must be a datetime")

        if self.assessed_at.tzinfo is None:
            raise ValueError(
                "assessed_at must be timezone-aware"
            )

        if self.review_process is not None:
            if (
                not isinstance(self.review_process, str)
                or not self.review_process.strip()
            ):
                raise ValueError(
                    "review_process must be non-empty when provided"
                )
