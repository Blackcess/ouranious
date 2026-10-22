
from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status

from application.services.technology_service import (
    TechnologyService,
)
from API.v1.dependancies.technology_dependancies import (
    get_technology_service,
)
from API.v1.DTOs.technology_dtos import (
    CreateTechnologyRequest,
    TechnologyResponse,
    to_technology_response,
)


router = APIRouter(
    prefix="/technologies",
    tags=["Technology"],
)


@router.post(
    "",
    response_model=TechnologyResponse,
    status_code=status.HTTP_201_CREATED,
)
def create_technology(
    request: CreateTechnologyRequest,
    service: Annotated[
        TechnologyService,
        Depends(get_technology_service),
    ],
) -> TechnologyResponse:
    technology = service.create(
        canonical_name=request.canonical_name,
        aliases=set(request.aliases),
    )

    return to_technology_response(technology)


@router.get(
    "/{technology_id}",
    response_model=TechnologyResponse,
    status_code=status.HTTP_200_OK,
)
def get_technology(
    technology_id: UUID,
    service: Annotated[
        TechnologyService,
        Depends(get_technology_service),
    ],
) -> TechnologyResponse:
    technology = service.get_by_id(technology_id)

    if technology is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Technology not found",
        )

    return to_technology_response(technology)
