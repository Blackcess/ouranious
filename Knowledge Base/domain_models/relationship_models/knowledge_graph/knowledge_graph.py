from domain_models.relationship_models.relationship_types.relationship_type_specification import RelationshipSpecification, specification_registry
from domain_models.relationship_models.relationship import Relationship 
from domain_models.Identity_model.identity import IdentityKind, IdentityReference, Identity
from uuid import UUID
from copy import deepcopy

class Knowledge_Graph:
    def __init__(self):
        self._identities:dict[UUID,Identity]={}
        self._relationships = set()

    def _validate_relationship(self, relationship: Relationship) -> None:

        # firstly check if the identities exists
        if(not(relationship.get_source().reference.value in self._identities and relationship.get_target().reference.value in self._identities)):
            raise ValueError(
                f"Specified identities are not recognized by the knowledge graph"
            )

        # check the specification registry for relationship types allowed src and target.
        specification = specification_registry.get(
            relationship.get_type()
        )

        if specification is None:
            raise ValueError(
                f"No specification found for relationship type "
                f"{relationship.get_type()}"
            )

        source_kind = relationship.get_source().kind
        target_kind = relationship.get_target().kind

        if source_kind != specification.allowed_source:
            raise ValueError(
                f"Invalid source for {relationship.get_type().value}: "
                f"expected {specification.allowed_source}, "
                f"got {source_kind}"
            )

        if target_kind != specification.allowed_target:
            raise ValueError(
                f"Invalid target for {relationship.get_type().value}: "
                f"expected {specification.allowed_target}, "
                f"got {target_kind}"
            )

    def add_relationship(self, relationship: Relationship):
        self._validate_relationship(relationship)
        self._relationships.add(relationship)

    def add_identity(self, id:Identity):
        self._identities[id.reference.value]  = id

    def remove_relationship(self, relationship:Relationship):
        self._relationships.remove(relationship)

    def get_relationships(self):
        return deepcopy(self._relationships)