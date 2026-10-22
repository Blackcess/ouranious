
from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status

from application.services.place_service import PlaceService
from API.v1.dependancies.place_dependancies import get_place_service
from API.v1.DTOs.place_dtos import (
    CreatePlaceRequest,
    PlaceResponse,
    to_place_response,
)


router = APIRouter(
    prefix="/places",
    tags=["Place"],
)


@router.post(
    "",
    response_model=PlaceResponse,
    status_code=status.HTTP_201_CREATED,
)
def create_place(
    request: CreatePlaceRequest,
    service: Annotated[
        PlaceService,
        Depends(get_place_service),
    ],
) -> PlaceResponse:
    place = service.create(
        canonical_name=request.canonical_name,
        place_kind=request.place_kind,
        aliases=set(request.aliases),
    )

    return to_place_response(place)


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
