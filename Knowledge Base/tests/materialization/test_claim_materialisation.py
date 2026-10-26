"""Unit coverage for accepted identity and relationship Claim materialisation.

These tests use in-memory repositories and a fake transaction context. They do
not connect to or modify the development database.
"""

from contextlib import contextmanager
from dataclasses import fields
from datetime import date
from decimal import Decimal
from uuid import UUID, uuid4

import pytest

from application.resolution.identity.contracts import (
    CandidateMatch,
    CandidateMatchKind,
    IdentityResolutionResult,
    ResolutionOutcome,
)
from application.resolution.relationship.contracts import (
    RelationshipCandidateMatch,
    RelationshipResolutionOutcome,
    RelationshipResolutionResult,
)
from application.services.claim_materialisation_service import (
    ClaimMaterialisationService,
)
from domain_models.Identity_model.identity import (
    Identity,
    IdentityKind,
    IdentityReference,
    IdentityRepresentations,
)
from domain_models.Identity_model.Industry_model.industry import Industry
from domain_models.Identity_model.Organisation_model.classification_specific_domain_model.accelerator.accelerator import Accelerator
from domain_models.Identity_model.Organisation_model.classification_specific_domain_model.accelerator.accelerator_programme import AcceleratorProgramme, InvestmentTerms
from domain_models.Identity_model.Organisation_model.classification_specific_domain_model.investor.investor import (
    InvestmentStage,
    InvestmentTypes,
    Investor,
)
from domain_models.Identity_model.Organisation_model.classification_specific_domain_model.startup.start_up import (
    Startup,
    StartupBusinessModels,
    StartupStages,
)
from domain_models.Identity_model.Organisation_model.organisation import Organisation
from domain_models.Identity_model.Organisation_model.organisation_classification import OrganisationClassification
from domain_models.Identity_model.Person_model.person import Person
from domain_models.Identity_model.Place_model.place import Place, PlaceKind
from domain_models.Identity_model.Product_model.product import Product
from domain_models.Identity_model.Technology_model.technology import Technology
from domain_models.Provenance.claim import Claim, ClaimStatus
from domain_models.Provenance.materialisation import (
    MaterialisationAction,
    MaterialisationOutcome,
    MaterialisationTargetKind,
)
from domain_models.Provenance.propositions import (
    IdentityAttributeProposition,
    IdentityProposalProposition,
    RelationshipPropertyProposition,
    RelationshipProposition,
)
from domain_models.relationship_models.relationship import (
    Relationship,
    RelationshipReference,
)
from domain_models.relationship_models.relationship_types.relationship_type_specification import specification_registry
from domain_models.relationship_models.relationship_types.relationship_types import RelationshipType
from repositories.utils.errors import RepositoryNotFoundError
from utils.representations import Duration, DurationUnit, Money


class FakeDatabaseManager:
    @contextmanager
    def transaction(self):
        yield object()


class FakeClaimRepository:
    def __init__(self, claim):
        self.claim = claim

    def get_by_reference_for_update(self, reference, *, connection):
        if self.claim is not None and self.claim.reference == reference:
            return self.claim
        return None


class FakeMaterialisationRepository:
    def __init__(self):
        self.by_claim = {}

    def get_by_claim_reference(self, reference, *, connection):
        return self.by_claim.get(reference)

    def create(self, materialisation, *, connection):
        assert materialisation.claim_reference not in self.by_claim
        self.by_claim[materialisation.claim_reference] = materialisation


class FakeIdentityRepository:
    def __init__(self, identities):
        self.identities = identities
        self.saved = []

    def save(self, identity, *, connection):
        self.saved.append(identity)
        self.identities[identity.reference.value] = identity


class FakeIdentityResolver:
    def __init__(self, identities):
        self.identities = identities

    def get_by_id(self, reference, *, connection=None):
        identifier = reference.value if isinstance(reference, IdentityReference) else reference
        return self.identities.get(identifier)


class FakeRelationshipRepository:
    def __init__(self):
        self.relationships = {}
        self.saved = []

    def save(self, relationship, *, connection):
        self.saved.append(relationship)
        self.relationships[relationship.get_reference().value] = relationship

    def get_by_id(self, reference, *, connection):
        identifier = reference.value if isinstance(reference, RelationshipReference) else reference
        return self.relationships.get(identifier)


