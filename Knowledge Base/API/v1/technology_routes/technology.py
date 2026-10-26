
from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Response, status

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
from API.v1.DTOs.create_result_dtos import (
    CreateResultResponse,
    http_status_for_create_result,
    to_create_result_response,
)


router = APIRouter(
    prefix="/technologies",
    tags=["Technology"],
)


@router.post(
    "",
    response_model=CreateResultResponse[TechnologyResponse],
    status_code=status.HTTP_201_CREATED,
    responses={
        status.HTTP_200_OK: {"model": CreateResultResponse[TechnologyResponse]},
        status.HTTP_409_CONFLICT: {"model": CreateResultResponse[TechnologyResponse]},
    },
)
def create_technology(
    request: CreateTechnologyRequest,
    service: Annotated[
        TechnologyService,
        Depends(get_technology_service),
    ],
    response: Response,
) -> CreateResultResponse[TechnologyResponse]:
    result = service.create(
        canonical_name=request.canonical_name,
        aliases=set(request.aliases),
        allow_possible_duplicate=request.allow_possible_duplicate,
    )
    response.status_code = http_status_for_create_result(result)
    return to_create_result_response(result, entity_mapper=to_technology_response)


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
