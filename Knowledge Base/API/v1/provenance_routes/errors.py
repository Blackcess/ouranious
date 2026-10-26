"""HTTP error mapping shared by Provenance endpoints."""

from fastapi import HTTPException, status

from repositories.utils.errors import (
    RepositoryConflictError,
    RepositoryNotFoundError,
    RepositoryReferenceError,
)


def raise_provenance_http_error(exc: Exception) -> None:
    if isinstance(exc, RepositoryConflictError):
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="The Provenance resource conflicts with an existing record.",
        ) from exc
    if isinstance(exc, (RepositoryNotFoundError, RepositoryReferenceError)):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(exc),
        ) from exc
    if isinstance(exc, LookupError):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(exc),
        ) from exc
    if isinstance(exc, (TypeError, ValueError)):
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=str(exc),
        ) from exc
    raise exc
