"""Contracts returned by identity and relationship create operations."""

from dataclasses import dataclass
from enum import Enum
from typing import Generic, TypeVar

from application.resolution.identity.contracts import (
    IdentityResolutionResult,
    ResolutionOutcome,
)
from application.resolution.relationship.contracts import (
    RelationshipResolutionOutcome,
    RelationshipResolutionResult,
)

EntityT = TypeVar("EntityT")
ResolutionT = TypeVar(
    "ResolutionT", IdentityResolutionResult, RelationshipResolutionResult
)


class CreateAction(Enum):
    CREATED = "created"
    RETURNED_EXISTING = "returned_existing"
    BLOCKED = "blocked"


ResolutionOutcomeType = ResolutionOutcome | RelationshipResolutionOutcome


@dataclass(frozen=True)
class CreateResult(Generic[EntityT, ResolutionT]):
    """Resolution decision, service action, entity, and match evidence."""

    outcome: ResolutionOutcomeType
    action: CreateAction
    entity: EntityT | None
    resolution: ResolutionT
    override_applied: bool = False

    def __post_init__(self) -> None:
        if not isinstance(
            self.outcome,
            (ResolutionOutcome, RelationshipResolutionOutcome),
        ):
            raise TypeError("outcome must be a registered resolution outcome")
        if not isinstance(self.action, CreateAction):
            raise TypeError("action must be a CreateAction")
        if not isinstance(self.override_applied, bool):
            raise TypeError("override_applied must be a boolean")
        if not isinstance(
            self.resolution,
            (IdentityResolutionResult, RelationshipResolutionResult),
        ):
            raise TypeError("resolution must be an identity or relationship result")
        if self.resolution.outcome is not self.outcome:
            raise ValueError("outcome must agree with resolution.outcome")
        if self.action is CreateAction.BLOCKED and self.entity is not None:
            raise ValueError("BLOCKED create results cannot contain an entity")
        if self.action is CreateAction.BLOCKED and self.outcome not in (
            ResolutionOutcome.POSSIBLE_DUPLICATE,
            RelationshipResolutionOutcome.POSSIBLE_DUPLICATE,
        ):
            raise ValueError("only possible duplicates can be blocked")
        if self.action is not CreateAction.BLOCKED and self.entity is None:
            raise ValueError("completed create results must contain an entity")
        if self.override_applied and self.outcome not in (
            ResolutionOutcome.POSSIBLE_DUPLICATE,
            RelationshipResolutionOutcome.POSSIBLE_DUPLICATE,
        ):
            raise ValueError("override_applied requires a possible duplicate")
        if self.override_applied and self.action is not CreateAction.CREATED:
            raise ValueError("an applied override must create a new entity")
        if self.action is CreateAction.RETURNED_EXISTING and self.override_applied:
            raise ValueError("an override cannot return an existing entity")
        if (
            self.action is CreateAction.RETURNED_EXISTING
            and self.outcome not in (
                ResolutionOutcome.EXACT_MATCH,
                RelationshipResolutionOutcome.EXACT_MATCH,
            )
        ):
            raise ValueError("only exact matches can return an existing entity")
        if (
            self.action is CreateAction.CREATED
            and self.outcome in (
                ResolutionOutcome.EXACT_MATCH,
                RelationshipResolutionOutcome.EXACT_MATCH,
            )
        ):
            raise ValueError("exact matches cannot create a new entity")
        if (
            self.action is CreateAction.CREATED
            and self.outcome in (
                ResolutionOutcome.POSSIBLE_DUPLICATE,
                RelationshipResolutionOutcome.POSSIBLE_DUPLICATE,
            )
            and not self.override_applied
        ):
            raise ValueError("possible duplicates require an explicit override")

