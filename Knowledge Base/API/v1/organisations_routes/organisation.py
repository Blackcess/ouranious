from typing import Annotated
from uuid import UUID
from fastapi import APIRouter, Depends, status, HTTPException, Response
from API.v1.dependancies.organisation_dependancies import get_organisation_service
from API.v1.DTOs.organisations_dtos import CreateStartupRequest, StartupResponse
from application.services.organisation_service import OrganisationService
from API.v1.DTOs.organisation_response_mappers import (
    to_startup_response,
    to_accelerator_response,
    to_incubator_response, 
    to_investor_response,
    to_organisation_response
)
from API.v1.DTOs.organisations_dtos import (
    CreateInvestorRequest,
    InvestorResponse,
    CreateAcceleratorRequest,
    AcceleratorResponse,
    CreateIncubatorRequest,
    IncubatorResponse,
    to_accelerator_programme,
    OrganisationResponse
)
from API.v1.DTOs.create_result_dtos import (
    CreateResultResponse,
    http_status_for_create_result,
    to_create_result_response,
)


router = APIRouter(
    prefix="/organisations",
    tags=["Organisation"]
)

# create startup route
@router.post(
    "/startups",
    response_model = CreateResultResponse[StartupResponse],
    status_code = status.HTTP_201_CREATED,
    responses={
        status.HTTP_200_OK: {"model": CreateResultResponse[StartupResponse]},
        status.HTTP_409_CONFLICT: {"model": CreateResultResponse[StartupResponse]},
    },
)
def  create_startup(
    request : CreateStartupRequest,
    service : Annotated[
        OrganisationService,
        Depends(get_organisation_service)
    ],
    response: Response,
)->CreateResultResponse[StartupResponse]:
    result = service.create_startup(
        canonical_name= request.canonical_name,
        founding_year = request.founding_year,
        stage = request.stage,
        business_model = request.business_model,
        aliases= set(request.aliases),
        allow_possible_duplicate=request.allow_possible_duplicate,
    )
    response.status_code = http_status_for_create_result(result)
    return to_create_result_response(
        result,
        entity_mapper=to_startup_response,
    )

# Create Investor route
@router.post(
    "/investors",
    response_model=CreateResultResponse[InvestorResponse],
    status_code=status.HTTP_201_CREATED,
    responses={
        status.HTTP_200_OK: {"model": CreateResultResponse[InvestorResponse]},
        status.HTTP_409_CONFLICT: {"model": CreateResultResponse[InvestorResponse]},
    },
)
def create_investor(
    request: CreateInvestorRequest,
    service: Annotated[
        OrganisationService,
        Depends(get_organisation_service),
    ],
    response: Response,
) -> CreateResultResponse[InvestorResponse]:
    result = service.create_investor(
        canonical_name=request.canonical_name,
        investor_type=request.investor_type,
        investment_stage=request.investment_stage,
        aliases=set(request.aliases),
        allow_possible_duplicate=request.allow_possible_duplicate,
    )
    response.status_code = http_status_for_create_result(result)
    return to_create_result_response(result, entity_mapper=to_investor_response)

# craate accelerator route
@router.post(
    "/accelerators",
    response_model=CreateResultResponse[AcceleratorResponse],
    status_code=status.HTTP_201_CREATED,
    responses={
        status.HTTP_200_OK: {"model": CreateResultResponse[AcceleratorResponse]},
        status.HTTP_409_CONFLICT: {"model": CreateResultResponse[AcceleratorResponse]},
    },
)
def create_accelerator(
    request: CreateAcceleratorRequest,
    service: Annotated[
        OrganisationService,
        Depends(get_organisation_service),
    ],
    response: Response,
) -> CreateResultResponse[AcceleratorResponse]:
    programmes = [
        to_accelerator_programme(programme)
        for programme in request.programmes
    ]

    result = service.create_accelerator(
        canonical_name=request.canonical_name,
        programmes=programmes,
        aliases=set(request.aliases),
        allow_possible_duplicate=request.allow_possible_duplicate,
    )
    response.status_code = http_status_for_create_result(result)
    return to_create_result_response(result, entity_mapper=to_accelerator_response)

# create incubator route
@router.post(
    "/incubators",
    response_model=CreateResultResponse[IncubatorResponse],
    status_code=status.HTTP_201_CREATED,
    responses={
        status.HTTP_200_OK: {"model": CreateResultResponse[IncubatorResponse]},
        status.HTTP_409_CONFLICT: {"model": CreateResultResponse[IncubatorResponse]},
    },
)
def create_incubator(
    request: CreateIncubatorRequest,
    service: Annotated[
        OrganisationService,
        Depends(get_organisation_service),
    ],
    response: Response,
) -> CreateResultResponse[IncubatorResponse]:
    result = service.create_incubator(
        canonical_name=request.canonical_name,
        aliases=set(request.aliases),
        allow_possible_duplicate=request.allow_possible_duplicate,
    )
    response.status_code = http_status_for_create_result(result)
    return to_create_result_response(result, entity_mapper=to_incubator_response)

# ======================================================
# GET ORGANISATION BY ID
# =======================================================

@router.get(
    "/{organisation_id}",
    response_model=OrganisationResponse,
)
def get_organisation(
    organisation_id: UUID,
    service: Annotated[
        OrganisationService,
        Depends(get_organisation_service),
    ],
) -> OrganisationResponse:
    organisation = service.get_organisation(organisation_id)

    if organisation is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Organisation not found",
        )

    return to_organisation_response(organisation)
