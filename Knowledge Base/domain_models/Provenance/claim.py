
# domain_models/provenance/claim.py

from datetime import datetime, timezone
from enum import Enum
from uuid import UUID, uuid4

from domain_models.Provenance.propositions import Proposition
from domain_models.Provenance.source import SourceReference
from domain_models.Provenance.propositions import (
    IdentityAttributeProposition,
    IdentityProposalProposition,
    Proposition,
    RelationshipPropertyProposition,
    RelationshipProposition,
)


class ClaimStatus(Enum):
    DRAFT = "draft"
    PENDING_REVIEW = "pending_review"
    ACCEPTED = "accepted"
    REJECTED = "rejected"
    DISPUTED = "disputed"
    NEEDS_RESEARCH = "needs_research"
    SUPERSEDED = "superseded"


class Claim:
    _ALLOWED_TRANSITIONS = {
        ClaimStatus.DRAFT: {
            ClaimStatus.PENDING_REVIEW,
            ClaimStatus.NEEDS_RESEARCH,
            ClaimStatus.SUPERSEDED,
        },
        ClaimStatus.PENDING_REVIEW: {
            ClaimStatus.ACCEPTED,
            ClaimStatus.REJECTED,
            ClaimStatus.DISPUTED,
            ClaimStatus.NEEDS_RESEARCH,
            ClaimStatus.SUPERSEDED,
        },
        ClaimStatus.NEEDS_RESEARCH: {
            ClaimStatus.PENDING_REVIEW,
            ClaimStatus.SUPERSEDED,
        },
        ClaimStatus.DISPUTED: {
            ClaimStatus.PENDING_REVIEW,
            ClaimStatus.ACCEPTED,
            ClaimStatus.REJECTED,
            ClaimStatus.SUPERSEDED,
        },
        ClaimStatus.ACCEPTED: {
            ClaimStatus.DISPUTED,
            ClaimStatus.SUPERSEDED,
        },
        ClaimStatus.REJECTED: {
            ClaimStatus.PENDING_REVIEW,
            ClaimStatus.SUPERSEDED,
        },
        ClaimStatus.SUPERSEDED: set(),
    }

    def __init__(
        self,
        *,
        proposition: Proposition,
        source_references: set[SourceReference] | None = None,
        research_notes: str = "",
        reference: UUID | None = None,
        status: ClaimStatus = ClaimStatus.DRAFT,
        created_at: datetime | None = None,
    ):
        if not isinstance(
            proposition,
            (
                IdentityAttributeProposition,
                RelationshipProposition,
                RelationshipPropertyProposition,
                IdentityProposalProposition,
            ),
        ):
            raise TypeError("proposition must be a supported Proposition")

        if not isinstance(research_notes, str):
            raise TypeError("research_notes must be a string")

        if not isinstance(status, ClaimStatus):
            raise TypeError("status must be a ClaimStatus")

        if reference is not None and not isinstance(reference, UUID):
            raise TypeError("reference must be a UUID or None")

        sources = set(source_references or set())

        if any(
            not isinstance(source, SourceReference)
            for source in sources
        ):
            raise TypeError(
                "source_references must contain SourceReference objects"
            )

        timestamp = created_at or datetime.now(timezone.utc)

        if not isinstance(timestamp, datetime):
            raise TypeError("created_at must be a datetime")

        if timestamp.tzinfo is None:
            raise ValueError("created_at must be timezone-aware")

        self._reference = reference or uuid4()
        self._proposition = proposition
        self._source_references = sources
        self._research_notes = research_notes
        self._status = status
        self._created_at = timestamp

    @property
    def reference(self) -> UUID:
        return self._reference

    @property
    def proposition(self) -> Proposition:
        return self._proposition

    @property
    def source_references(self) -> frozenset[SourceReference]:
        return frozenset(self._source_references)

    @property
    def research_notes(self) -> str:
        return self._research_notes

    @property
    def status(self) -> ClaimStatus:
        return self._status

    @property
    def created_at(self) -> datetime:
        return self._created_at

    def add_source(self, source_reference: SourceReference) -> None:
        if not isinstance(source_reference, SourceReference):
            raise TypeError(
                "source_reference must be a SourceReference"
            )
        self._source_references.add(source_reference)

    def remove_source(self, source_reference: SourceReference) -> None:
        self._source_references.discard(source_reference)

    def update_research_notes(self, notes: str) -> None:
        if not isinstance(notes, str):
            raise TypeError("notes must be a string")
        self._research_notes = notes

    def transition_to(self, new_status: ClaimStatus) -> None:
        if not isinstance(new_status, ClaimStatus):
            raise TypeError("new_status must be a ClaimStatus")

        allowed = self._ALLOWED_TRANSITIONS[self._status]

        if new_status not in allowed:
            raise ValueError(
                f"Invalid claim status transition: "
                f"{self._status.value} -> {new_status.value}"
            )

        self._status = new_status
