"""Safe, deterministic JSON codec for explicitly supported domain values.

No imports are selected from payload content. Dataclasses and enums are
reconstructed only through the fixed registries below.
"""

from dataclasses import fields, is_dataclass
from datetime import date, datetime, timezone
from decimal import Decimal, InvalidOperation
from enum import Enum
import json
import math
from typing import Mapping
from uuid import UUID

from domain_models.Identity_model.identity import (
    IdentityKind,
    IdentityReference,
    IdentityRepresentations,
    LifecycleState,
)
from domain_models.Identity_model.Place_model.place import PlaceKind
from domain_models.Identity_model.Organisation_model.organisation_classification import (
    OrganisationClassification,
)
from domain_models.Identity_model.Organisation_model.classification_specific_domain_model.investor.investor import (
    InvestmentStage,
    InvestmentTypes,
)
from domain_models.Identity_model.Organisation_model.classification_specific_domain_model.startup.start_up import (
    StartupStages,
    StartupBusinessModels,
)
from domain_models.Provenance.claim import ClaimStatus
from domain_models.Provenance.source import Source, SourceReference, SourceType
from domain_models.Provenance.propositions import (
    IdentityAttributeProposition,
    IdentityProposalProposition,
    RelationshipPropertyProposition,
    RelationshipProposition,
)
from domain_models.Provenance.verification_assessment import AssessmentOutcome
from domain_models.Provenance.verification_assessment import VerificationAssessment
from domain_models.relationship_models.relationship import RelationshipReference
from domain_models.relationship_models.relationship_properties.properties_merge import (
    AcquisitionProperties,
    FounderProperties,
    HeadquartersProperties,
    IndustryParticipationProperties,
    InvestmentProperties,
    LeadershipProperties,
    MarketPresenceProperties,
    OwnershipProperties,
    PartnershipProperties,
    ProductAvailabilityProperties,
    ProductDevelopmentProperties,
    ProductOfferingProperties,
    ProductTechnologyProperties,
    ResidenceProperties,
    TechnologyAdoptionProperties,
)
from domain_models.relationship_models.relationship_properties.properties.acquisitionProperties import AcquisitionType
from domain_models.relationship_models.relationship_properties.properties.founderProperties import FoundingStage
from domain_models.relationship_models.relationship_properties.properties.headquartersProperties import (
    HeadquartersFunction,
    HeadquartersLevel,
)
from domain_models.relationship_models.relationship_properties.properties.marketPresenceProperties import OperatingStatus
from domain_models.relationship_models.relationship_properties.properties.ownershipProperties import OwnershipType
from domain_models.relationship_models.relationship_properties.properties.partnershipProperties import PartnershipStatus
from domain_models.relationship_models.relationship_properties.properties.productAvailabilityProperties import AvailabilityStatus
from domain_models.relationship_models.relationship_properties.properties.productDevelopmentProperties import DevelopmentStatus
from domain_models.relationship_models.relationship_properties.properties.productOfferingProperties import OfferingStatus
from domain_models.relationship_models.relationship_types.relationship_types import RelationshipType
from domain_models.Identity_model.Organisation_model.classification_specific_domain_model.accelerator.accelerator_programme import InvestmentTerms
from utils.representations import Duration, DurationUnit, Money


class ValueCodecError(ValueError):
    """A value is unsupported or a stored typed payload is malformed."""


_ENUM_TYPES: dict[str, type[Enum]] = {
    "identity_kind": IdentityKind,
    "lifecycle_state": LifecycleState,
    "place_kind": PlaceKind,
    "organisation_classification": OrganisationClassification,
    "investment_stage": InvestmentStage,
    "investment_types": InvestmentTypes,
    "startup_stage": StartupStages,
    "startup_business_model": StartupBusinessModels,
    "claim_status": ClaimStatus,
    "source_type": SourceType,
    "assessment_outcome": AssessmentOutcome,
    "relationship_type": RelationshipType,
    "acquisition_type": AcquisitionType,
    "founding_stage": FoundingStage,
    "headquarters_function": HeadquartersFunction,
    "headquarters_level": HeadquartersLevel,
    "operating_status": OperatingStatus,
    "ownership_type": OwnershipType,
    "partnership_status": PartnershipStatus,
    "availability_status": AvailabilityStatus,
    "development_status": DevelopmentStatus,
    "offering_status": OfferingStatus,
    "duration_unit": DurationUnit,
}
_ENUM_TAGS = {enum_type: tag for tag, enum_type in _ENUM_TYPES.items()}

