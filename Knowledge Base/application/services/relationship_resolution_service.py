"""Application service for type-aware relationship duplicate resolution."""

from pymysql.connections import Connection

from application.resolution.relationship.canonicalization import (
    canonicalize_relationship_properties,
    compare_canonical_properties,
)
from application.resolution.relationship.contracts import (
    RelationshipCandidateMatch,
    RelationshipMatchEvidence,
    RelationshipMatchEvidenceKind,
    RelationshipResolutionOutcome,
    RelationshipResolutionRequest,
    RelationshipResolutionResult,
)
from application.services.identity_resolver import IdentityResolver
from domain_models.Identity_model.identity import Identity
from domain_models.relationship_models.relationship import Relationship
from repositories.relationship_repository import RelationshipRepository


class RelationshipEndpointNotFoundError(LookupError):
    """Raised when endpoint references are missing or resolve to another kind."""


class RelationshipResolutionService:
    """Find equivalent relationships using the caller's transaction."""

    def __init__(
        self,
        *,
        relationship_repository: RelationshipRepository,
        identity_resolver: IdentityResolver | None = None,
        require_persisted_endpoints: bool = False,
    ):
        if not isinstance(require_persisted_endpoints, bool):
            raise TypeError("require_persisted_endpoints must be a boolean")
        if require_persisted_endpoints and identity_resolver is None:
            raise ValueError(
                "identity_resolver is required when persisted endpoint checks are enabled"
            )
        self._relationship_repository = relationship_repository
        self._identity_resolver = identity_resolver
        self._require_persisted_endpoints = require_persisted_endpoints

    def resolve(
        self,
        request: RelationshipResolutionRequest,
        *,
        connection: Connection,
    ) -> RelationshipResolutionResult:
        if not isinstance(request, RelationshipResolutionRequest):
            raise TypeError("request must be a RelationshipResolutionRequest")

        relationship = request.relationship
        if not isinstance(relationship, Relationship):
            raise TypeError("request must contain a Relationship instance")

        if self._require_persisted_endpoints:
            self._validate_persisted_endpoints(
                relationship,
                connection=connection,
            )

        requested_properties = canonicalize_relationship_properties(relationship)
        candidate_page = self._relationship_repository.find_candidates(
            source_reference=relationship.get_source().reference,
            target_reference=relationship.get_target().reference,
            relationship_type=relationship.get_type(),
            limit=request.candidate_limit,
            connection=connection,
        )

        matches: list[RelationshipCandidateMatch] = []
        exact_matches = 0
        possible_matches = 0

        for candidate in candidate_page.items:
            if not self._same_base_key(relationship, candidate):
                continue
            candidate_properties = canonicalize_relationship_properties(candidate)
            has_conflict, missing_paths = compare_canonical_properties(
                requested_properties,
                candidate_properties,
            )
            if has_conflict:
                # Populated conflicts preserve separate events or states.
                continue
            if missing_paths:
                possible_matches += 1
                matches.append(
                    RelationshipCandidateMatch(
                        relationship=candidate,
                        evidence=(
                            RelationshipMatchEvidence(
                                kind=(
                                    RelationshipMatchEvidenceKind.OPTIONAL_PROPERTIES_MISSING
                                ),
                                property_paths=missing_paths,
                            ),
                        ),
                    )
                )
            else:
                exact_matches += 1
                matches.append(
                    RelationshipCandidateMatch(
                        relationship=candidate,
                        evidence=(
                            RelationshipMatchEvidence(
                                kind=RelationshipMatchEvidenceKind.PROPERTIES_EQUAL,
                            ),
                        ),
                    )
                )

        if (
            exact_matches == 1
            and possible_matches == 0
            and not candidate_page.truncated
        ):
            return RelationshipResolutionResult(
                outcome=RelationshipResolutionOutcome.EXACT_MATCH,
                matches=tuple(matches),
            )

        if matches or candidate_page.truncated:
            return RelationshipResolutionResult(
                outcome=RelationshipResolutionOutcome.POSSIBLE_DUPLICATE,
                matches=tuple(matches),
                ambiguous=True,
                candidates_truncated=candidate_page.truncated,
            )

        return RelationshipResolutionResult(
            outcome=RelationshipResolutionOutcome.NO_MATCH,
        )

    def _validate_persisted_endpoints(
        self,
        relationship: Relationship,
        *,
        connection: Connection,
    ) -> None:
        if self._identity_resolver is None:
            raise RuntimeError("Persisted endpoint checks require an IdentityResolver")
        for endpoint_name, endpoint in (
            ("source", relationship.get_source()),
            ("target", relationship.get_target()),
        ):
            resolved = self._identity_resolver.get_by_id(
                endpoint.reference,
                connection=connection,
            )
            if resolved is None:
                raise RelationshipEndpointNotFoundError(
                    f"Relationship {endpoint_name} identity "
                    f"{endpoint.reference.value} is not persisted"
                )
            if not isinstance(resolved, Identity) or resolved.kind is not endpoint.kind:
                raise RelationshipEndpointNotFoundError(
                    f"Persisted relationship {endpoint_name} reference resolves "
                    "to a different identity kind"
                )

    @staticmethod
    def _same_base_key(
        requested: Relationship,
        candidate: Relationship,
    ) -> bool:
        return (
            candidate.get_source().reference.value
            == requested.get_source().reference.value
            and candidate.get_target().reference.value
            == requested.get_target().reference.value
            and candidate.get_type() is requested.get_type()
        )