class FakeIdentityResolutionService:
    def __init__(self, outcome=ResolutionOutcome.NO_MATCH, candidate=None):
        self.outcome = outcome
        self.candidate = candidate
        self.received = []

    def resolve(self, request, *, connection):
        identity = request.identity
        self.received.append(identity)
        if self.outcome is ResolutionOutcome.NO_MATCH:
            return IdentityResolutionResult(outcome=self.outcome)
        match_kind = (
            CandidateMatchKind.EXACT_MATCH
            if self.outcome is ResolutionOutcome.EXACT_MATCH
            else CandidateMatchKind.POSSIBLE_DUPLICATE
        )
        return IdentityResolutionResult(
            outcome=self.outcome,
            matches=(CandidateMatch(self.candidate, match_kind, ()),),
            ambiguous=self.outcome is ResolutionOutcome.POSSIBLE_DUPLICATE,
        )


class FakeRelationshipResolutionService:
    def __init__(
        self,
        outcome=RelationshipResolutionOutcome.NO_MATCH,
        candidate=None,
    ):
        self.outcome = outcome
        self.candidate = candidate
        self.received = []

    def resolve(self, request, *, connection):
        relationship = request.relationship
        self.received.append(relationship)
        if self.outcome is RelationshipResolutionOutcome.NO_MATCH:
            return RelationshipResolutionResult(outcome=self.outcome)
        return RelationshipResolutionResult(
            outcome=self.outcome,
            matches=(RelationshipCandidateMatch(self.candidate, ()),),
            ambiguous=self.outcome is RelationshipResolutionOutcome.POSSIBLE_DUPLICATE,
        )


def _identity(kind, name=None):
    representations = IdentityRepresentations(canonical_name=name or f"{kind.value}-{uuid4()}")
    if kind is IdentityKind.PERSON:
        return Person(representations=representations)
    if kind is IdentityKind.ORGANISATION:
        return Organisation(representations=representations, classifications=set())
    if kind is IdentityKind.PLACE:
        return Place(representations=representations, place_kind=PlaceKind.CITY)
    if kind is IdentityKind.INDUSTRY:
        return Industry(representations=representations)
    if kind is IdentityKind.PRODUCT:
        return Product(representations=representations)
    if kind is IdentityKind.TECHNOLOGY:
        return Technology(representations=representations)
    raise AssertionError(f"No identity test factory for {kind}")


def _property_model(properties_type):
    if properties_type is None:
        return None
    required = [
        item.name
        for item in fields(properties_type)
        if item.default.__class__.__name__ == "_MISSING_TYPE"
        and item.default_factory.__class__.__name__ == "_MISSING_TYPE"
    ]
    assert not required, f"Update property fixture for {properties_type}: {required}"
    return properties_type()


def _relationship(type_, identities):
    specification = specification_registry.get(type_)
    source = _identity(specification.allowed_source)
    target = _identity(specification.allowed_target)
    identities[source.reference.value] = source
    identities[target.reference.value] = target
    return Relationship(
        source=source,
        target=target,
        type=type_,
        properties=_property_model(specification.properties_type),
    )


def _make_service(
    claim,
    *,
    identity_outcome=ResolutionOutcome.NO_MATCH,
    identity_candidate=None,
    relationship_outcome=RelationshipResolutionOutcome.NO_MATCH,
    relationship_candidate=None,
    monkeypatch=None,
):
    if monkeypatch is not None:
        import application.services.create_orchestration as orchestration

        monkeypatch.setattr(orchestration, "acquire_identity_resolution_locks", lambda *a, **k: None)
        monkeypatch.setattr(orchestration, "lock_relationship_endpoints", lambda *a, **k: None)

    identities = {}
    if identity_candidate is not None:
        identities[identity_candidate.reference.value] = identity_candidate
    identity_repositories = {
        kind: FakeIdentityRepository(identities)
        for kind in IdentityKind
    }
    identity_resolver = FakeIdentityResolver(identities)
    relationship_repository = FakeRelationshipRepository()
    if relationship_candidate is not None:
        relationship_repository.relationships[
            relationship_candidate.get_reference().value
        ] = relationship_candidate
    identity_resolution = FakeIdentityResolutionService(
        identity_outcome, identity_candidate
    )
    relationship_resolution = FakeRelationshipResolutionService(
        relationship_outcome, relationship_candidate
    )
    materialisations = FakeMaterialisationRepository()
    service = ClaimMaterialisationService(
        claim_repository=FakeClaimRepository(claim),
        materialisation_repository=materialisations,
        identity_repositories=identity_repositories,
        relationship_repository=relationship_repository,
        identity_resolver=identity_resolver,
        identity_resolution_service=identity_resolution,
        relationship_resolution_service=relationship_resolution,
        database_manager=FakeDatabaseManager(),
    )
    return service, identity_repositories, relationship_repository, materialisations


