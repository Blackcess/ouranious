"""Immutable record linking an accepted Claim to a canonical graph record."""

from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum
from uuid import UUID, uuid4


class MaterialisationTargetKind(Enum):
    IDENTITY = "identity"
    RELATIONSHIP = "relationship"


class MaterialisationOutcome(Enum):
    NO_MATCH = "no_match"
    EXACT_MATCH = "exact_match"
    POSSIBLE_DUPLICATE = "possible_duplicate"


class MaterialisationAction(Enum):
    CREATED = "created"
    LINKED = "linked"


@dataclass(frozen=True)
class ClaimMaterialisation:
    claim_reference: UUID
    target_kind: MaterialisationTargetKind
    target_reference: UUID
    outcome: MaterialisationOutcome
    action: MaterialisationAction
    override_applied: bool = False
    reference: UUID = field(default_factory=uuid4)
    materialised_at: datetime = field(
        default_factory=lambda: datetime.now(timezone.utc)
    )

    def __post_init__(self) -> None:
        if not isinstance(self.claim_reference, UUID):
            raise TypeError("claim_reference must be a UUID")
        if not isinstance(self.reference, UUID):
            raise TypeError("reference must be a UUID")
        if not isinstance(self.target_reference, UUID):
            raise TypeError("target_reference must be a UUID")
        if not isinstance(self.target_kind, MaterialisationTargetKind):
            raise TypeError("target_kind must be a MaterialisationTargetKind")
        if not isinstance(self.outcome, MaterialisationOutcome):
            raise TypeError("outcome must be a MaterialisationOutcome")
        if not isinstance(self.action, MaterialisationAction):
            raise TypeError("action must be a MaterialisationAction")
        if not isinstance(self.override_applied, bool):
            raise TypeError("override_applied must be a boolean")
        if not isinstance(self.materialised_at, datetime):
            raise TypeError("materialised_at must be a datetime")
        if (
            self.materialised_at.tzinfo is None
            or self.materialised_at.utcoffset() is None
        ):
            raise ValueError("materialised_at must be timezone-aware")
        if self.action is MaterialisationAction.LINKED and self.outcome is not MaterialisationOutcome.EXACT_MATCH:
            raise ValueError("linked materialisations require an exact match")
        if self.action is MaterialisationAction.CREATED and self.outcome is MaterialisationOutcome.EXACT_MATCH:
            raise ValueError("exact matches must link to the existing record")
        if self.override_applied and (
            self.action is not MaterialisationAction.CREATED
            or self.outcome is not MaterialisationOutcome.POSSIBLE_DUPLICATE
        ):
            raise ValueError("override_applied requires a possible-duplicate creation")
