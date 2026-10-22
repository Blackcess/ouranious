"""Relationship-resolution contracts and property canonicalization."""

from application.resolution.relationship.canonicalization import (
    canonicalize_relationship_properties,
)
from application.resolution.relationship.contracts import (
    RelationshipCandidateMatch,
    RelationshipMatchEvidence,
    RelationshipMatchEvidenceKind,
    RelationshipResolutionOutcome,
    RelationshipResolutionRequest,
    RelationshipResolutionResult,
)

__all__ = [
    "RelationshipCandidateMatch",
    "RelationshipMatchEvidence",
    "RelationshipMatchEvidenceKind",
    "RelationshipResolutionOutcome",
    "RelationshipResolutionRequest",
    "RelationshipResolutionResult",
    "canonicalize_relationship_properties",
]
