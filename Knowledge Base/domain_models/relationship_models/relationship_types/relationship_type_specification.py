from domain_models.Identity_model.identity import IdentityKind
from domain_models.relationship_models.relationship_types.relationship_types import RelationshipType
from dataclasses import dataclass
from typing import TypeAlias
from domain_models.relationship_models.relationship_properties import properties_merge as properties


RelationshipPropertiesType: TypeAlias = type | None

@dataclass(frozen = True)
class RelationshipSpecification:
    relationship_type: RelationshipType
    allowed_source: IdentityKind
    allowed_target: IdentityKind
    properties_type: RelationshipPropertiesType = None



specification_registry = {

    RelationshipType.FOUNDED:
        RelationshipSpecification(
            relationship_type=RelationshipType.FOUNDED,
            allowed_source=IdentityKind.PERSON,
            allowed_target=IdentityKind.ORGANISATION,
            properties_type= properties.FounderProperties
        ),

    RelationshipType.LEADS:
        RelationshipSpecification(
            relationship_type=RelationshipType.LEADS,
            allowed_source=IdentityKind.PERSON,
            allowed_target=IdentityKind.ORGANISATION,
            properties_type=properties.LeadershipProperties
        ),

    RelationshipType.OWNS:
        RelationshipSpecification(
            relationship_type=RelationshipType.OWNS,
            allowed_source=IdentityKind.PERSON,
            allowed_target=IdentityKind.ORGANISATION,
            properties_type= properties.OwnershipProperties
        ),

    RelationshipType.BORN_IN:
        RelationshipSpecification(
            relationship_type=RelationshipType.BORN_IN,
            allowed_source=IdentityKind.PERSON,
            allowed_target=IdentityKind.PLACE,
        ),

    RelationshipType.LIVES_IN:
        RelationshipSpecification(
            relationship_type=RelationshipType.LIVES_IN,
            allowed_source=IdentityKind.PERSON,
            allowed_target=IdentityKind.PLACE,
            properties_type=properties.ResidenceProperties
        ),

    RelationshipType.PARTNERED_WITH:
        RelationshipSpecification(
            relationship_type=RelationshipType.PARTNERED_WITH,
            allowed_source=IdentityKind.ORGANISATION,
            allowed_target=IdentityKind.ORGANISATION,
            properties_type=properties.PartnershipProperties
        ),

    RelationshipType.INVESTED_IN:
        RelationshipSpecification(
            relationship_type=RelationshipType.INVESTED_IN,
            allowed_source=IdentityKind.ORGANISATION,
            allowed_target=IdentityKind.ORGANISATION,
            properties_type=properties.InvestmentProperties
        ),

    RelationshipType.ACQUIRED:
        RelationshipSpecification(
            relationship_type=RelationshipType.ACQUIRED,
            allowed_source=IdentityKind.ORGANISATION,
            allowed_target=IdentityKind.ORGANISATION,
            properties_type= properties.AcquisitionProperties
        ),

    RelationshipType.HEADQUARTERED_IN:
        RelationshipSpecification(
            relationship_type=RelationshipType.HEADQUARTERED_IN,
            allowed_source=IdentityKind.ORGANISATION,
            allowed_target=IdentityKind.PLACE,
            properties_type=properties.HeadquartersProperties
        ),

    RelationshipType.OPERATES_IN:
        RelationshipSpecification(
            relationship_type=RelationshipType.OPERATES_IN,
            allowed_source=IdentityKind.ORGANISATION,
            allowed_target=IdentityKind.PLACE,
            properties_type=properties.MarketPresenceProperties
        ),

    RelationshipType.OPERATES_IN_INDUSTRY:
        RelationshipSpecification(
            relationship_type=RelationshipType.OPERATES_IN_INDUSTRY,
            allowed_source=IdentityKind.ORGANISATION,
            allowed_target=IdentityKind.INDUSTRY,
            properties_type=properties.IndustryParticipationProperties

        ),

    RelationshipType.OFFERS:
        RelationshipSpecification(
            relationship_type=RelationshipType.OFFERS,
            allowed_source=IdentityKind.ORGANISATION,
            allowed_target=IdentityKind.PRODUCT,
            properties_type=properties.ProductOfferingProperties
        ),

    RelationshipType.DEVELOPS:
        RelationshipSpecification(
            relationship_type=RelationshipType.DEVELOPS,
            allowed_source=IdentityKind.ORGANISATION,
            allowed_target=IdentityKind.PRODUCT,
            properties_type=properties.ProductDevelopmentProperties
        ),

    RelationshipType.USES:
        RelationshipSpecification(
            relationship_type=RelationshipType.USES,
            allowed_source=IdentityKind.ORGANISATION,
            allowed_target=IdentityKind.TECHNOLOGY,
            properties_type=properties.TechnologyAdoptionProperties
        ),

    RelationshipType.BUILT_WITH:
        RelationshipSpecification(
            relationship_type=RelationshipType.BUILT_WITH,
            allowed_source=IdentityKind.PRODUCT,
            allowed_target=IdentityKind.TECHNOLOGY,
            properties_type=properties.ProductTechnologyProperties
        ),

    RelationshipType.AVAILABLE_IN:
        RelationshipSpecification(
            relationship_type=RelationshipType.AVAILABLE_IN,
            allowed_source=IdentityKind.PRODUCT,
            allowed_target=IdentityKind.PLACE,
            properties_type=properties.ProductAvailabilityProperties
        ),

    RelationshipType.LOCATED_IN:
        RelationshipSpecification(
            relationship_type=RelationshipType.LOCATED_IN,
            allowed_source=IdentityKind.PLACE,
            allowed_target=IdentityKind.PLACE,
        ),

    RelationshipType.PART_OF:
        RelationshipSpecification(
            relationship_type=RelationshipType.PART_OF,
            allowed_source=IdentityKind.PLACE,
            allowed_target=IdentityKind.PLACE,
        ),
}


