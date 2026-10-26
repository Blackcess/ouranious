"""HTTP response contracts for create operations with resolution metadata."""

from typing import Any, Generic, TypeVar

from fastapi.encoders import jsonable_encoder
from fastapi import status
from pydantic import BaseModel, ConfigDict

from application.resolution.create_result import CreateAction, CreateResult
from application.resolution.identity.contracts import IdentityResolutionResult
from application.resolution.relationship.contracts import (
    RelationshipResolutionResult,
)

EntityResponseT = TypeVar("EntityResponseT")


class CreateResultResponse(BaseModel, Generic[EntityResponseT]):
    model_config = ConfigDict(extra="forbid")

    outcome: str
    action: str
    override_applied: bool
    entity: EntityResponseT | None
    candidates: list[dict[str, Any]]
    candidates_truncated: bool


def http_status_for_create_result(result: CreateResult) -> int:
    if result.action is CreateAction.CREATED:
        return status.HTTP_201_CREATED
    if result.action is CreateAction.RETURNED_EXISTING:
        return status.HTTP_200_OK
    return status.HTTP_409_CONFLICT


def to_create_result_response(
    result: CreateResult,
    *,
    entity_mapper,
) -> CreateResultResponse:
    entity = entity_mapper(result.entity) if result.entity is not None else None
    matches = result.resolution.matches
    candidates: list[dict[str, Any]] = []

    if isinstance(result.resolution, IdentityResolutionResult):
        for match in matches:
            identity = match.identity
            candidates.append(
                {
                    "id": identity.reference.value,
                    "kind": identity.kind.value,
                    "canonical_name": identity.representations.canonical_name,
                    "match_kind": match.kind.value,
                    "evidence": jsonable_encoder(match.evidence),
                }
            )
    elif isinstance(result.resolution, RelationshipResolutionResult):
        for match in matches:
            relationship = match.relationship
            candidates.append(
                {
                    "id": relationship.get_reference().value,
                    "source_id": relationship.get_source().reference.value,
                    "target_id": relationship.get_target().reference.value,
                    "relationship_type": relationship.get_type().value,
                    "properties": jsonable_encoder(relationship.get_properties()),
                    "evidence": jsonable_encoder(match.evidence),
                }
            )

    return CreateResultResponse(
        outcome=result.outcome.value,
        action=result.action.value,
        override_applied=result.override_applied,
        entity=entity,
        candidates=candidates,
        candidates_truncated=result.resolution.candidates_truncated,
    )