@pytest.mark.parametrize(
    "kind, attributes, expected_type",
    [
        (IdentityKind.PERSON, {}, Person),
        (IdentityKind.INDUSTRY, {}, Industry),
        (IdentityKind.PRODUCT, {}, Product),
        (IdentityKind.TECHNOLOGY, {}, Technology),
        (IdentityKind.PLACE, {"place_kind": "city"}, Place),
        (
            IdentityKind.ORGANISATION,
            {
                "classifications": [
                    {
                        "classification": "startup",
                        "founding_year": 2021,
                        "stage": "seed",
                        "business_model": "b2b",
                    }
                ]
            },
            Organisation,
        ),
    ],
)
def test_identity_kind_proposals_build_and_materialise(kind, attributes, expected_type, monkeypatch):
    claim = Claim(
        proposition=IdentityProposalProposition(kind, f"Test {kind.value}", attributes=attributes),
        status=ClaimStatus.ACCEPTED,
    )
    service, repositories, _, records = _make_service(claim, monkeypatch=monkeypatch)

    result = service.materialise(claim.reference)

    assert result.action is MaterialisationAction.CREATED
    assert isinstance(result.entity, expected_type)
    assert result.entity.kind is kind
    assert repositories[kind].saved == [result.entity]
    assert records.get_by_claim_reference(claim.reference, connection=None).target_reference == result.entity.reference.value


@pytest.mark.parametrize(
    "classification, details, model_type",
    [
        (
            "startup",
            {"founding_year": 2020, "stage": "seed", "business_model": "b2b"},
            Startup,
        ),
        (
            "investor",
            {"investor_type": "venture_capital", "investment_stage": "seed"},
            Investor,
        ),
        ("accelerator", {"programmes": []}, Accelerator),
        ("incubator", {}, None),
    ],
)
def test_all_organisation_classifications_materialise_with_their_domain_models(
    classification, details, model_type, monkeypatch
):
    claim = Claim(
        proposition=IdentityProposalProposition(
            IdentityKind.ORGANISATION,
            f"Test {classification}",
            attributes={"classifications": [{"classification": classification, **details}]},
        ),
        status=ClaimStatus.ACCEPTED,
    )
    service, _, _, _ = _make_service(claim, monkeypatch=monkeypatch)

    organisation = service.materialise(claim.reference).entity

    classification_enum = OrganisationClassification(classification)
    assert organisation.has_classification(classification_enum)
    model = organisation.get_classification_model(classification_enum)
    assert (model is None) if model_type is None else isinstance(model, model_type)


def test_accelerator_programme_values_are_converted_to_domain_types(monkeypatch):
    claim = Claim(
        proposition=IdentityProposalProposition(
            IdentityKind.ORGANISATION,
            "Example accelerator",
            attributes={
                "classifications": [
                    {
                        "classification": "accelerator",
                        "programmes": [
                            {
                                "name": "Launch",
                                "duration": {
                                    "value": "12",
                                    "unit": "months",
                                    "start_date": "2026-01-01",
                                    "end_date": "2026-12-31",
                                },
                                "investment_terms": {
                                    "money": {"amount": "10000.00", "currency": "USD"},
                                    "equity_percentage": "5",
                                },
                            }
                        ],
                    }
                ]
            },
        ),
        status=ClaimStatus.ACCEPTED,
    )
    service, _, _, _ = _make_service(claim, monkeypatch=monkeypatch)

    organisation = service.materialise(claim.reference).entity
    programme = organisation.get_classification_model(
        OrganisationClassification.ACCELERATOR
    ).programmes[0]

    assert isinstance(programme, AcceleratorProgramme)
    assert programme.duration.value == Decimal("12")
    assert programme.duration.unit is DurationUnit.MONTHS
    assert programme.duration.start_date == date(2026, 1, 1)
    assert isinstance(programme.investment_terms.money, Money)
    assert programme.investment_terms.equity_percentage == Decimal("5")


