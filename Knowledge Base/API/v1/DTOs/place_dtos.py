from uuid import UUID
from pydantic import BaseModel, ConfigDict, Field
from domain_models.Identity_model.Place_model.place import Place, PlaceKind


class CreatePlaceRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")

    canonical_name: str = Field(min_length=1)
    place_kind: PlaceKind
    aliases: list[str] = Field(default_factory=list)


class PlaceResponse(BaseModel):
    model_config = ConfigDict(extra="forbid")

    id: UUID
    canonical_name: str
    aliases: list[str]
    kind: PlaceKind


def to_place_response(place: Place) -> PlaceResponse:
    return PlaceResponse(
        id=place.reference.value,
        canonical_name=place.representations.canonical_name,
        aliases=sorted(place.representations.aliases),
        kind=place.get_place_kind(),
    )
