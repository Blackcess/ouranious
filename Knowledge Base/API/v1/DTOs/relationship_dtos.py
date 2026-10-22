
from typing import Any
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field

from domain_models.relationship_models.relationship import Relationship
from domain_models.relationship_models.relationship_types.relationship_types import (
    RelationshipType,
)

from API.v1.DTOs.relationship_properties import (
    serialize_relationship_properties,
)


class CreateRelationshipRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")

    source_id: UUID
    target_id: UUID
    relationship_type: RelationshipType
    properties: dict[str, Any] | None = Field(default=None)


class RelationshipResponse(BaseModel):
    model_config = ConfigDict(extra="forbid")

    id: UUID
    source_id: UUID
    target_id: UUID
    relationship_type: RelationshipType
    properties: dict[str, Any] | None = None


def to_relationship_response(
    relationship: Relationship,
) -> RelationshipResponse:
    relationship_type = relationship.get_type()

    properties = serialize_relationship_properties(
        relationship_type=relationship_type,
        properties=relationship.get_properties(),
    )

    return RelationshipResponse(
        id=relationship.get_reference().value,
        source_id=relationship.get_source().reference.value,
        target_id=relationship.get_target().reference.value,
        relationship_type=relationship_type,
        properties=properties,
    )
