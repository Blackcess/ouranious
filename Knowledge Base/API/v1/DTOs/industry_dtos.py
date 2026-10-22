from uuid import UUID
from pydantic import BaseModel, ConfigDict, Field

from domain_models.Identity_model.Industry_model.industry import Industry


class CreateIndustryRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")

    canonical_name: str = Field(min_length=1)
    aliases: list[str] = Field(default_factory=list)


class IndustryResponse(BaseModel):
    model_config = ConfigDict(extra="forbid")

    id: UUID
    canonical_name: str
    aliases: list[str]


def to_industry_response(industry: Industry) -> IndustryResponse:
    return IndustryResponse(
        id=industry.reference.value,
        canonical_name=industry.representations.canonical_name,
        aliases=sorted(industry.representations.aliases),
    )
