"""Data contracts for identity resolution.

These contracts describe requests and decisions. They intentionally contain no
matching or persistence policy; those belong to strategies and services.
"""

from dataclasses import dataclass
from enum import Enum

from domain_models.Identity_model.identity import Identity, IdentityReference


class MatchEvidenceStrength(Enum):
    """Qualitative evidence labels; these are not confidence scores."""

    DETERMINISTIC = "deterministic"
    SUPPORTING = "supporting"
    CONFLICTING = "conflicting"


@dataclass(frozen=True)
class MatchEvidence:
    """One explainable observation made while comparing two identities."""

    rule: str
    strength: MatchEvidenceStrength
    input_value: object | None = None
    candidate_value: object | None = None
    detail: str | None = None


class CandidateMatchKind(Enum):
    """Comparison result for one candidate."""

    EXACT_MATCH = "exact_match"
    POSSIBLE_DUPLICATE = "possible_duplicate"
    NON_MATCH = "non_match"


class ResolutionOutcome(Enum):
    """Aggregate resolution result across all retrieved candidates."""

    EXACT_MATCH = "exact_match"
    POSSIBLE_DUPLICATE = "possible_duplicate"
    NO_MATCH = "no_match"


@dataclass(frozen=True)
class CandidateComparison:
    """Strategy decision for a single candidate and its supporting evidence."""

    kind: CandidateMatchKind
    evidence: tuple[MatchEvidence, ...] = ()

    def __post_init__(self) -> None:
        if not isinstance(self.kind, CandidateMatchKind):
            raise TypeError("kind must be a CandidateMatchKind")


@dataclass(frozen=True)
class CandidateMatch:
    """A candidate identity and the evidence associated with it."""

    identity: Identity
    kind: CandidateMatchKind
    evidence: tuple[MatchEvidence, ...]

    def __post_init__(self) -> None:
        if not isinstance(self.identity, Identity):
            raise TypeError("identity must be an Identity instance")
        if not isinstance(self.kind, CandidateMatchKind):
            raise TypeError("kind must be a CandidateMatchKind")
        if self.kind is CandidateMatchKind.NON_MATCH:
            raise ValueError("NON_MATCH candidates must not be included in matches")


@dataclass(frozen=True)
class IdentityResolutionRequest:
    """Input to identity matching; the identity itself remains the domain model."""

    identity: Identity
    exclude_reference: IdentityReference | None = None
    include_retired: bool = False
    candidate_limit: int = 100

    def __post_init__(self) -> None:
        if not isinstance(self.identity, Identity):
            raise TypeError("identity must be an Identity instance")
        if self.exclude_reference is not None and not isinstance(
            self.exclude_reference, IdentityReference
        ):
            raise TypeError("exclude_reference must be an IdentityReference or None")
        if not isinstance(self.include_retired, bool):
            raise TypeError("include_retired must be a boolean")
        if isinstance(self.candidate_limit, bool) or not isinstance(
            self.candidate_limit, int
        ):
            raise TypeError("candidate_limit must be an integer")
        if self.candidate_limit <= 0:
            raise ValueError("candidate_limit must be greater than zero")


@dataclass(frozen=True)
class IdentityResolutionResult:
    """Outcome plus all matching candidates and any unresolved ambiguity."""

    outcome: ResolutionOutcome
    matches: tuple[CandidateMatch, ...] = ()
    ambiguous: bool = False
    candidates_truncated: bool = False

    def __post_init__(self) -> None:
        if not isinstance(self.outcome, ResolutionOutcome):
            raise TypeError("outcome must be a ResolutionOutcome")
        if not isinstance(self.ambiguous, bool):
            raise TypeError("ambiguous must be a boolean")
        if not isinstance(self.candidates_truncated, bool):
            raise TypeError("candidates_truncated must be a boolean")
        if self.outcome is ResolutionOutcome.NO_MATCH and self.matches:
            raise ValueError("NO_MATCH results cannot contain matches")
        if (
            self.outcome is ResolutionOutcome.POSSIBLE_DUPLICATE
            and not self.matches
            and not self.candidates_truncated
        ):
            raise ValueError(
                "POSSIBLE_DUPLICATE requires matches or a truncated candidate set"
            )
        if self.outcome is ResolutionOutcome.EXACT_MATCH:
            if (
                len(self.matches) != 1
                or self.ambiguous
                or self.candidates_truncated
                or self.matches[0].kind is not CandidateMatchKind.EXACT_MATCH
            ):
                raise ValueError(
                    "EXACT_MATCH requires one exact, unambiguous, complete candidate set"
                )
