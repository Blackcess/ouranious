
from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status

from application.services.product_service import (
    ProductService,
)
from API.v1.dependancies.product_dependancies import (
    get_product_service,
)
from API.v1.DTOs.product_dto import (
    CreateProductRequest,
    ProductResponse,
    to_product_response,
)


router = APIRouter(
    prefix="/products",
    tags=["Product"],
)


@router.post(
    "",
    response_model=ProductResponse,
    status_code=status.HTTP_201_CREATED,
)
def create_product(
    request: CreateProductRequest,
    service: Annotated[
        ProductService,
        Depends(get_product_service),
    ],
) -> ProductResponse:
    product = service.create(
        canonical_name=request.canonical_name,
        aliases=set(request.aliases),
    )

    return to_product_response(product)


@router.get(
    "/{product_id}",
    response_model=ProductResponse,
    status_code=status.HTTP_200_OK,
)
def get_product(
    product_id: UUID,
    service: Annotated[
        ProductService,
        Depends(get_product_service),
    ],
) -> ProductResponse:
    product = service.get_by_id(product_id)

    if product is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Product not found",
        )

    return to_product_response(product)
