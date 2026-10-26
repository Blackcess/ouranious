"""Shared atomic resolve-and-create workflows for application services."""

from typing import Protocol, TypeVar

from pymysql.connections import Connection

from application.resolution.create_result import CreateAction, CreateResult
from application.resolution.creation_locks import (
    acquire_identity_resolution_locks,
    lock_relationship_endpoints,
)
from application.resolution.identity.contracts import (
    IdentityResolutionRequest,
    IdentityResolutionResult,
    ResolutionOutcome,
)
from application.resolution.relationship.contracts import (
    RelationshipResolutionOutcome,
    RelationshipResolutionRequest,
    RelationshipResolutionResult,
)
from application.services.identity_resolution_service import IdentityResolutionService
from application.services.relationship_resolution_service import (
    RelationshipResolutionService,
)
from domain_models.Identity_model.identity import Identity
from domain_models.relationship_models.relationship import Relationship
from infrastructure.database.connection import DatabaseManager


IdentityT = TypeVar("IdentityT", bound=Identity)


class IdentitySaveRepository(Protocol):
    def save(self, identity: Identity, *, connection: Connection) -> None: ...


class RelationshipSaveRepository(Protocol):
    def save(self, relationship: Relationship, *, connection: Connection) -> None: ...


def resolve_and_create_identity(
    identity: IdentityT,
    *,
    repository: IdentitySaveRepository,
    database_manager: DatabaseManager,
    resolver: IdentityResolutionService,
    allow_possible_duplicate: bool,
) -> CreateResult[IdentityT, IdentityResolutionResult]:
    """Resolve and, if allowed, persist an identity in one locked transaction."""

    if not isinstance(allow_possible_duplicate, bool):
        raise TypeError("allow_possible_duplicate must be a boolean")

    with database_manager.transaction() as connection:
        return resolve_and_create_identity_in_transaction(
            identity,
            repository=repository,
            resolver=resolver,
            allow_possible_duplicate=allow_possible_duplicate,
            connection=connection,
        )


def resolve_and_create_identity_in_transaction(
    identity: IdentityT,
    *,
    repository: IdentitySaveRepository,
    resolver: IdentityResolutionService,
    allow_possible_duplicate: bool,
    connection: Connection,
) -> CreateResult[IdentityT, IdentityResolutionResult]:
    """Resolve and save using a transaction owned by the caller."""
    if not isinstance(allow_possible_duplicate, bool):
        raise TypeError("allow_possible_duplicate must be a boolean")
    acquire_identity_resolution_locks(identity, connection=connection)
    resolution = resolver.resolve(
        IdentityResolutionRequest(identity), connection=connection
    )
    if resolution.outcome is ResolutionOutcome.EXACT_MATCH:
        return CreateResult(
            outcome=resolution.outcome,
            action=CreateAction.RETURNED_EXISTING,
            entity=resolution.matches[0].identity,
            resolution=resolution,
        )
    if resolution.outcome is ResolutionOutcome.POSSIBLE_DUPLICATE:
        if not allow_possible_duplicate:
            return CreateResult(
                outcome=resolution.outcome,
                action=CreateAction.BLOCKED,
                entity=None,
                resolution=resolution,
            )
        repository.save(identity, connection=connection)
        return CreateResult(
            outcome=resolution.outcome,
            action=CreateAction.CREATED,
            entity=identity,
            resolution=resolution,
            override_applied=True,
        )
    repository.save(identity, connection=connection)
    return CreateResult(
        outcome=resolution.outcome,
        action=CreateAction.CREATED,
        entity=identity,
        resolution=resolution,
    )


def resolve_and_create_relationship(
    relationship: Relationship,
    *,
    repository: RelationshipSaveRepository,
    database_manager: DatabaseManager,
    resolver: RelationshipResolutionService,
    allow_possible_duplicate: bool,
) -> CreateResult[Relationship, RelationshipResolutionResult]:
    """Resolve and, if allowed, persist a relationship atomically."""

    if not isinstance(allow_possible_duplicate, bool):
        raise TypeError("allow_possible_duplicate must be a boolean")

    with database_manager.transaction() as connection:
        return resolve_and_create_relationship_in_transaction(
            relationship,
            repository=repository,
            resolver=resolver,
            allow_possible_duplicate=allow_possible_duplicate,
            connection=connection,
        )


def resolve_and_create_relationship_in_transaction(
    relationship: Relationship,
    *,
    repository: RelationshipSaveRepository,
    resolver: RelationshipResolutionService,
    allow_possible_duplicate: bool,
    connection: Connection,
) -> CreateResult[Relationship, RelationshipResolutionResult]:
    """Resolve and save using a transaction owned by the caller."""
    if not isinstance(allow_possible_duplicate, bool):
        raise TypeError("allow_possible_duplicate must be a boolean")
    lock_relationship_endpoints(relationship, connection=connection)
    resolution = resolver.resolve(
        RelationshipResolutionRequest(relationship), connection=connection
    )
    if resolution.outcome is RelationshipResolutionOutcome.EXACT_MATCH:
        return CreateResult(
            outcome=resolution.outcome,
            action=CreateAction.RETURNED_EXISTING,
            entity=resolution.matches[0].relationship,
            resolution=resolution,
        )
    if resolution.outcome is RelationshipResolutionOutcome.POSSIBLE_DUPLICATE:
        if not allow_possible_duplicate:
            return CreateResult(
                outcome=resolution.outcome,
                action=CreateAction.BLOCKED,
                entity=None,
                resolution=resolution,
            )
        repository.save(relationship, connection=connection)
        return CreateResult(
            outcome=resolution.outcome,
            action=CreateAction.CREATED,
            entity=relationship,
            resolution=resolution,
            override_applied=True,
        )
    repository.save(relationship, connection=connection)
    return CreateResult(
        outcome=resolution.outcome,
        action=CreateAction.CREATED,
        entity=relationship,
        resolution=resolution,
    )