def test_exact_identity_match_links_existing_without_saving_new_identity(monkeypatch):
    candidate = Person(representations=IdentityRepresentations("Ada Example"))
    claim = Claim(
        proposition=IdentityProposalProposition(IdentityKind.PERSON, "Ada Example"),
        status=ClaimStatus.ACCEPTED,
    )
    service, repositories, _, records = _make_service(
        claim,
        identity_outcome=ResolutionOutcome.EXACT_MATCH,
        identity_candidate=candidate,
        monkeypatch=monkeypatch,
    )

    result = service.materialise(claim.reference)

    assert result.entity is candidate
    assert result.outcome is MaterialisationOutcome.EXACT_MATCH
    assert result.action is MaterialisationAction.LINKED
    assert not result.override_applied
    assert not repositories[IdentityKind.PERSON].saved
    assert records.get_by_claim_reference(claim.reference, connection=None).target_reference == candidate.reference.value


@pytest.mark.parametrize("allow_override, expected_action", [(False, None), (True, MaterialisationAction.CREATED)])
def test_possible_identity_duplicate_is_blocked_or_created_with_audited_override(
    allow_override, expected_action, monkeypatch
):
    candidate = Person(representations=IdentityRepresentations("Ada Example"))
    claim = Claim(
        proposition=IdentityProposalProposition(IdentityKind.PERSON, "Ada Example"),
        status=ClaimStatus.ACCEPTED,
    )
    service, repositories, _, records = _make_service(
        claim,
        identity_outcome=ResolutionOutcome.POSSIBLE_DUPLICATE,
        identity_candidate=candidate,
        monkeypatch=monkeypatch,
    )

    result = service.materialise(
        claim.reference, allow_possible_duplicate=allow_override
    )

    assert result.action is expected_action
    if allow_override:
        assert result.override_applied
        record = records.get_by_claim_reference(claim.reference, connection=None)
        assert record.override_applied
        assert record.outcome is MaterialisationOutcome.POSSIBLE_DUPLICATE
    else:
        assert result.entity is None
        assert not result.override_applied
        assert records.get_by_claim_reference(claim.reference, connection=None) is None
        assert not repositories[IdentityKind.PERSON].saved


def test_materialisation_retry_returns_the_recorded_canonical_target(monkeypatch):
    claim = Claim(
        proposition=IdentityProposalProposition(IdentityKind.PERSON, "Retry Person"),
        status=ClaimStatus.ACCEPTED,
    )
    service, _, _, records = _make_service(claim, monkeypatch=monkeypatch)
    first = service.materialise(claim.reference)
    second = service.materialise(claim.reference)

    assert second.already_materialised
    assert second.entity is first.entity
    assert second.action is first.action
    assert len(records.by_claim) == 1


def test_non_accepted_claim_is_rejected_without_a_materialisation_record(monkeypatch):
    claim = Claim(
        proposition=IdentityProposalProposition(IdentityKind.PERSON, "Draft Person"),
        status=ClaimStatus.DRAFT,
    )
    service, _, _, records = _make_service(claim, monkeypatch=monkeypatch)

    with pytest.raises(ValueError, match="Only accepted Claims"):
        service.materialise(claim.reference)
    assert records.get_by_claim_reference(claim.reference, connection=None) is None


@pytest.mark.parametrize(
    "kind, attributes, message",
    [
        (IdentityKind.PLACE, {}, "place_kind"),
        (IdentityKind.ORGANISATION, {}, "classifications"),
        (IdentityKind.PERSON, {"birth_date": "2000-01-01"}, "do not accept additional"),
    ],
)
def test_incomplete_or_unmodelled_identity_attributes_are_rejected(
    kind, attributes, message, monkeypatch
):
    claim = Claim(
        proposition=IdentityProposalProposition(kind, "Invalid proposal", attributes=attributes),
        status=ClaimStatus.ACCEPTED,
    )
    service, _, _, records = _make_service(claim, monkeypatch=monkeypatch)

    with pytest.raises(ValueError, match=message):
        service.materialise(claim.reference)
    assert records.get_by_claim_reference(claim.reference, connection=None) is None


@pytest.mark.parametrize(
    "proposition_factory",
    [
        lambda: IdentityAttributeProposition(IdentityReference(), "name", "New name"),
        lambda: RelationshipPropertyProposition(RelationshipReference(), "since", 2020),
    ],
)
def test_attribute_and_relationship_property_claims_remain_deferred(
    proposition_factory, monkeypatch
):
    claim = Claim(proposition=proposition_factory(), status=ClaimStatus.ACCEPTED)
    service, _, _, records = _make_service(claim, monkeypatch=monkeypatch)

    with pytest.raises(ValueError, match="not enabled for materialisation"):
        service.materialise(claim.reference)
    assert records.get_by_claim_reference(claim.reference, connection=None) is None


