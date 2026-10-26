from datetime import date, datetime, timezone
from uuid import uuid4

import pytest

from domain_models.Identity_model.identity import IdentityKind, IdentityReference
from domain_models.Provenance.claim import Claim, ClaimStatus
from domain_models.Provenance.propositions import (
    IdentityAttributeProposition,
    IdentityProposalProposition,
    RelationshipProposition,
    RelationshipPropertyProposition,
)
from domain_models.Provenance.source import Source, SourceReference, SourceType
from domain_models.Provenance.verification_assessment import (
    AssessmentOutcome,
    VerificationAssessment,
)
from domain_models.relationship_models.relationship import RelationshipReference
from domain_models.relationship_models.relationship_types.relationship_types import (
    RelationshipType,
)


def test_source_accepts_valid_metadata_and_generates_utc_retrieval_time():
    source = Source(
        title="Annual report",
        source_type=SourceType.REPORT,
        publisher="Example publisher",
        url="https://example.test/report",
        publication_date=date(2025, 1, 2),
    )

    assert isinstance(source.reference, SourceReference)
    assert source.retrieved_at.tzinfo is not None
    assert source.retrieved_at.utcoffset().total_seconds() == 0


@pytest.mark.parametrize(
    "kwargs, error",
    [
        ({"title": "  ", "source_type": SourceType.REPORT}, ValueError),
        ({"title": "Report", "source_type": "report"}, TypeError),
        (
            {"title": "Report", "source_type": SourceType.REPORT, "publisher": " "},
            ValueError,
        ),
        (
            {"title": "Report", "source_type": SourceType.REPORT, "url": " "},
            ValueError,
        ),
        (
            {
                "title": "Report",
                "source_type": SourceType.REPORT,
                "retrieved_at": datetime(2025, 1, 1),
            },
            ValueError,
        ),
    ],
)
def test_source_rejects_invalid_values(kwargs, error):
    with pytest.raises(error):
        Source(**kwargs)


def test_propositions_validate_references_and_non_empty_names():
    identity_ref = IdentityReference()
    relation_ref = RelationshipReference()

    assert IdentityAttributeProposition(identity_ref, "birth_date", date(2000, 1, 1))
    assert RelationshipPropertyProposition(relation_ref, "since", 2020)
    assert IdentityProposalProposition(IdentityKind.PERSON, "Ada Example")
    assert RelationshipProposition(
        identity_ref,
        IdentityReference(),
        RelationshipType.BORN_IN,
    )

    with pytest.raises(TypeError):
        IdentityAttributeProposition(uuid4(), "birth_date", date(2000, 1, 1))
    with pytest.raises(ValueError):
        IdentityAttributeProposition(identity_ref, "  ", "value")
    with pytest.raises(ValueError):
        IdentityProposalProposition(IdentityKind.PERSON, " ")
    with pytest.raises(ValueError):
        IdentityProposalProposition(IdentityKind.PERSON, "Ada", aliases={1})


def test_proposition_values_are_copied_and_identity_attributes_mapping_is_read_only():
    value = {"facts": ["first"]}
    proposition = IdentityAttributeProposition(
        IdentityReference(), "profile", value
    )
    value["facts"].append("later")
    assert proposition.proposed_value == {"facts": ["first"]}

    attributes = {"country": "Wonderland"}
    proposal = IdentityProposalProposition(
        IdentityKind.PERSON, "Ada Example", attributes=attributes
    )
    attributes["country"] = "Elsewhere"
    assert proposal.attributes["country"] == "Wonderland"
    with pytest.raises(TypeError):
        proposal.attributes["country"] = "Elsewhere"


def test_relationship_proposition_checks_registry_property_model():
    identity_ref = IdentityReference()
    with pytest.raises(TypeError, match="does not accept properties"):
        RelationshipProposition(
            identity_ref,
            IdentityReference(),
            RelationshipType.BORN_IN,
            properties=object(),
        )
    with pytest.raises(TypeError, match="requires an"):
        RelationshipProposition(
            identity_ref,
            IdentityReference(),
            RelationshipType.FOUNDED,
        )


def test_claim_defaults_and_source_management():
    source_ref = SourceReference()
    claim = Claim(
        proposition=IdentityProposalProposition(IdentityKind.PERSON, "Ada Example"),
        source_references={source_ref},
    )
    assert claim.status is ClaimStatus.DRAFT
    assert claim.created_at.tzinfo is not None
    assert claim.source_references == frozenset({source_ref})

    another_source = SourceReference()
    claim.add_source(another_source)
    claim.remove_source(source_ref)
    assert claim.source_references == frozenset({another_source})


@pytest.mark.parametrize(
    "status, expected",
    [
        (ClaimStatus.PENDING_REVIEW, ClaimStatus.PENDING_REVIEW),
        (ClaimStatus.NEEDS_RESEARCH, ClaimStatus.NEEDS_RESEARCH),
        (ClaimStatus.SUPERSEDED, ClaimStatus.SUPERSEDED),
    ],
)
def test_claim_allows_declared_draft_transitions(status, expected):
    claim = Claim(
        proposition=IdentityProposalProposition(IdentityKind.PERSON, "Ada Example")
    )
    claim.transition_to(status)
    assert claim.status is expected


def test_claim_rejects_invalid_status_transition_and_naive_timestamp():
    claim = Claim(
        proposition=IdentityProposalProposition(IdentityKind.PERSON, "Ada Example")
    )
    with pytest.raises(ValueError, match="Invalid claim status transition"):
        claim.transition_to(ClaimStatus.ACCEPTED)
    with pytest.raises(ValueError, match="timezone-aware"):
        Claim(
            proposition=IdentityProposalProposition(
                IdentityKind.PERSON, "Ada Example"
            ),
            created_at=datetime(2025, 1, 1),
        )


def test_verification_assessment_accepts_valid_values_and_generates_utc_time():
    assessment = VerificationAssessment(
        claim_reference=uuid4(),
        outcome=AssessmentOutcome.ACCEPT,
        rationale="Supported by the cited report.",
        assessed_by="reviewer@example.test",
        review_process="two-person review",
    )
    assert assessment.assessed_at.tzinfo is not None
    assert assessment.assessed_at.utcoffset().total_seconds() == 0


@pytest.mark.parametrize(
    "kwargs, error",
    [
        ({"claim_reference": "not-a-uuid"}, TypeError),
        ({"outcome": "accept"}, TypeError),
        ({"rationale": " "}, ValueError),
        ({"assessed_by": " "}, ValueError),
        ({"assessed_at": datetime(2025, 1, 1)}, ValueError),
        ({"review_process": " "}, ValueError),
    ],
)
def test_verification_assessment_rejects_invalid_values(kwargs, error):
    values = {
        "claim_reference": uuid4(),
        "outcome": AssessmentOutcome.REJECT,
        "rationale": "Insufficient support.",
        "assessed_by": "reviewer@example.test",
    }
    values.update(kwargs)
    with pytest.raises(error):
        VerificationAssessment(**values)
