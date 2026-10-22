"""Application orchestration for identity duplicate resolution."""

from typing import Protocol
from uuid import UUID

from pymysql.connections import Connection

from application.resolution.identity.contracts import (
    CandidateMatch,
    CandidateMatchKind,
    IdentityResolutionRequest,
    IdentityResolutionResult,
    ResolutionOutcome,
)
from application.resolution.identity.registry import (
    IdentityStrategyRegistry,
    build_default_identity_strategy_registry,
)
from domain_models.Identity_model.identity import (
    Identity,
    IdentityKind,
    IdentityReference,
)
from infrastructure.database.connection import DatabaseManager
from repositories.industry_repository import IndustryRepository
from repositories.organisation_repository import OrganisationRepository
from repositories.person_repository import PersonRepository
from repositories.place_repository import PlaceRepository
from repositories.product_repository import ProductRepository
from repositories.technology_repository import TechnologyRepository
from repositories.utils.candidate_page import CandidatePage


class IdentityCandidateRepository(Protocol):
    def find_candidates(
        self,
        identity: Identity,
        *,
        exclude_reference: UUID | IdentityReference | None,
        include_retired: bool,
        limit: int,
        connection: Connection,
    ) -> CandidatePage[Identity]:
        ...


class IdentityResolutionService:
    """Selects candidates, delegates kind matching, and aggregates outcomes."""

    def __init__(
        self,
        *,
        person_repository: PersonRepository,
        organisation_repository: OrganisationRepository,
        place_repository: PlaceRepository,
        industry_repository: IndustryRepository,
        product_repository: ProductRepository,
        technology_repository: TechnologyRepository,
        database_manager: DatabaseManager,
        strategy_registry: IdentityStrategyRegistry | None = None,
    ):
        self._repositories: dict[IdentityKind, IdentityCandidateRepository] = {
            IdentityKind.PERSON: person_repository,
            IdentityKind.ORGANISATION: organisation_repository,
            IdentityKind.PLACE: place_repository,
            IdentityKind.INDUSTRY: industry_repository,
            IdentityKind.PRODUCT: product_repository,
            IdentityKind.TECHNOLOGY: technology_repository,
        }
        self._database_manager = database_manager
        self._strategy_registry = (
            strategy_registry or build_default_identity_strategy_registry()
        )
        self._strategy_registry.validate_complete()

    def resolve(
        self,
        request: IdentityResolutionRequest,
    ) -> IdentityResolutionResult:
        if not isinstance(request, IdentityResolutionRequest):
            raise TypeError("request must be an IdentityResolutionRequest")

        identity = request.identity
        strategy = self._strategy_registry.get(identity.kind)
        repository = self._repositories.get(identity.kind)
        if repository is None:
            raise ValueError(
                f"No candidate repository is configured for {identity.kind.value}"
            )

        # Exclude the represented record by default when resolving an existing
        # identity; callers can explicitly choose a different reference.
        excluded_reference = request.exclude_reference or identity.reference
        with self._database_manager.connection() as connection:
            candidate_page = repository.find_candidates(
                identity,
                exclude_reference=excluded_reference,
                include_retired=request.include_retired,
                limit=request.candidate_limit,
                connection=connection,
            )

        matches: list[CandidateMatch] = []
        for candidate in candidate_page.items:
            comparison = strategy.compare(identity, candidate)
            if comparison.kind is not CandidateMatchKind.NON_MATCH:
                matches.append(
                    CandidateMatch(
                        identity=candidate,
                        kind=comparison.kind,
                        evidence=comparison.evidence,
                    )
                )

        exact_matches = [
            match
            for match in matches
            if match.kind is CandidateMatchKind.EXACT_MATCH
        ]
        possible_matches = [
            match
            for match in matches
            if match.kind is CandidateMatchKind.POSSIBLE_DUPLICATE
        ]

        if (
            len(exact_matches) == 1
            and not possible_matches
            and not candidate_page.truncated
        ):
            return IdentityResolutionResult(
                outcome=ResolutionOutcome.EXACT_MATCH,
                matches=tuple(exact_matches),
            )

        if matches or candidate_page.truncated:
            return IdentityResolutionResult(
                outcome=ResolutionOutcome.POSSIBLE_DUPLICATE,
                matches=tuple(matches),
                ambiguous=True,
                candidates_truncated=candidate_page.truncated,
            )

        return IdentityResolutionResult(
            outcome=ResolutionOutcome.NO_MATCH,
            candidates_truncated=False,
        )