@pytest.mark.parametrize("relationship_type", list(RelationshipType))
def test_every_registered_relationship_type_materialises_without_a_duplicate(
    relationship_type, monkeypatch
):
    identities = {}
    relationship = _relationship(relationship_type, identities)
    proposition = RelationshipProposition(
        relationship.get_source().reference,
        relationship.get_target().reference,
        relationship_type,
        relationship.get_properties(),
    )
    claim = Claim(proposition=proposition, status=ClaimStatus.ACCEPTED)
    service, _, relationship_repository, records = _make_service(
        claim, monkeypatch=monkeypatch
    )
    # Seed the references used by this test's proposition as persisted endpoints.
    service._identity_resolver.identities.update(identities)

    result = service.materialise(claim.reference)

    assert result.action is MaterialisationAction.CREATED
    assert result.entity.get_type() is relationship_type
    assert relationship_repository.saved == [result.entity]
    assert records.get_by_claim_reference(claim.reference, connection=None).target_kind is MaterialisationTargetKind.RELATIONSHIP


def test_relationship_exact_match_links_existing_relationship(monkeypatch):
    identities = {}
    existing = _relationship(RelationshipType.BORN_IN, identities)
    proposition = RelationshipProposition(
        existing.get_source().reference,
        existing.get_target().reference,
        RelationshipType.BORN_IN,
        None,
    )
    claim = Claim(proposition=proposition, status=ClaimStatus.ACCEPTED)
    service, _, relationship_repository, records = _make_service(
        claim,
        relationship_outcome=RelationshipResolutionOutcome.EXACT_MATCH,
        relationship_candidate=existing,
        monkeypatch=monkeypatch,
    )
    service._identity_resolver.identities.update(identities)

    result = service.materialise(claim.reference)

    assert result.entity is existing
    assert result.action is MaterialisationAction.LINKED
    assert not relationship_repository.saved
    assert records.get_by_claim_reference(claim.reference, connection=None).target_reference == existing.get_reference().value


@pytest.mark.parametrize("allow_override", [False, True])
def test_possible_relationship_duplicate_requires_explicit_override(allow_override, monkeypatch):
    identities = {}
    existing = _relationship(RelationshipType.BORN_IN, identities)
    claim = Claim(
        proposition=RelationshipProposition(
            existing.get_source().reference,
            existing.get_target().reference,
            RelationshipType.BORN_IN,
            None,
        ),
        status=ClaimStatus.ACCEPTED,
    )
    service, _, relationship_repository, records = _make_service(
        claim,
        relationship_outcome=RelationshipResolutionOutcome.POSSIBLE_DUPLICATE,
        relationship_candidate=existing,
        monkeypatch=monkeypatch,
    )
    service._identity_resolver.identities.update(identities)

    result = service.materialise(
        claim.reference, allow_possible_duplicate=allow_override
    )

    if allow_override:
        assert result.action is MaterialisationAction.CREATED
        assert result.override_applied
        assert records.get_by_claim_reference(claim.reference, connection=None).override_applied
        assert len(relationship_repository.saved) == 1
    else:
        assert result.action is None
        assert result.entity is None
        assert records.get_by_claim_reference(claim.reference, connection=None) is None
        assert not relationship_repository.saved


def test_explicit_relationship_reference_links_only_the_exact_proposal(monkeypatch):
    identities = {}
    existing = _relationship(RelationshipType.BORN_IN, identities)
    claim = Claim(
        proposition=RelationshipProposition(
            existing.get_source().reference,
            existing.get_target().reference,
            RelationshipType.BORN_IN,
            None,
            existing.get_reference(),
        ),
        status=ClaimStatus.ACCEPTED,
    )
    service, _, relationship_repository, records = _make_service(
        claim, monkeypatch=monkeypatch
    )
    relationship_repository.relationships[existing.get_reference().value] = existing
    service._identity_resolver.identities.update(identities)

    result = service.materialise(claim.reference)

    assert result.entity is existing
    assert result.action is MaterialisationAction.LINKED
    assert records.get_by_claim_reference(claim.reference, connection=None)
    assert not relationship_repository.saved


