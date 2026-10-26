
from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Response, status

from application.services.place_service import PlaceService
from API.v1.dependancies.place_dependancies import get_place_service
from API.v1.DTOs.place_dtos import (
    CreatePlaceRequest,
    PlaceResponse,
    to_place_response,
)
from API.v1.DTOs.create_result_dtos import (
    CreateResultResponse,
    http_status_for_create_result,
    to_create_result_response,
)


router = APIRouter(
    prefix="/places",
    tags=["Place"],
)


@router.post(
    "",
    response_model=CreateResultResponse[PlaceResponse],
    status_code=status.HTTP_201_CREATED,
    responses={
        status.HTTP_200_OK: {"model": CreateResultResponse[PlaceResponse]},
        status.HTTP_409_CONFLICT: {"model": CreateResultResponse[PlaceResponse]},
    },
)
def create_place(
    request: CreatePlaceRequest,
    service: Annotated[
        PlaceService,
        Depends(get_place_service),
    ],
    response: Response,
) -> CreateResultResponse[PlaceResponse]:
    result = service.create(
        canonical_name=request.canonical_name,
        place_kind=request.place_kind,
        aliases=set(request.aliases),
        allow_possible_duplicate=request.allow_possible_duplicate,
    )
    response.status_code = http_status_for_create_result(result)
    return to_create_result_response(result, entity_mapper=to_place_response)


@router.get(
    "/{place_id}",
    response_model=PlaceResponse,
    status_code=status.HTTP_200_OK,
)
def get_place(
    place_id: UUID,
    service: Annotated[
        PlaceService,
        Depends(get_place_service),
    ],
) -> PlaceResponse:
    place = service.get_by_id(place_id)

    if place is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Place not found",
        )

    return to_place_response(place)
