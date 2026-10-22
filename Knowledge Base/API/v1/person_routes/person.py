from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status

from application.services.person_service import PersonService
from API.v1.dependancies.person_dependancies import get_person_service
from API.v1.DTOs.person_dtos import (
    CreatePersonRequest,
    PersonResponse,
    to_person_response,
)


router = APIRouter(
    prefix="/persons",
    tags=["Person"],
)


@router.post(
    "",
    response_model=PersonResponse,
    status_code=status.HTTP_201_CREATED,
)
def create_person(
    request: CreatePersonRequest,
    service: Annotated[
        PersonService,
        Depends(get_person_service),
    ],
) -> PersonResponse:
    person = service.create(
        canonical_name=request.canonical_name,
        aliases=set(request.aliases),
    )

    return to_person_response(person)


@router.get(
    "/{person_id}",
    response_model=PersonResponse,
    status_code=status.HTTP_200_OK,
)
def get_person(
    person_id: UUID,
    service: Annotated[
        PersonService,
        Depends(get_person_service),
    ],
) -> PersonResponse:
    person = service.get_by_id(person_id)

    if person is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Person not found",
        )

    return to_person_response(person)
