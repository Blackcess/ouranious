from typing import Annotated
from uuid import UUID
from fastapi import APIRouter, Depends, status, HTTPException
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


router = APIRouter(
    prefix="/organisations",
    tags=["Organisation"]
)

# create startup route
@router.post(
    "/startups",
    response_model = StartupResponse,
    status_code = status.HTTP_201_CREATED
)
def  create_startup(
    request : CreateStartupRequest,
    service : Annotated[
        OrganisationService,
        Depends(get_organisation_service)
    ]
)->StartupResponse:
    organisation = service.create_startup(
        canonical_name= request.canonical_name,
        founding_year = request.founding_year,
        stage = request.stage,
        business_model = request.business_model,
        aliases= set(request.aliases)
    )

    return to_startup_response(
        organisation= organisation
    )

# Create Investor route
@router.post(
    "/investors",
    response_model=InvestorResponse,
    status_code=status.HTTP_201_CREATED,
)
def create_investor(
    request: CreateInvestorRequest,
    service: Annotated[
        OrganisationService,
        Depends(get_organisation_service),
    ],
) -> InvestorResponse:
    organisation = service.create_investor(
        canonical_name=request.canonical_name,
        investor_type=request.investor_type,
        investment_stage=request.investment_stage,
        aliases=set(request.aliases),
    )

    return to_investor_response(organisation)

# craate accelerator route
@router.post(
    "/accelerators",
    response_model=AcceleratorResponse,
    status_code=status.HTTP_201_CREATED,
)
def create_accelerator(
    request: CreateAcceleratorRequest,
    service: Annotated[
        OrganisationService,
        Depends(get_organisation_service),
    ],
) -> AcceleratorResponse:
    programmes = [
        to_accelerator_programme(programme)
        for programme in request.programmes
    ]

    organisation = service.create_accelerator(
        canonical_name=request.canonical_name,
        programmes=programmes,
        aliases=set(request.aliases),
    )

    return to_accelerator_response(organisation)

# create incubator route
@router.post(
    "/incubators",
    response_model=IncubatorResponse,
    status_code=status.HTTP_201_CREATED,
)
def create_incubator(
    request: CreateIncubatorRequest,
    service: Annotated[
        OrganisationService,
        Depends(get_organisation_service),
    ],
) -> IncubatorResponse:
    organisation = service.create_incubator(
        canonical_name=request.canonical_name,
        aliases=set(request.aliases),
    )

    return to_incubator_response(organisation)

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
