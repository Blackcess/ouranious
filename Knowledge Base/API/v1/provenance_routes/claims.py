from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Response, status

from API.v1.DTOs.provenance_dtos import (
    ClaimResponse,
    CreateClaimRequest,
    UpdateClaimStatusRequest,
    to_claim_response,
    to_domain_proposition,
)
from API.v1.dependancies.provenance_dependancies import get_claim_service
from API.v1.provenance_routes.errors import raise_provenance_http_error
from application.services.claim_service import ClaimService
from domain_models.Provenance.claim import Claim
from domain_models.Provenance.source import SourceReference

router = APIRouter(prefix="/claims", tags=["Provenance"])


@router.post("", response_model=ClaimResponse, status_code=status.HTTP_201_CREATED)
def create_claim(
    request: CreateClaimRequest,
    service: Annotated[ClaimService, Depends(get_claim_service)],
) -> ClaimResponse:
    try:
        claim = Claim(
            proposition=to_domain_proposition(request.proposition),
            source_references={SourceReference(item) for item in request.source_ids},
            research_notes=request.research_notes,
        )
        return to_claim_response(service.create(claim))
    except (TypeError, ValueError) as exc:
        raise_provenance_http_error(exc)
    except Exception as exc:
        raise_provenance_http_error(exc)


@router.get("/{claim_id}", response_model=ClaimResponse)
def get_claim(
    claim_id: UUID,
    service: Annotated[ClaimService, Depends(get_claim_service)],
) -> ClaimResponse:
    claim = service.get_by_reference(claim_id)
    if claim is None:
        raise HTTPException(status_code=404, detail="Claim was not found.")
    return to_claim_response(claim)


@router.patch("/{claim_id}/status", response_model=ClaimResponse)
def transition_claim_status(
    claim_id: UUID,
    request: UpdateClaimStatusRequest,
    service: Annotated[ClaimService, Depends(get_claim_service)],
) -> ClaimResponse:
    try:
        return to_claim_response(service.transition_status(claim_id, request.status))
    except Exception as exc:
        raise_provenance_http_error(exc)


@router.post(
    "/{claim_id}/sources/{source_id}",
    status_code=status.HTTP_204_NO_CONTENT,
)
def add_claim_source(
    claim_id: UUID,
    source_id: UUID,
    service: Annotated[ClaimService, Depends(get_claim_service)],
) -> Response:
    try:
        service.add_source(claim_id, SourceReference(source_id))
        return Response(status_code=status.HTTP_204_NO_CONTENT)
    except Exception as exc:
        raise_provenance_http_error(exc)


@router.delete(
    "/{claim_id}/sources/{source_id}",
    status_code=status.HTTP_204_NO_CONTENT,
)
def remove_claim_source(
    claim_id: UUID,
    source_id: UUID,
    service: Annotated[ClaimService, Depends(get_claim_service)],
) -> Response:
    try:
        if service.get_by_reference(claim_id) is None:
            raise HTTPException(status_code=404, detail="Claim was not found.")
        service.remove_source(claim_id, SourceReference(source_id))
        return Response(status_code=status.HTTP_204_NO_CONTENT)
    except Exception as exc:
        raise_provenance_http_error(exc)