def test_explicit_relationship_reference_with_wrong_endpoints_is_rejected(monkeypatch):
    identities = {}
    existing = _relationship(RelationshipType.BORN_IN, identities)
    other_place = Place(
        representations=IdentityRepresentations("Another place"),
        place_kind=PlaceKind.CITY,
    )
    identities[other_place.reference.value] = other_place
    claim = Claim(
        proposition=RelationshipProposition(
            existing.get_source().reference,
            other_place.reference,
            RelationshipType.BORN_IN,
            None,
            existing.get_reference(),
        ),
        status=ClaimStatus.ACCEPTED,
    )
    service, _, relationship_repository, records = _make_service(
        claim, monkeypatch=monkeypatch
    )
    relationship_repository.relationships[existing.get_reference().value] = existing
    service._identity_resolver.identities.update(identities)

    with pytest.raises(ValueError, match="does not exactly match"):
        service.materialise(claim.reference)
    assert records.get_by_claim_reference(claim.reference, connection=None) is None


def test_relationship_missing_endpoint_is_reported(monkeypatch):
    person = _identity(IdentityKind.PERSON)
    missing_place = Place(
        representations=IdentityRepresentations("Missing place"),
        place_kind=PlaceKind.CITY,
    )
    claim = Claim(
        proposition=RelationshipProposition(
            person.reference,
            missing_place.reference,
            RelationshipType.BORN_IN,
            None,
        ),
        status=ClaimStatus.ACCEPTED,
    )
    service, _, _, _ = _make_service(claim, monkeypatch=monkeypatch)
    service._identity_resolver.identities[person.reference.value] = person

    with pytest.raises(RepositoryNotFoundError, match="does not exist"):
        service.materialise(claim.reference)


def test_relationship_endpoint_with_wrong_identity_kind_is_rejected(monkeypatch):
    person = _identity(IdentityKind.PERSON)
    wrong_target = _identity(IdentityKind.PERSON)
    claim = Claim(
        proposition=RelationshipProposition(
            person.reference,
            wrong_target.reference,
            RelationshipType.BORN_IN,
            None,
        ),
        status=ClaimStatus.ACCEPTED,
    )
    service, _, _, _ = _make_service(claim, monkeypatch=monkeypatch)
    service._identity_resolver.identities.update(
        {person.reference.value: person, wrong_target.reference.value: wrong_target}
    )

    with pytest.raises(ValueError, match="Invalid target"):
        service.materialise(claim.reference)


def test_explicit_relationship_reference_must_exist(monkeypatch):
    identities = {}
    proposal = _relationship(RelationshipType.BORN_IN, identities)
    claim = Claim(
        proposition=RelationshipProposition(
            proposal.get_source().reference,
            proposal.get_target().reference,
            RelationshipType.BORN_IN,
            None,
            RelationshipReference(uuid4()),
        ),
        status=ClaimStatus.ACCEPTED,
    )
    service, _, _, _ = _make_service(claim, monkeypatch=monkeypatch)
    service._identity_resolver.identities.update(identities)

    with pytest.raises(RepositoryNotFoundError, match="does not exist"):
        service.materialise(claim.reference)


def test_unknown_claim_reference_is_reported(monkeypatch):
    service, _, _, _ = _make_service(None, monkeypatch=monkeypatch)

    with pytest.raises(RepositoryNotFoundError, match="does not exist"):
        service.materialise(uuid4())


def test_materialisation_request_requires_boolean_override(monkeypatch):
    claim = Claim(
        proposition=IdentityProposalProposition(IdentityKind.PERSON, "Boolean test"),
        status=ClaimStatus.ACCEPTED,
    )
    service, _, _, _ = _make_service(claim, monkeypatch=monkeypatch)

    with pytest.raises(TypeError, match="must be a boolean"):
        service.materialise(claim.reference, allow_possible_duplicate="true")


def test_all_materialisation_domain_records_enforce_target_and_override_invariants():
    from domain_models.Provenance.materialisation import ClaimMaterialisation

    with pytest.raises(ValueError, match="linked materialisations require an exact match"):
        ClaimMaterialisation(
            claim_reference=uuid4(),
            target_kind=MaterialisationTargetKind.IDENTITY,
            target_reference=uuid4(),
            outcome=MaterialisationOutcome.NO_MATCH,
            action=MaterialisationAction.LINKED,
        )

    with pytest.raises(ValueError, match="override_applied requires"):
        ClaimMaterialisation(
            claim_reference=uuid4(),
            target_kind=MaterialisationTargetKind.IDENTITY,
            target_reference=uuid4(),
            outcome=MaterialisationOutcome.NO_MATCH,
            action=MaterialisationAction.CREATED,
            override_applied=True,
        )
