from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Response, status

from application.services.person_service import PersonService
from API.v1.dependancies.person_dependancies import get_person_service
from API.v1.DTOs.person_dtos import (
    CreatePersonRequest,
    PersonResponse,
    to_person_response,
)
from API.v1.DTOs.create_result_dtos import (
    CreateResultResponse,
    http_status_for_create_result,
    to_create_result_response,
)


router = APIRouter(
    prefix="/persons",
    tags=["Person"],
)


@router.post(
    "",
    response_model=CreateResultResponse[PersonResponse],
    status_code=status.HTTP_201_CREATED,
    responses={
        status.HTTP_200_OK: {"model": CreateResultResponse[PersonResponse]},
        status.HTTP_409_CONFLICT: {"model": CreateResultResponse[PersonResponse]},
    },
)
def create_person(
    request: CreatePersonRequest,
    service: Annotated[
        PersonService,
        Depends(get_person_service),
    ],
    response: Response,
) -> CreateResultResponse[PersonResponse]:
    result = service.create(
        canonical_name=request.canonical_name,
        aliases=set(request.aliases),
        allow_possible_duplicate=request.allow_possible_duplicate,
    )
    response.status_code = http_status_for_create_result(result)
    return to_create_result_response(result, entity_mapper=to_person_response)


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