_DATACLASS_TYPES: dict[str, type] = {
    "identity_reference": IdentityReference,
    "relationship_reference": RelationshipReference,
    "source_reference": SourceReference,
    "identity_representations": IdentityRepresentations,
    "source": Source,
    "verification_assessment": VerificationAssessment,
    "identity_attribute_proposition": IdentityAttributeProposition,
    "relationship_proposition": RelationshipProposition,
    "relationship_property_proposition": RelationshipPropertyProposition,
    "identity_proposal_proposition": IdentityProposalProposition,
    "money": Money,
    "duration": Duration,
    "investment_terms": InvestmentTerms,
    "acquisition_properties": AcquisitionProperties,
    "founder_properties": FounderProperties,
    "headquarters_properties": HeadquartersProperties,
    "industry_participation_properties": IndustryParticipationProperties,
    "investment_properties": InvestmentProperties,
    "leadership_properties": LeadershipProperties,
    "market_presence_properties": MarketPresenceProperties,
    "ownership_properties": OwnershipProperties,
    "partnership_properties": PartnershipProperties,
    "product_availability_properties": ProductAvailabilityProperties,
    "product_development_properties": ProductDevelopmentProperties,
    "product_offering_properties": ProductOfferingProperties,
    "product_technology_properties": ProductTechnologyProperties,
    "residence_properties": ResidenceProperties,
    "technology_adoption_properties": TechnologyAdoptionProperties,
}
_DATACLASS_TAGS = {model: tag for tag, model in _DATACLASS_TYPES.items()}


def dumps(value: object) -> str:
    """Encode a supported value as deterministic JSON."""
    try:
        return json.dumps(
            _encode(value),
            ensure_ascii=False,
            allow_nan=False,
            sort_keys=True,
            separators=(",", ":"),
        )
    except (TypeError, ValueError, OverflowError, RecursionError) as exc:
        if isinstance(exc, ValueCodecError):
            raise
        raise ValueCodecError(f"Unable to encode typed value: {exc}") from exc


def loads(payload: str | bytes | bytearray | object) -> object:
    """Decode a typed JSON value using only the fixed trusted registries."""
    if isinstance(payload, (str, bytes, bytearray)):
        try:
            raw = json.loads(payload)
        except (json.JSONDecodeError, UnicodeDecodeError, TypeError) as exc:
            raise ValueCodecError("Malformed typed JSON payload") from exc
    else:
        raw = payload
    return _decode(raw)


def _encode(value: object) -> object:
    # StrEnum and IntEnum inherit from primitive types, so tag enums first to
    # avoid reconstructing them as plain strings or integers.
    if isinstance(value, Enum):
        tag = _ENUM_TAGS.get(type(value))
        if tag is None:
            raise ValueCodecError(f"Unsupported enum type: {type(value).__name__}")
        return {"$type": "enum", "class": tag, "value": value.value}
    if value is None or isinstance(value, (bool, int, str)):
        return value
    if isinstance(value, float):
        if not math.isfinite(value):
            raise ValueCodecError("Non-finite floats are not supported")
        return value
    if isinstance(value, Decimal):
        if not value.is_finite():
            raise ValueCodecError("Non-finite Decimal values are not supported")
        return {"$type": "decimal", "value": str(value)}
    if isinstance(value, datetime):
        if value.tzinfo is None or value.utcoffset() is None:
            raise ValueCodecError("Datetime values must be timezone-aware")
        normalized = value.astimezone(timezone.utc)
        return {"$type": "datetime", "value": normalized.isoformat(timespec="microseconds")}
    if isinstance(value, date):
        return {"$type": "date", "value": value.isoformat()}
    if isinstance(value, UUID):
        return {"$type": "uuid", "value": str(value)}
    if isinstance(value, Mapping):
        pairs = [[_encode(key), _encode(item)] for key, item in value.items()]
        pairs.sort(key=lambda pair: _canonical_json(pair[0]))
        return {"$type": "dict", "items": pairs}
    if isinstance(value, list):
        return [_encode(item) for item in value]
    if isinstance(value, tuple):
        return {"$type": "tuple", "items": [_encode(item) for item in value]}
    if isinstance(value, set):
        items = [_encode(item) for item in value]
        items.sort(key=_canonical_json)
        return {"$type": "set", "items": items}
    if isinstance(value, frozenset):
        items = [_encode(item) for item in value]
        items.sort(key=_canonical_json)
        return {"$type": "frozenset", "items": items}
    if is_dataclass(value) and not isinstance(value, type):
        tag = _DATACLASS_TAGS.get(type(value))
        if tag is None:
            raise ValueCodecError(f"Unsupported dataclass type: {type(value).__name__}")
        params = getattr(type(value), "__dataclass_params__", None)
        if params is None or not params.frozen:
            raise ValueCodecError("Only registered frozen dataclasses are supported")
        return {
            "$type": "dataclass",
            "class": tag,
            "fields": {field.name: _encode(getattr(value, field.name)) for field in fields(value)},
        }
    raise ValueCodecError(f"Unsupported value type: {type(value).__name__}")


