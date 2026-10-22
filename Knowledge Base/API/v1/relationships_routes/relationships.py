
from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status

from API.v1.DTOs.relationship_dtos import (
    CreateRelationshipRequest,
    RelationshipResponse,
    to_relationship_response,
)
from API.v1.DTOs.relationship_properties import (
    deserialize_relationship_properties,
)
from API.v1.dependancies.relationship_dependancies import (
    get_relationship_service,
)
from API.v1.dependancies.identity_resolver_dependancies import get_identity_resolver
from application.services.identity_relationship_service import RelationshipService
from application.services.identity_resolver import IdentityResolver


router = APIRouter(
    prefix="/relationships",
    tags=["Relationships"],
)


@router.post(
    "",
    response_model=RelationshipResponse,
    status_code=status.HTTP_201_CREATED,
)
def create_relationship(
    request: CreateRelationshipRequest,
    service: Annotated[
        RelationshipService,
        Depends(get_relationship_service),
    ],
    identity_resolver: Annotated[
        IdentityResolver,
        Depends(get_identity_resolver),
    ],
) -> RelationshipResponse:
    # Resolve the source identity.
    source = identity_resolver.get_by_id(request.source_id)

    if source is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Source identity '{request.source_id}' was not found.",
        )

    # Resolve the target identity.
    target = identity_resolver.get_by_id(request.target_id)

    if target is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Target identity '{request.target_id}' was not found.",
        )

    # Convert the JSON properties into the appropriate domain dataclass.
    try:
        properties = deserialize_relationship_properties(
            relationship_type=request.relationship_type,
            payload=request.properties,
        )

        relationship = service.create(
            source=source,
            target=target,
            relationship_type=request.relationship_type,
            properties=properties,
        )

    except (ValueError, TypeError) as exc:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=str(exc),
        ) from exc

    return to_relationship_response(relationship)


@router.get(
    "/{relationship_id}",
    response_model=RelationshipResponse,
    status_code=status.HTTP_200_OK,
)
def get_relationship(
    relationship_id: UUID,
    service: Annotated[
        RelationshipService,
        Depends(get_relationship_service),
    ],
) -> RelationshipResponse:
    relationship = service.get_by_id(relationship_id)

    if relationship is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Relationship '{relationship_id}' was not found.",
        )

    return to_relationship_response(relationship)
