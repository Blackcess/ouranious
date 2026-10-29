from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends, Response, status

from API.v1.DTOs.create_result_dtos import to_create_result_response
from API.v1.DTOs.provenance_dtos import (
    ClaimMaterialisationResponse,
    MaterialiseClaimRequest,
)
from API.v1.dependancies.provenance_dependancies import (
    get_claim_materialisation_service,
)
from API.v1.provenance_routes.errors import raise_provenance_http_error
from application.resolution.create_result import CreateAction, CreateResult
from application.services.claim_materialisation_service import (
    ClaimMaterialisationResult,
    ClaimMaterialisationService,
)

router = APIRouter(prefix="/claims", tags=["Provenance"])


@router.post(
    "/{claim_id}/materialisation",
    response_model=ClaimMaterialisationResponse,
    status_code=status.HTTP_201_CREATED,
    responses={
        status.HTTP_200_OK: {"model": ClaimMaterialisationResponse},
        status.HTTP_409_CONFLICT: {"model": ClaimMaterialisationResponse},
    },
)
def materialise_claim(
    claim_id: UUID,
    request: MaterialiseClaimRequest,
    service: Annotated[
        ClaimMaterialisationService,
        Depends(get_claim_materialisation_service),
    ],
    response: Response,
) -> ClaimMaterialisationResponse:
    try:
        result = service.materialise(
            claim_id,
            allow_possible_duplicate=request.allow_possible_duplicate,
        )
        
        if result.action is None:
            response.status_code = status.HTTP_409_CONFLICT
        elif result.already_materialised or result.action.value == "linked":
            response.status_code = status.HTTP_200_OK
        else:
            response.status_code = status.HTTP_201_CREATED
        return _to_response(result)
    except Exception as exc:
        raise_provenance_http_error(exc)


def _to_response(result: ClaimMaterialisationResult) -> ClaimMaterialisationResponse:
    candidates = []
    candidates_truncated = False
    if result.resolution is not None:
        candidates_truncated = result.resolution.candidates_truncated
        action = CreateAction.BLOCKED if result.action is None else (
            CreateAction.CREATED if result.action.value == "created"
            else CreateAction.RETURNED_EXISTING
        )
        create_result = CreateResult(
            outcome=result.resolution.outcome,
            action=action,
            entity=result.entity,
            resolution=result.resolution,
            override_applied=result.override_applied,
        )
        candidates = to_create_result_response(
            create_result,
            entity_mapper=lambda entity: {},
        ).candidates
    target_id = None
    if result.entity is not None:
        target_id = (
            result.entity.reference.value
            if hasattr(result.entity, "kind")
            else result.entity.get_reference().value
        )
    return ClaimMaterialisationResponse(
        claim_id=result.claim_reference,
        target_kind=result.target_kind.value,
        target_id=target_id,
        outcome=result.outcome.value,
        action=None if result.action is None else result.action.value,
        override_applied=result.override_applied,
        already_materialised=result.already_materialised,
        candidates=candidates,
        candidates_truncated=candidates_truncated,
    )