def _decode(value: object) -> object:
    if isinstance(value, list):
        return [_decode(item) for item in value]
    if not isinstance(value, dict):
        if isinstance(value, float) and not math.isfinite(value):
            raise ValueCodecError("Non-finite floats are not supported")
        return value
    tag = value.get("$type")
    if tag is None:
        raise ValueCodecError("Untagged object in typed JSON payload")
    try:
        if tag == "decimal":
            if set(value) != {"$type", "value"} or not isinstance(value["value"], str):
                raise ValueCodecError("Malformed Decimal payload")
            result = Decimal(value["value"])
            if not result.is_finite():
                raise ValueCodecError("Non-finite Decimal payload")
            return result
        if tag == "datetime":
            if set(value) != {"$type", "value"}:
                raise ValueCodecError("Malformed datetime payload")
            result = datetime.fromisoformat(value["value"])
            if result.tzinfo is None or result.utcoffset() is None:
                raise ValueCodecError("Stored datetime is not timezone-aware")
            return result.astimezone(timezone.utc)
        if tag == "date":
            if set(value) != {"$type", "value"}:
                raise ValueCodecError("Malformed date payload")
            return date.fromisoformat(value["value"])
        if tag == "uuid":
            if set(value) != {"$type", "value"}:
                raise ValueCodecError("Malformed UUID payload")
            return UUID(value["value"])
        if tag == "enum":
            if set(value) != {"$type", "class", "value"}:
                raise ValueCodecError("Malformed enum payload")
            enum_type = _ENUM_TYPES.get(value["class"])
            if enum_type is None:
                raise ValueCodecError(f"Unknown enum tag: {value['class']}")
            return enum_type(value["value"])
        if tag in {"tuple", "set", "frozenset"}:
            if set(value) != {"$type", "items"} or not isinstance(value["items"], list):
                raise ValueCodecError(f"Malformed {tag} payload")
            items = [_decode(item) for item in value["items"]]
            return tuple(items) if tag == "tuple" else set(items) if tag == "set" else frozenset(items)
        if tag == "dict":
            if set(value) != {"$type", "items"} or not isinstance(value["items"], list):
                raise ValueCodecError("Malformed dictionary payload")
            result = {}
            for pair in value["items"]:
                if not isinstance(pair, list) or len(pair) != 2:
                    raise ValueCodecError("Malformed dictionary item")
                key, item = (_decode(part) for part in pair)
                try:
                    if key in result:
                        raise ValueCodecError("Duplicate dictionary key")
                    result[key] = item
                except TypeError as exc:
                    raise ValueCodecError("Decoded dictionary key is not hashable") from exc
            return result
        if tag == "dataclass":
            if set(value) != {"$type", "class", "fields"} or not isinstance(value["fields"], dict):
                raise ValueCodecError("Malformed dataclass payload")
            model = _DATACLASS_TYPES.get(value["class"])
            if model is None:
                raise ValueCodecError(f"Unknown dataclass tag: {value['class']}")
            expected_fields = {field.name for field in fields(model)}
            if set(value["fields"]) != expected_fields:
                raise ValueCodecError(f"Stored fields do not match {value['class']}")
            decoded_fields = {name: _decode(item) for name, item in value["fields"].items()}
            return model(**decoded_fields)
    except (ValueError, TypeError, InvalidOperation, KeyError) as exc:
        if isinstance(exc, ValueCodecError):
            raise
        raise ValueCodecError(f"Invalid {tag!r} typed value: {exc}") from exc
    raise ValueCodecError(f"Unknown typed value tag: {tag!r}")


def _canonical_json(value: object) -> str:
    return json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":"))
