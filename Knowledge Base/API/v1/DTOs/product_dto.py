
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field

from domain_models.Identity_model.Product_model.product import Product


class CreateProductRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")

    canonical_name: str = Field(min_length=1)
    aliases: list[str] = Field(default_factory=list)


class ProductResponse(BaseModel):
    model_config = ConfigDict(extra="forbid")

    id: UUID
    canonical_name: str
    aliases: list[str]


def to_product_response(product: Product) -> ProductResponse:
    return ProductResponse(
        id=product.reference.value,
        canonical_name=product.representations.canonical_name,
        aliases=sorted(product.representations.aliases),
    )
