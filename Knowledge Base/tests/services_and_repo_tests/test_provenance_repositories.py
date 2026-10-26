from datetime import date, datetime, timedelta, timezone
from decimal import Decimal
from uuid import uuid4

import pytest

from domain_models.Identity_model.Place_model.place import PlaceKind
from domain_models.Identity_model.identity import IdentityKind, IdentityReference
from domain_models.Provenance.claim import Claim, ClaimStatus
from domain_models.Provenance.propositions import (
    IdentityAttributeProposition,
    IdentityProposalProposition,
    RelationshipPropertyProposition,
    RelationshipProposition,
)
from domain_models.Provenance.source import Source, SourceReference, SourceType
from domain_models.Provenance.verification_assessment import (
    AssessmentOutcome,
    VerificationAssessment,
)
from domain_models.relationship_models.relationship import Relationship, RelationshipReference
from domain_models.relationship_models.relationship_properties.properties_merge import ResidenceProperties
from domain_models.relationship_models.relationship_types.relationship_types import RelationshipType
from repositories.claim_repository import ClaimRepository
from repositories.source_repository import SourceRepository
from repositories.utils.errors import (
    RepositoryConflictError,
    RepositoryIntegrityError,
    RepositoryReferenceError,
)
from application.persistence.typed_value_codec import ValueCodecError
from repositories.verification_assessment_repository import VerificationAssessmentRepository


@pytest.fixture
def provenance_records(database_manager, service_environment):
    records = {"sources": [], "claims": [], "assessments": []}
    yield records
    source_ids = records["sources"]
    claim_ids = records["claims"]
    assessment_ids = records["assessments"]
    if source_ids or claim_ids or assessment_ids:
        with database_manager.transaction() as connection:
            with connection.cursor() as cursor:
                if assessment_ids:
                    marks = ", ".join(["%s"] * len(assessment_ids))
                    cursor.execute(
                        f"DELETE FROM verification_assessments WHERE assessment_id IN ({marks})",
                        assessment_ids,
                    )
                if claim_ids:
                    marks = ", ".join(["%s"] * len(claim_ids))
                    cursor.execute(f"DELETE FROM claim_sources WHERE claim_id IN ({marks})", claim_ids)
                    for table in (
                        "identity_attribute_propositions",
                        "relationship_propositions",
                        "relationship_property_propositions",
                        "identity_proposal_propositions",
                    ):
                        cursor.execute(f"DELETE FROM {table} WHERE claim_id IN ({marks})", claim_ids)
                    cursor.execute(f"DELETE FROM claim_propositions WHERE claim_id IN ({marks})", claim_ids)
                    cursor.execute(f"DELETE FROM claims WHERE claim_id IN ({marks})", claim_ids)
                if source_ids:
                    marks = ", ".join(["%s"] * len(source_ids))
                    cursor.execute(f"DELETE FROM sources WHERE source_id IN ({marks})", source_ids)


def _track_claim(records, claim):
    records["claims"].append(claim.reference.bytes)


def test_source_repository_round_trip_without_url_and_duplicate_id(
    database_manager, provenance_records
):
    repository = SourceRepository()
    source = Source(
        title="Source without a public URL",
        source_type=SourceType.REPORT,
        reference=SourceReference(),
        publication_date=date(2024, 8, 9),
        retrieved_at=datetime(2025, 1, 2, 3, 4, tzinfo=timezone(timedelta(hours=3))),
    )
    provenance_records["sources"].append(source.reference.value.bytes)
    with database_manager.transaction() as connection:
        repository.create(source, connection=connection)
    with database_manager.connection() as connection:
        actual = repository.get_by_reference(source.reference, connection=connection)
        assert not repository.exists(uuid4(), connection=connection)
    assert actual == source
    assert actual.url is None
    assert actual.retrieved_at.utcoffset() == timedelta(0)

    with database_manager.transaction() as connection:
        with pytest.raises(RepositoryConflictError):
            repository.create(source, connection=connection)


