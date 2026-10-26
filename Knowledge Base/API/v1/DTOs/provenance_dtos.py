"""Request and response DTOs for Provenance domain resources."""

from datetime import date, datetime
import json
from typing import Annotated, Any, Literal, Union
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field

from API.v1.DTOs.relationship_properties import (
    deserialize_relationship_properties,
    serialize_relationship_properties,
)
from application.persistence.typed_value_codec import dumps, loads
from domain_models.Identity_model.identity import IdentityKind, IdentityReference
from domain_models.Provenance.claim import Claim, ClaimStatus
from domain_models.Provenance.propositions import (
    IdentityAttributeProposition,
    IdentityProposalProposition,
    Proposition,
    RelationshipPropertyProposition,
    RelationshipProposition,
)
from domain_models.Provenance.source import Source, SourceReference, SourceType
from domain_models.Provenance.verification_assessment import (
    AssessmentOutcome,
    VerificationAssessment,
)
from domain_models.relationship_models.relationship import RelationshipReference
from domain_models.relationship_models.relationship_types.relationship_types import RelationshipType


class CreateSourceRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")

    title: str = Field(min_length=1)
    source_type: SourceType
    publisher: str | None = None
    url: str | None = None
    publication_date: date | None = None
    retrieved_at: datetime | None = None


class SourceResponse(BaseModel):
    model_config = ConfigDict(extra="forbid")

    id: UUID
    title: str
    source_type: SourceType
    publisher: str | None
    url: str | None
    publication_date: date | None
    retrieved_at: datetime


def to_source_response(source: Source) -> SourceResponse:
    return SourceResponse(
        id=source.reference.value,
        title=source.title,
        source_type=source.source_type,
        publisher=source.publisher,
        url=source.url,
        publication_date=source.publication_date,
        retrieved_at=source.retrieved_at,
    )


class IdentityAttributePropositionRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")
    proposition_type: Literal["identity_attribute"]
    identity_id: UUID
    attribute_name: str = Field(min_length=1)
    proposed_value: Any


class RelationshipPropositionRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")
    proposition_type: Literal["relationship"]
    source_identity_id: UUID
    target_identity_id: UUID
    relationship_type: RelationshipType
    existing_relationship_id: UUID | None = None
    properties: dict[str, Any] | None = None


class RelationshipPropertyPropositionRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")
    proposition_type: Literal["relationship_property"]
    relationship_id: UUID
    property_name: str = Field(min_length=1)
    proposed_value: Any


class IdentityProposalPropositionRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")
    proposition_type: Literal["identity_proposal"]
    identity_kind: IdentityKind
    canonical_name: str = Field(min_length=1)
    aliases: list[str] = Field(default_factory=list)
    attributes: dict[str, Any] = Field(default_factory=dict)


ClaimPropositionRequest = Annotated[
    Union[
        IdentityAttributePropositionRequest,
        RelationshipPropositionRequest,
        RelationshipPropertyPropositionRequest,
        IdentityProposalPropositionRequest,
    ],
    Field(discriminator="proposition_type"),
]


class CreateClaimRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")

    proposition: ClaimPropositionRequest
    source_ids: list[UUID] = Field(default_factory=list)
    research_notes: str = ""


class IdentityAttributePropositionResponse(IdentityAttributePropositionRequest):
    proposed_value: Any


class RelationshipPropositionResponse(RelationshipPropositionRequest):
    properties: dict[str, Any] | None = None


class RelationshipPropertyPropositionResponse(RelationshipPropertyPropositionRequest):
    proposed_value: Any


class IdentityProposalPropositionResponse(IdentityProposalPropositionRequest):
    attributes: Any = Field(default_factory=dict)


ClaimPropositionResponse = Annotated[
    Union[
        IdentityAttributePropositionResponse,
        RelationshipPropositionResponse,
        RelationshipPropertyPropositionResponse,
        IdentityProposalPropositionResponse,
    ],
    Field(discriminator="proposition_type"),
]


class ClaimResponse(BaseModel):
    model_config = ConfigDict(extra="forbid")

    id: UUID
    status: ClaimStatus
    research_notes: str
    created_at: datetime
    source_ids: list[UUID]
    proposition: ClaimPropositionResponse


class UpdateClaimStatusRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")
    status: ClaimStatus


class MaterialiseClaimRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")

    allow_possible_duplicate: bool = False


class ClaimMaterialisationResponse(BaseModel):
    model_config = ConfigDict(extra="forbid")

    claim_id: UUID
    target_kind: Literal["identity", "relationship"]
    target_id: UUID | None
    outcome: str
    action: str | None
    override_applied: bool
    already_materialised: bool
    candidates: list[dict[str, Any]] = Field(default_factory=list)
    candidates_truncated: bool = False


class CreateAssessmentRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")

    outcome: AssessmentOutcome
    rationale: str = Field(min_length=1)
    assessed_by: str = Field(min_length=1)
    review_process: str | None = None
    transition_claim_to: ClaimStatus | None = None


class VerificationAssessmentResponse(BaseModel):
    model_config = ConfigDict(extra="forbid")

    id: UUID
    claim_id: UUID
    outcome: AssessmentOutcome
    rationale: str
    assessed_by: str
    assessed_at: datetime
    review_process: str | None


class AssessmentCreatedResponse(BaseModel):
    model_config = ConfigDict(extra="forbid")

    assessment: VerificationAssessmentResponse
    claim_status: ClaimStatus | None = None


def to_assessment_response(
    assessment: VerificationAssessment,
) -> VerificationAssessmentResponse:
    return VerificationAssessmentResponse(
        id=assessment.reference,
        claim_id=assessment.claim_reference,
        outcome=assessment.outcome,
        rationale=assessment.rationale,
        assessed_by=assessment.assessed_by,
        assessed_at=assessment.assessed_at,
        review_process=assessment.review_process,
    )


def to_claim_response(claim: Claim) -> ClaimResponse:
    return ClaimResponse(
        id=claim.reference,
        status=claim.status,
        research_notes=claim.research_notes,
        created_at=claim.created_at,
        source_ids=sorted(
            (source.value for source in claim.source_references), key=str
        ),
        proposition=to_proposition_response(claim.proposition),
    )


def to_proposition_response(proposition: Proposition):
    if isinstance(proposition, IdentityAttributeProposition):
        return IdentityAttributePropositionResponse(
            proposition_type="identity_attribute",
            identity_id=proposition.identity_reference.value,
            attribute_name=proposition.attribute_name,
            proposed_value=_encode_api_value(proposition.proposed_value),
        )
    if isinstance(proposition, RelationshipProposition):
        return RelationshipPropositionResponse(
            proposition_type="relationship",
            source_identity_id=proposition.source_reference.value,
            target_identity_id=proposition.target_reference.value,
            relationship_type=proposition.relationship_type,
            existing_relationship_id=(
                None
                if proposition.existing_relationship_reference is None
                else proposition.existing_relationship_reference.value
            ),
            properties=serialize_relationship_properties(
                proposition.relationship_type, proposition.properties
            ),
        )
    if isinstance(proposition, RelationshipPropertyProposition):
        return RelationshipPropertyPropositionResponse(
            proposition_type="relationship_property",
            relationship_id=proposition.relationship_reference.value,
            property_name=proposition.property_name,
            proposed_value=_encode_api_value(proposition.proposed_value),
        )
    if isinstance(proposition, IdentityProposalProposition):
        return IdentityProposalPropositionResponse(
            proposition_type="identity_proposal",
            identity_kind=proposition.identity_kind,
            canonical_name=proposition.canonical_name,
            aliases=sorted(proposition.aliases),
            attributes=_encode_api_value(proposition.attributes),
        )
    raise TypeError(f"Unsupported proposition type: {type(proposition).__name__}")


def to_domain_proposition(request: ClaimPropositionRequest) -> Proposition:
    if isinstance(request, IdentityAttributePropositionRequest):
        return IdentityAttributeProposition(
            IdentityReference(request.identity_id),
            request.attribute_name,
            _decode_api_value(request.proposed_value),
        )
    if isinstance(request, RelationshipPropositionRequest):
        properties = deserialize_relationship_properties(
            request.relationship_type, request.properties
        )
        return RelationshipProposition(
            IdentityReference(request.source_identity_id),
            IdentityReference(request.target_identity_id),
            request.relationship_type,
            properties,
            None
            if request.existing_relationship_id is None
            else RelationshipReference(request.existing_relationship_id),
        )
    if isinstance(request, RelationshipPropertyPropositionRequest):
        return RelationshipPropertyProposition(
            RelationshipReference(request.relationship_id),
            request.property_name,
            _decode_api_value(request.proposed_value),
        )
    if isinstance(request, IdentityProposalPropositionRequest):
        attributes = {
            key: _decode_api_value(value)
            for key, value in request.attributes.items()
        }
        return IdentityProposalProposition(
            request.identity_kind,
            request.canonical_name,
            frozenset(request.aliases),
            attributes,
        )
    raise TypeError(f"Unsupported proposition request: {type(request).__name__}")


def _decode_api_value(value: Any) -> Any:
    """Decode explicit codec tags; preserve ordinary JSON as normal containers."""
    if isinstance(value, dict):
        if "$type" in value:
            return loads(json.dumps(value, ensure_ascii=False))
        return {key: _decode_api_value(item) for key, item in value.items()}
    if isinstance(value, list):
        return [_decode_api_value(item) for item in value]
    return value


def _encode_api_value(value: object) -> Any:
    return json.loads(dumps(value))
