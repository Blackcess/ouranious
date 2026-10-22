
from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status

from application.services.industry_service import IndustryService
from API.v1.dependancies.industry_dependancies import get_industry_service
from API.v1.DTOs.industry_dtos import (
    CreateIndustryRequest,
    IndustryResponse,
    to_industry_response,
)


router = APIRouter(
    prefix="/industries",
    tags=["Industry"],
)


@router.post(
    "",
    response_model=IndustryResponse,
    status_code=status.HTTP_201_CREATED,
)
def create_industry(
    request: CreateIndustryRequest,
    service: Annotated[
        IndustryService,
        Depends(get_industry_service),
    ],
) -> IndustryResponse:
    industry = service.create(
        canonical_name=request.canonical_name,
        aliases=set(request.aliases),
    )

    return to_industry_response(industry)


@router.get(
    "/{industry_id}",
    response_model=IndustryResponse,
    status_code=status.HTTP_200_OK,
)
def get_industry(
    industry_id: UUID,
    service: Annotated[
        IndustryService,
        Depends(get_industry_service),
    ],
) -> IndustryResponse:
    industry = service.get_by_id(industry_id)

    if industry is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Industry not found",
        )

    return to_industry_response(industry)
