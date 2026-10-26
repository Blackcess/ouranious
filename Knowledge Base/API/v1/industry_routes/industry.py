
from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Response, status

from application.services.industry_service import IndustryService
from API.v1.dependancies.industry_dependancies import get_industry_service
from API.v1.DTOs.industry_dtos import (
    CreateIndustryRequest,
    IndustryResponse,
    to_industry_response,
)
from API.v1.DTOs.create_result_dtos import (
    CreateResultResponse,
    http_status_for_create_result,
    to_create_result_response,
)


router = APIRouter(
    prefix="/industries",
    tags=["Industry"],
)


@router.post(
    "",
    response_model=CreateResultResponse[IndustryResponse],
    status_code=status.HTTP_201_CREATED,
    responses={
        status.HTTP_200_OK: {"model": CreateResultResponse[IndustryResponse]},
        status.HTTP_409_CONFLICT: {"model": CreateResultResponse[IndustryResponse]},
    },
)
def create_industry(
    request: CreateIndustryRequest,
    service: Annotated[
        IndustryService,
        Depends(get_industry_service),
    ],
    response: Response,
) -> CreateResultResponse[IndustryResponse]:
    result = service.create(
        canonical_name=request.canonical_name,
        aliases=set(request.aliases),
        allow_possible_duplicate=request.allow_possible_duplicate,
    )
    response.status_code = http_status_for_create_result(result)
    return to_create_result_response(result, entity_mapper=to_industry_response)


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
