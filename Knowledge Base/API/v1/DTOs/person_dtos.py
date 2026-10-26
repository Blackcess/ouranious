from uuid import UUID
from pydantic import BaseModel, ConfigDict, Field
from domain_models.Identity_model.Person_model.person import Person


class CreatePersonRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")

    canonical_name: str = Field(min_length=1)
    aliases: list[str] = Field(default_factory=list)
    allow_possible_duplicate: bool = False


class PersonResponse(BaseModel):
    model_config = ConfigDict(extra="forbid")

    id: UUID
    canonical_name: str
    aliases: list[str]


def to_person_response(person: Person) -> PersonResponse:
    return PersonResponse(
        id=person.reference.value,
        canonical_name=person.representations.canonical_name,
        aliases=sorted(person.representations.aliases),
    )
