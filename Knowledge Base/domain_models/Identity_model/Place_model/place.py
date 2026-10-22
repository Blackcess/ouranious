from enum import Enum
from domain_models.Identity_model.identity import Identity, IdentityKind, IdentityRepresentations, IdentityReference, LifecycleState

class PlaceKind(Enum):
    COUNTRY = "country"
    CITY = "city"
    REGION  = "region"

class Place(Identity):

    def __init__(
            self,
            *,
            representations:IdentityRepresentations,
            reference: IdentityReference | None = None,
            lifecycle_state: LifecycleState = LifecycleState.CANONICAL,
            place_kind: PlaceKind
    ):
        super().__init__(
            kind = IdentityKind.PLACE,
            representations= representations,
            reference= reference,
            lifecycle_state= lifecycle_state
        )
        self._place_kind : PlaceKind = place_kind

    def get_place_kind(self):
        return self._place_kind

                




