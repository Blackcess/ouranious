from domain_models.relationship_models.relationship_types.relationship_types import RelationshipType
from domain_models.Identity_model.identity import Identity
from domain_models.relationship_models.relationship_types.relationship_type_specification import specification_registry
from copy import deepcopy
from uuid import UUID, uuid4
from dataclasses import dataclass, field

@dataclass(frozen=True)
class RelationshipReference:
    value : UUID = field(default_factory=uuid4)

class Relationship:
    def __init__(
            self,
            *,
            source: Identity,
            target: Identity,
            type: RelationshipType,
            properties: object | None = None,
            reference: RelationshipReference | None = None,
        ):
        specification = specification_registry.get(type)

        if specification is None:
            raise ValueError(
                f"Unsupported relationship type: {type}"
            )

        if(source.kind != specification.allowed_source):
            raise ValueError(
                            f"Invalid source for {type.value}: "
                            f"expected {specification.allowed_source}, "
                            f"got {source.kind}"
                        )

        if(target.kind != specification.allowed_target):
            raise ValueError(
                            f"Invalid target for {type.value}: "
                            f"expected {specification.allowed_target}, "
                            f"got {target.kind}"
                        )

        expected_type = specification.properties_type

        if expected_type is None:
            if properties is not None:
                raise TypeError(
                    f"{type} does not accept properties"
                )

        elif not isinstance(properties, expected_type):
            raise TypeError(
                f"{type} requires "
                f"{expected_type.__name__}"
            )
        if(expected_type is not None and properties is None):
            raise TypeError(
                f"{type} requires "
                f"{expected_type.__name__}"
            )

        self._reference = reference or RelationshipReference()
        self._source = source
        self._target = target
        self._type = type
        self._properties = properties

    def get_source(self) -> Identity:
        return self._source

    def get_target(self) -> Identity:
        return self._target

    def get_type(self) -> RelationshipType:
        return self._type

    def get_properties(self):
        if(self._properties == None):
            return None
        return deepcopy(self._properties)

    def get_reference(self) -> RelationshipReference:
        return self._reference
        
    