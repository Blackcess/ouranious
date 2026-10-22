
# domain_models/provenance/propositions.py

from copy import deepcopy
from dataclasses import dataclass
from types import MappingProxyType
from typing import Mapping, TypeAlias

from domain_models.Identity_model.identity import (
    IdentityKind,
    IdentityReference,
)
from domain_models.relationship_models.relationship_types.relationship_types import (
    RelationshipType,
)
from domain_models.relationship_models.relationship_types.relationship_type_specification import (
    specification_registry,
)
from domain_models.relationship_models.relationship import (
    RelationshipReference,
)


@dataclass(frozen=True)
class IdentityAttributeProposition:
    identity_reference: IdentityReference
    attribute_name: str
    proposed_value: object

    def __post_init__(self) -> None:
        if not isinstance(self.identity_reference, IdentityReference):
            raise TypeError(
                "identity_reference must be an IdentityReference"
            )

        if (
            not isinstance(self.attribute_name, str)
            or not self.attribute_name.strip()
        ):
            raise ValueError(
                "attribute_name cannot be empty"
            )

        object.__setattr__(
            self,
            "proposed_value",
            deepcopy(self.proposed_value),
        )


@dataclass(frozen=True)
class RelationshipProposition:
    source_reference: IdentityReference
    target_reference: IdentityReference
    relationship_type: RelationshipType
    properties: object | None = None
    existing_relationship_reference: (
        RelationshipReference | None
    ) = None

    def __post_init__(self) -> None:
        if not isinstance(self.source_reference, IdentityReference):
            raise TypeError(
                "source_reference must be an IdentityReference"
            )

        if not isinstance(self.target_reference, IdentityReference):
            raise TypeError(
                "target_reference must be an IdentityReference"
            )

        if not isinstance(self.relationship_type, RelationshipType):
            raise TypeError(
                "relationship_type must be a RelationshipType"
            )

        specification = specification_registry.get(
            self.relationship_type
        )

        if specification is None:
            raise ValueError(
                f"Unsupported relationship type: "
                f"{self.relationship_type}"
            )

        expected_type = specification.properties_type

        if expected_type is None:
            if self.properties is not None:
                raise TypeError(
                    f"{self.relationship_type.value} "
                    "does not accept properties"
                )
        elif not isinstance(self.properties, expected_type):
            raise TypeError(
                f"{self.relationship_type.value} requires an "
                f"instance of {expected_type.__name__}"
            )

        if self.existing_relationship_reference is not None:
            if not isinstance(
                self.existing_relationship_reference,
                RelationshipReference,
            ):
                raise TypeError(
                    "existing_relationship_reference must be a "
                    "RelationshipReference or None"
                )

        object.__setattr__(
            self,
            "properties",
            deepcopy(self.properties),
        )

    @property
    def targets_existing_relationship(self) -> bool:
        return self.existing_relationship_reference is not None


@dataclass(frozen=True)
class RelationshipPropertyProposition:
    relationship_reference: RelationshipReference
    property_name: str
    proposed_value: object

    def __post_init__(self) -> None:
        if not isinstance(
            self.relationship_reference,
            RelationshipReference,
        ):
            raise TypeError(
                "relationship_reference must be a RelationshipReference"
            )

        if (
            not isinstance(self.property_name, str)
            or not self.property_name.strip()
        ):
            raise ValueError("property_name cannot be empty")

        object.__setattr__(
            self,
            "proposed_value",
            deepcopy(self.proposed_value),
        )


@dataclass(frozen=True)
class IdentityProposalProposition:
    identity_kind: IdentityKind
    canonical_name: str
    aliases: frozenset[str] = frozenset()
    attributes: Mapping[str, object] | None = None

    def __post_init__(self) -> None:
        if not isinstance(self.identity_kind, IdentityKind):
            raise TypeError("identity_kind must be an IdentityKind")

        if (
            not isinstance(self.canonical_name, str)
            or not self.canonical_name.strip()
        ):
            raise ValueError("canonical_name cannot be empty")

        if not isinstance(self.aliases, (set, frozenset)):
            raise TypeError("aliases must be a set or frozenset")

        normalised_aliases = frozenset(self.aliases)

        if any(
            not isinstance(alias, str) or not alias.strip()
            for alias in normalised_aliases
        ):
            raise ValueError(
                "aliases must contain non-empty strings"
            )

        object.__setattr__(self, "aliases", normalised_aliases)

        attributes = dict(self.attributes or {})

        if any(
            not isinstance(name, str) or not name.strip()
            for name in attributes
        ):
            raise ValueError(
                "attribute names must be non-empty strings"
            )

        object.__setattr__(
            self,
            "attributes",
            MappingProxyType(deepcopy(attributes)),
        )


Proposition: TypeAlias = (
    IdentityAttributeProposition
    | RelationshipProposition
    | RelationshipPropertyProposition
    | IdentityProposalProposition
)
