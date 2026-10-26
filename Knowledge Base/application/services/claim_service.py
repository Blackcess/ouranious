"""Application operations for claims and their source associations."""

from uuid import UUID

from domain_models.Provenance.claim import Claim, ClaimStatus
from domain_models.Provenance.propositions import (
    IdentityAttributeProposition,
    RelationshipPropertyProposition,
    RelationshipProposition,
)
from domain_models.Provenance.source import SourceReference
from domain_models.relationship_models.relationship_types.relationship_type_specification import (
    specification_registry,
)
from infrastructure.database.connection import DatabaseManager
from repositories.claim_repository import ClaimRepository
from repositories.relationship_repository import RelationshipRepository
from repositories.utils.errors import RepositoryNotFoundError
from application.services.identity_resolver import IdentityResolver


class ClaimService:
    """Coordinates claim persistence while leaving canonical graph state alone."""

    def __init__(
        self,
        *,
        claim_repository: ClaimRepository,
        database_manager: DatabaseManager,
        identity_resolver: IdentityResolver,
        relationship_repository: RelationshipRepository,
    ):
        self._claim_repository = claim_repository
        self._database_manager = database_manager
        self._identity_resolver = identity_resolver
        self._relationship_repository = relationship_repository

    def create(self, claim: Claim) -> Claim:
        """Atomically persist a claim, its typed proposition, and source links."""
        with self._database_manager.transaction() as connection:
            self._validate_canonical_references(claim, connection=connection)
            self._claim_repository.create(claim, connection=connection)
        return claim

    def get_by_reference(self, reference: UUID) -> Claim | None:
        with self._database_manager.connection() as connection:
            return self._claim_repository.get_by_reference(
                reference, connection=connection
            )

    def update(self, claim: Claim) -> Claim:
        """Persist mutable claim state; proposition identity remains unchanged."""
        with self._database_manager.transaction() as connection:
            self._claim_repository.update(claim, connection=connection)
        return claim

    def add_source(
        self, claim_reference: UUID, source_reference: SourceReference
    ) -> None:
        with self._database_manager.transaction() as connection:
            self._claim_repository.add_source(
                claim_reference, source_reference, connection=connection
            )

    def remove_source(
        self, claim_reference: UUID, source_reference: SourceReference
    ) -> None:
        with self._database_manager.transaction() as connection:
            self._claim_repository.remove_source(
                claim_reference, source_reference, connection=connection
            )

    def transition_status(self, reference: UUID, new_status: ClaimStatus) -> Claim:
        """Transition a claim using its domain rules and persist atomically."""
        with self._database_manager.transaction() as connection:
            claim = self._claim_repository.get_by_reference(
                reference, connection=connection
            )
            if claim is None:
                raise RepositoryNotFoundError(f"Claim {reference} does not exist.")
            claim.transition_to(new_status)
            self._claim_repository.update(claim, connection=connection)
        return claim

    def _validate_canonical_references(self, claim: Claim, *, connection) -> None:
        proposition = claim.proposition
        if isinstance(proposition, IdentityAttributeProposition):
            if self._identity_resolver.get_by_id(
                proposition.identity_reference, connection=connection
            ) is None:
                raise RepositoryNotFoundError(
                    f"Identity {proposition.identity_reference.value} does not exist."
                )
            return

        if isinstance(proposition, RelationshipPropertyProposition):
            if self._relationship_repository.get_by_id(
                proposition.relationship_reference, connection=connection
            ) is None:
                raise RepositoryNotFoundError(
                    "The referenced canonical relationship does not exist."
                )
            return

        if not isinstance(proposition, RelationshipProposition):
            return

        source = self._identity_resolver.get_by_id(
            proposition.source_reference, connection=connection
        )
        target = self._identity_resolver.get_by_id(
            proposition.target_reference, connection=connection
        )
        if source is None or target is None:
            missing = proposition.source_reference if source is None else proposition.target_reference
            raise RepositoryNotFoundError(
                f"Identity {missing.value} does not exist."
            )

        specification = specification_registry.get(proposition.relationship_type)
        if specification is None:
            raise ValueError(
                f"Unsupported relationship type: {proposition.relationship_type.value}"
            )
        if (
            source.kind is not specification.allowed_source
            or target.kind is not specification.allowed_target
        ):
            raise ValueError(
                f"{proposition.relationship_type.value} does not permit "
                f"{source.kind.value} -> {target.kind.value} endpoints."
            )

        existing_reference = proposition.existing_relationship_reference
        if existing_reference is not None:
            existing = self._relationship_repository.get_by_id(
                existing_reference, connection=connection
            )
            if existing is None:
                raise RepositoryNotFoundError(
                    f"Relationship {existing_reference.value} does not exist."
                )
            if (
                existing.get_source().reference != proposition.source_reference
                or existing.get_target().reference != proposition.target_reference
                or existing.get_type() is not proposition.relationship_type
            ):
                raise ValueError(
                    "The referenced relationship does not match the proposition endpoints and type."
                )