def test_claim_repository_round_trips_all_proposition_variants(
    database_manager, service_environment, provenance_records
):
    person = service_environment["person"].create(
        canonical_name=f"Provenance person {uuid4().hex}"
    ).entity
    place = service_environment["place"].create(
        canonical_name=f"Provenance place {uuid4().hex}", place_kind=PlaceKind.CITY
    ).entity
    service_environment["track_identity"](person)
    service_environment["track_identity"](place)
    existing_relation = service_environment["relationship"].create(
        source=person,
        target=place,
        relationship_type=RelationshipType.LIVES_IN,
        properties=ResidenceProperties(residence_type="primary"),
    ).entity
    service_environment["track_relationship"](existing_relation)
    repository = ClaimRepository()

    propositions = [
        IdentityAttributeProposition(person.reference, "biography", {"years": [1, 2]}),
        RelationshipProposition(
            person.reference,
            place.reference,
            RelationshipType.LIVES_IN,
            ResidenceProperties(start_date=date(2020, 1, 1)),
        ),
        RelationshipPropertyProposition(
            existing_relation.get_reference(), "residence_type", "primary"
        ),
        IdentityProposalProposition(
            person.kind,
            f"Proposed person {uuid4().hex}",
            {"Proposed alias"},
            {"net_worth": Decimal("123456789.001")},
        ),
    ]

    for proposition in propositions:
        claim = Claim(
            proposition=proposition,
            research_notes="Repository round trip",
            status=ClaimStatus.PENDING_REVIEW,
        )
        _track_claim(provenance_records, claim)
        with database_manager.transaction() as connection:
            repository.create(claim, connection=connection)
        with database_manager.connection() as connection:
            actual = repository.get_by_reference(claim.reference, connection=connection)
        assert type(actual.proposition) is type(proposition)
        assert actual.reference == claim.reference
        assert actual.status is claim.status
        assert actual.research_notes == claim.research_notes
        assert actual.proposition == proposition
        with database_manager.connection() as connection:
            with connection.cursor() as cursor:
                cursor.execute(
                    """SELECT
                       (SELECT COUNT(*) FROM identity_attribute_propositions WHERE claim_id = %s) +
                       (SELECT COUNT(*) FROM relationship_propositions WHERE claim_id = %s) +
                       (SELECT COUNT(*) FROM relationship_property_propositions WHERE claim_id = %s) +
                       (SELECT COUNT(*) FROM identity_proposal_propositions WHERE claim_id = %s) AS subtype_count""",
                    (claim.reference.bytes,) * 4,
                )
                assert cursor.fetchone()["subtype_count"] == 1


def test_claim_relationship_existing_reference_and_source_links(
    database_manager, service_environment, provenance_records
):
    person = service_environment["person"].create(
        canonical_name=f"Provenance link person {uuid4().hex}"
    ).entity
    place = service_environment["place"].create(
        canonical_name=f"Provenance link place {uuid4().hex}", place_kind=PlaceKind.CITY
    ).entity
    service_environment["track_identity"](person)
    service_environment["track_identity"](place)
    relation = Relationship(
        source=person,
        target=place,
        type=RelationshipType.LIVES_IN,
        properties=ResidenceProperties(residence_type="primary"),
    )
    with database_manager.transaction() as connection:
        service_environment["relationship"]._relationship_repository.save(
            relation, connection=connection
        )
    service_environment["track_relationship"](relation)

    source = Source(title="Evidence", source_type=SourceType.NEWS_ARTICLE)
    provenance_records["sources"].append(source.reference.value.bytes)
    with database_manager.transaction() as connection:
        SourceRepository().create(source, connection=connection)

    proposition = RelationshipProposition(
        person.reference,
        place.reference,
        RelationshipType.LIVES_IN,
        ResidenceProperties(residence_type="primary"),
        relation.get_reference(),
    )
    claim = Claim(proposition=proposition, source_references={source.reference})
    _track_claim(provenance_records, claim)
    repository = ClaimRepository()
    with database_manager.transaction() as connection:
        repository.create(claim, connection=connection)
        repository.add_source(claim.reference, source.reference, connection=connection)
    with database_manager.connection() as connection:
        actual = repository.get_by_reference(claim.reference, connection=connection)
    with database_manager.transaction() as connection:
        repository.remove_source(claim.reference, source.reference, connection=connection)
        repository.remove_source(claim.reference, source.reference, connection=connection)
    assert actual.proposition.existing_relationship_reference == relation.get_reference()
    assert actual.source_references == frozenset({source.reference})
    with database_manager.connection() as connection:
        assert repository.get_by_reference(claim.reference, connection=connection).source_references == frozenset()
    with database_manager.transaction() as connection:
        repository.add_source(claim.reference, source.reference, connection=connection)
        repository.add_source(claim.reference, source.reference, connection=connection)


def test_claim_create_rolls_back_when_source_reference_is_missing(
    database_manager, provenance_records
):
    claim = Claim(
        proposition=IdentityProposalProposition(
            IdentityKind.PERSON,
            f"Rollback proposal {uuid4().hex}",
        ),
        source_references={SourceReference()},
    )
    repository = ClaimRepository()
    with database_manager.transaction() as connection:
        with pytest.raises(RepositoryReferenceError):
            repository.create(claim, connection=connection)
        assert repository.get_by_reference(claim.reference, connection=connection) is None


def test_claim_create_rolls_back_when_typed_value_cannot_be_encoded(
    database_manager, provenance_records
):
    claim = Claim(
        proposition=IdentityAttributeProposition(
            IdentityReference(), "opaque", object()
        )
    )
    _track_claim(provenance_records, claim)
    with database_manager.transaction() as connection:
        with pytest.raises(ValueCodecError):
            ClaimRepository().create(claim, connection=connection)
        assert ClaimRepository().get_by_reference(claim.reference, connection=connection) is None


def test_claim_rejects_missing_canonical_identity_reference(
    database_manager, provenance_records
):
    claim = Claim(
        proposition=IdentityAttributeProposition(IdentityReference(), "name", "x")
    )
    _track_claim(provenance_records, claim)
    with database_manager.transaction() as connection:
        with pytest.raises(RepositoryReferenceError):
            ClaimRepository().create(claim, connection=connection)
        assert ClaimRepository().get_by_reference(claim.reference, connection=connection) is None


