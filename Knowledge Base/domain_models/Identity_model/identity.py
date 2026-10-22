from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from enum import Enum
from uuid import UUID, uuid4

class IdentityKind(Enum):
    PERSON = "person"
    ORGANISATION = "organisation"
    PLACE  = "place"
    INDUSTRY = "industry"
    PRODUCT = "product"
    TECHNOLOGY = "technology"

class LifecycleState(Enum):
    CANONICAL = "canonical"
    RETIRED = "retired"

@dataclass(frozen=True)
class IdentityReference:
    value : UUID = field(default_factory=uuid4)

@dataclass(frozen=True)
class IdentityRepresentations:
    canonical_name: str
    aliases: set[str] = field(default_factory = set)

class Identity(ABC):

    def __init__(
        self,
        *,
        kind:IdentityKind,
        representations: IdentityRepresentations,
        reference: IdentityReference | None = None,
        lifecycle_state: LifecycleState = LifecycleState.CANONICAL,
    ):
        self._reference = reference or IdentityReference()
        self._kind = kind
        self._lifecycle_state = lifecycle_state
        self._representations = representations

    @property
    def reference(self) -> IdentityReference:
        return self._reference

    @property
    def kind(self)-> IdentityKind:
        return self._kind

    @property
    def lifecycle_state(self) -> LifecycleState:
        return self._lifecycle_state

    @property
    def representations(self) -> IdentityRepresentations:
        return self._representations



# obj = Identity(
#     kind = IdentityKind.PERSON,
#     representations= IdentityRepresentations(
#         canonical_name=  "Takudzwa Jawet Gwiriri",
#         aliases= {"Sir Taku", "Taku"}
#     )
# )

# print(obj.reference.value)