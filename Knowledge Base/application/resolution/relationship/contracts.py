"""Contracts for relationship duplicate resolution."""

from dataclasses import dataclass
from enum import Enum

from domain_models.relationship_models.relationship import Relationship


class RelationshipResolutionOutcome(Enum):
    EXACT_MATCH = "exact_match"
    POSSIBLE_DUPLICATE = "possible_duplicate"
    NO_MATCH = "no_match"


class RelationshipMatchEvidenceKind(Enum):
    PROPERTIES_EQUAL = "properties_equal"
    OPTIONAL_PROPERTIES_MISSING = "optional_properties_missing"


@dataclass(frozen=True)
class RelationshipMatchEvidence:
    kind: RelationshipMatchEvidenceKind
    property_paths: tuple[str, ...] = ()


@dataclass(frozen=True)
class RelationshipCandidateMatch:
    relationship: Relationship
    evidence: tuple[RelationshipMatchEvidence, ...]

    def __post_init__(self) -> None:
        if not isinstance(self.relationship, Relationship):
            raise TypeError("relationship must be a Relationship instance")


@dataclass(frozen=True)
class RelationshipResolutionRequest:
    relationship: Relationship
    candidate_limit: int = 100

    def __post_init__(self) -> None:
        if not isinstance(self.relationship, Relationship):
            raise TypeError("relationship must be a Relationship instance")
        if isinstance(self.candidate_limit, bool) or not isinstance(
            self.candidate_limit, int
        ):
            raise TypeError("candidate_limit must be an integer")
        if self.candidate_limit <= 0:
            raise ValueError("candidate_limit must be greater than zero")


@dataclass(frozen=True)
class RelationshipResolutionResult:
    outcome: RelationshipResolutionOutcome
    matches: tuple[RelationshipCandidateMatch, ...] = ()
    ambiguous: bool = False
    candidates_truncated: bool = False

    def __post_init__(self) -> None:
        if not isinstance(self.outcome, RelationshipResolutionOutcome):
            raise TypeError("outcome must be a RelationshipResolutionOutcome")
        if not isinstance(self.ambiguous, bool):
            raise TypeError("ambiguous must be a boolean")
        if not isinstance(self.candidates_truncated, bool):
            raise TypeError("candidates_truncated must be a boolean")
        if self.outcome is RelationshipResolutionOutcome.NO_MATCH and self.matches:
            raise ValueError("NO_MATCH results cannot contain matches")
        if (
            self.outcome is RelationshipResolutionOutcome.POSSIBLE_DUPLICATE
            and not self.matches
            and not self.candidates_truncated
        ):
            raise ValueError(
                "POSSIBLE_DUPLICATE requires matches or a truncated candidate set"
            )
        if self.outcome is RelationshipResolutionOutcome.EXACT_MATCH:
            if len(self.matches) != 1 or self.ambiguous or self.candidates_truncated:
                raise ValueError(
                    "EXACT_MATCH requires one unambiguous candidate and a complete candidate set"
                )
