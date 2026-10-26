from typing import Annotated
from datetime import datetime, timezone
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status

from API.v1.DTOs.provenance_dtos import (
    CreateSourceRequest,
    SourceResponse,
    to_source_response,
)
from API.v1.dependancies.provenance_dependancies import get_source_service
from API.v1.provenance_routes.errors import raise_provenance_http_error
from application.services.source_service import SourceService
from domain_models.Provenance.source import Source, SourceReference

router = APIRouter(prefix="/sources", tags=["Provenance"])


@router.post("", response_model=SourceResponse, status_code=status.HTTP_201_CREATED)
def create_source(
    request: CreateSourceRequest,
    service: Annotated[SourceService, Depends(get_source_service)],
) -> SourceResponse:
    try:
        source = Source(
            title=request.title,
            source_type=request.source_type,
            publisher=request.publisher,
            url=request.url,
            publication_date=request.publication_date,
            retrieved_at=request.retrieved_at
            if request.retrieved_at is not None
            else datetime.now(timezone.utc),
        )
        return to_source_response(service.create(source))
    except Exception as exc:
        raise_provenance_http_error(exc)


@router.get("/{source_id}", response_model=SourceResponse)
def get_source(
    source_id: UUID,
    service: Annotated[SourceService, Depends(get_source_service)],
) -> SourceResponse:
    source = service.get_by_reference(SourceReference(source_id))
    if source is None:
        raise HTTPException(status_code=404, detail="Source was not found.")
    return to_source_response(source)
