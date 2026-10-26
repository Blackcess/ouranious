
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field

from domain_models.Identity_model.Technology_model.technology import Technology


class CreateTechnologyRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")

    canonical_name: str = Field(min_length=1)
    aliases: list[str] = Field(default_factory=list)
    allow_possible_duplicate: bool = False


class TechnologyResponse(BaseModel):
    model_config = ConfigDict(extra="forbid")

    id: UUID
    canonical_name: str
    aliases: list[str]


def to_technology_response(
    technology: Technology,
) -> TechnologyResponse:
    return TechnologyResponse(
        id=technology.reference.value,
        canonical_name=technology.representations.canonical_name,
        aliases=sorted(technology.representations.aliases),
    )
