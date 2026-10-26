from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status

from API.v1.DTOs.provenance_dtos import (
    AssessmentCreatedResponse,
    CreateAssessmentRequest,
    VerificationAssessmentResponse,
    to_assessment_response,
)
from API.v1.dependancies.provenance_dependancies import (
    get_claim_service,
    get_verification_assessment_service,
)
from API.v1.provenance_routes.errors import raise_provenance_http_error
from application.services.claim_service import ClaimService
from application.services.verification_assessment_service import (
    VerificationAssessmentService,
)
from domain_models.Provenance.verification_assessment import (
    VerificationAssessment,
)

router = APIRouter(tags=["Provenance"])


@router.post(
    "/claims/{claim_id}/assessments",
    response_model=AssessmentCreatedResponse,
    status_code=status.HTTP_201_CREATED,
)
def create_assessment(
    claim_id: UUID,
    request: CreateAssessmentRequest,
    service: Annotated[
        VerificationAssessmentService,
        Depends(get_verification_assessment_service),
    ],
) -> AssessmentCreatedResponse:
    try:
        assessment = VerificationAssessment(
            claim_reference=claim_id,
            outcome=request.outcome,
            rationale=request.rationale,
            assessed_by=request.assessed_by,
            review_process=request.review_process,
        )
        if request.transition_claim_to is None:
            service.create(assessment)
            claim_status = None
        else:
            _, claim = service.create_and_transition_claim(
                assessment, new_status=request.transition_claim_to
            )
            claim_status = claim.status
        return AssessmentCreatedResponse(
            assessment=to_assessment_response(assessment),
            claim_status=claim_status,
        )
    except Exception as exc:
        raise_provenance_http_error(exc)


@router.get(
    "/claims/{claim_id}/assessments",
    response_model=list[VerificationAssessmentResponse],
)
def get_claim_assessments(
    claim_id: UUID,
    service: Annotated[
        VerificationAssessmentService,
        Depends(get_verification_assessment_service),
    ],
    claim_service: Annotated[ClaimService, Depends(get_claim_service)],
) -> list[VerificationAssessmentResponse]:
    if claim_service.get_by_reference(claim_id) is None:
        raise HTTPException(status_code=404, detail="Claim was not found.")
    return [
        to_assessment_response(item)
        for item in service.get_by_claim_reference(claim_id)
    ]


@router.get(
    "/assessments/{assessment_id}", response_model=VerificationAssessmentResponse
)
def get_assessment(
    assessment_id: UUID,
    service: Annotated[
        VerificationAssessmentService,
        Depends(get_verification_assessment_service),
    ],
) -> VerificationAssessmentResponse:
    assessment = service.get_by_reference(assessment_id)
    if assessment is None:
        raise HTTPException(status_code=404, detail="Assessment was not found.")
    return to_assessment_response(assessment)