def test_claim_reader_rejects_missing_subtype(database_manager, provenance_records):
    claim = Claim(
        proposition=IdentityProposalProposition(
            IdentityKind.PERSON,
            f"Corrupt claim {uuid4().hex}",
        )
    )
    _track_claim(provenance_records, claim)
    with database_manager.transaction() as connection:
        with connection.cursor() as cursor:
            cursor.execute("INSERT INTO claims (claim_id, status, research_notes, created_at) VALUES (%s, %s, %s, %s)",
                           (claim.reference.bytes, claim.status.value, claim.research_notes, claim.created_at.replace(tzinfo=None)))
            cursor.execute("INSERT INTO claim_propositions (claim_id, proposition_type) VALUES (%s, %s)",
                           (claim.reference.bytes, "identity_proposal"))
    with database_manager.connection() as connection:
        with pytest.raises(RepositoryIntegrityError, match="subtype row is missing"):
            ClaimRepository().get_by_reference(claim.reference, connection=connection)


def test_claim_reader_rejects_unknown_discriminator(database_manager, provenance_records):
    claim = Claim(
        proposition=IdentityProposalProposition(
            IdentityKind.PERSON, f"Unknown discriminator {uuid4().hex}"
        )
    )
    _track_claim(provenance_records, claim)
    with database_manager.transaction() as connection:
        with connection.cursor() as cursor:
            cursor.execute(
                "INSERT INTO claims (claim_id, status, research_notes, created_at) VALUES (%s, %s, %s, %s)",
                (claim.reference.bytes, claim.status.value, claim.research_notes, claim.created_at.replace(tzinfo=None)),
            )
            cursor.execute(
                "INSERT INTO claim_propositions (claim_id, proposition_type) VALUES (%s, %s)",
                (claim.reference.bytes, "unknown_type"),
            )
    with database_manager.connection() as connection:
        with pytest.raises(RepositoryIntegrityError, match="Unknown proposition discriminator"):
            ClaimRepository().get_by_reference(claim.reference, connection=connection)


def test_claim_update_uses_domain_transition_rules(database_manager, provenance_records):
    claim = Claim(
        proposition=IdentityProposalProposition(
            IdentityKind.PERSON, f"Updatable claim {uuid4().hex}"
        )
    )
    _track_claim(provenance_records, claim)
    repository = ClaimRepository()
    with database_manager.transaction() as connection:
        repository.create(claim, connection=connection)
    claim.transition_to(ClaimStatus.PENDING_REVIEW)
    claim.update_research_notes("Reviewed once")
    with database_manager.transaction() as connection:
        repository.update(claim, connection=connection)
    with database_manager.connection() as connection:
        stored = repository.get_by_reference(claim.reference, connection=connection)
    assert stored.status is ClaimStatus.PENDING_REVIEW
    assert stored.research_notes == "Reviewed once"

    invalid_transition = Claim(
        proposition=claim.proposition,
        reference=claim.reference,
        status=ClaimStatus.DRAFT,
    )
    with database_manager.transaction() as connection:
        with pytest.raises(ValueError, match="Invalid claim status transition"):
            repository.update(invalid_transition, connection=connection)


def test_assessment_repository_preserves_append_only_history(
    database_manager, provenance_records
):
    claim = Claim(
        proposition=IdentityProposalProposition(
            IdentityKind.PERSON,
            f"Assessed person {uuid4().hex}",
        )
    )
    _track_claim(provenance_records, claim)
    claim_repository = ClaimRepository()
    with database_manager.transaction() as connection:
        claim_repository.create(claim, connection=connection)
    repo = VerificationAssessmentRepository()
    earlier = VerificationAssessment(
        claim.reference, AssessmentOutcome.REQUEST_MORE_RESEARCH,
        "Need a second source", "reviewer", assessed_at=datetime(2025, 1, 1, tzinfo=timezone.utc),
    )
    later = VerificationAssessment(
        claim.reference, AssessmentOutcome.ACCEPT,
        "Corroborated", "reviewer", assessed_at=datetime(2025, 1, 2, tzinfo=timezone.utc),
    )
    provenance_records["assessments"].extend([earlier.reference.bytes, later.reference.bytes])
    with database_manager.transaction() as connection:
        repo.create(later, connection=connection)
        repo.create(earlier, connection=connection)
    with database_manager.connection() as connection:
        assert repo.get_by_reference(earlier.reference, connection=connection) == earlier
        assert repo.get_by_claim_reference(claim.reference, connection=connection) == [earlier, later]
    with database_manager.transaction() as connection:
        with pytest.raises(RepositoryConflictError):
            repo.create(earlier, connection=connection)


def test_assessment_repository_rejects_missing_claim(database_manager):
    assessment = VerificationAssessment(
        uuid4(), AssessmentOutcome.REJECT, "No claim exists", "reviewer"
    )
    with database_manager.transaction() as connection:
        with pytest.raises(RepositoryReferenceError):
            VerificationAssessmentRepository().create(assessment, connection=connection)
