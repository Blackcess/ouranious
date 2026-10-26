"""Service-level integration coverage for resolution against MySQL.

These tests write uniquely named fixture rows to the configured development
database and remove those rows after the module-scoped fixture completes.
"""

from dataclasses import fields, is_dataclass
from datetime import date
from decimal import Decimal
from uuid import uuid4

import pytest
from concurrent.futures import ThreadPoolExecutor

from application.resolution.identity.contracts import (
    CandidateMatchKind,
    IdentityResolutionRequest,
    ResolutionOutcome,
)
from application.resolution.relationship.contracts import (
    RelationshipResolutionOutcome,
    RelationshipResolutionRequest,
)
from application.resolution.relationship.canonicalization import (
    canonicalize_relationship_properties,
    compare_canonical_properties,
)
from application.services.identity_resolution_service import IdentityResolutionService
from application.services.identity_resolver import IdentityResolver
from application.services.identity_relationship_service import RelationshipService
from application.services.relationship_resolution_service import (
    RelationshipResolutionService,
)
from application.services.person_service import PersonService
from domain_models.Identity_model.identity import (
    IdentityKind,
    IdentityRepresentations,
)
from domain_models.Identity_model.Industry_model.industry import Industry
from domain_models.Identity_model.Organisation_model.classification_specific_domain_model.accelerator.accelerator import (
    Accelerator,
)
from domain_models.Identity_model.Organisation_model.classification_specific_domain_model.accelerator.accelerator_programme import (
    AcceleratorProgramme,
    InvestmentTerms,
)
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
from domain_models.Identity_model.Organisation_model.organisation_classification import (
    OrganisationClassification,
)
from domain_models.Identity_model.Person_model.person import Person
from domain_models.Identity_model.Place_model.place import Place, PlaceKind
from domain_models.Identity_model.Product_model.product import Product
from domain_models.Identity_model.Technology_model.technology import Technology
from domain_models.relationship_models.relationship import Relationship
from domain_models.relationship_models.relationship_properties.properties.acquisitionProperties import (
    AcquisitionProperties,
    AcquisitionType,
)
from domain_models.relationship_models.relationship_properties.properties.partnershipProperties import (
    PartnershipProperties,
    PartnershipStatus,
)
from domain_models.relationship_models.relationship_types.relationship_type_specification import (
    specification_registry,
)
from domain_models.relationship_models.relationship_types.relationship_types import (
    RelationshipType,
)
from infrastructure.database.connection import DatabaseManager
from repositories.industry_repository import IndustryRepository
from repositories.organisation_repository import OrganisationRepository
from repositories.person_repository import PersonRepository
from repositories.place_repository import PlaceRepository
from repositories.product_repository import ProductRepository
from repositories.relationship_repository import RelationshipRepository
from repositories.technology_repository import TechnologyRepository
from utils.representations import Duration, Money


_IDENTITY_REPOSITORY_TYPES = {
    IdentityKind.PERSON: PersonRepository,
    IdentityKind.ORGANISATION: OrganisationRepository,
    IdentityKind.PLACE: PlaceRepository,
    IdentityKind.INDUSTRY: IndustryRepository,
    IdentityKind.PRODUCT: ProductRepository,
    IdentityKind.TECHNOLOGY: TechnologyRepository,
}

_RELATIONSHIP_PROPERTY_TABLES = (
    "relationship_investment_properties",
    "relationship_acquisition_properties",
    "relationship_founder_properties",
    "relationship_headquarters_properties",
    "relationship_industry_participation_properties",
    "relationship_leadership_properties",
    "relationship_market_presence_properties",
    "relationship_ownership_properties",
    "relationship_partnership_properties",
    "relationship_product_availability_properties",
    "relationship_product_development_properties",
    "relationship_product_offering_properties",
    "relationship_product_technology_properties",
    "relationship_residence_properties",
    "relationship_technology_adoption_properties",
)


def _representations(token: str, *, alias: str | None = None):
    return IdentityRepresentations(
        canonical_name=token,
        aliases={alias} if alias else set(),
    )


def _identity_for_kind(kind: IdentityKind, token: str, *, alias: str):
    representations = _representations(token, alias=alias)
    if kind is IdentityKind.PERSON:
        return Person(representations=representations)
    if kind is IdentityKind.ORGANISATION:
        identity = Organisation(
            representations=representations,
            classifications={OrganisationClassification.STARTUP},
        )
        identity.add_classification_model(
            OrganisationClassification.STARTUP,
            Startup(2020, StartupStages.SEED, StartupBusinessModels.B2B),
        )
        return identity
    if kind is IdentityKind.PLACE:
        return Place(representations=representations, place_kind=PlaceKind.CITY)
    if kind is IdentityKind.INDUSTRY:
        return Industry(representations=representations)
    if kind is IdentityKind.PRODUCT:
        return Product(representations=representations)
    if kind is IdentityKind.TECHNOLOGY:
        return Technology(representations=representations)
    raise AssertionError(f"Missing identity factory for {kind}")


def _organisation_for_classification(
    token: str,
    classification: OrganisationClassification,
):
    identity = Organisation(
        representations=_representations(token),
        classifications={classification},
    )
    if classification is OrganisationClassification.STARTUP:
        model = Startup(2021, StartupStages.SEED, StartupBusinessModels.B2B)
    elif classification is OrganisationClassification.INVESTOR:
        model = Investor(InvestmentTypes.VENTURE_CAPITAL, InvestmentStage.SEED)
    elif classification is OrganisationClassification.ACCELERATOR:
        model = Accelerator()
        model.programmes.append(
            AcceleratorProgramme(
                name=f"Test programme {uuid4().hex}",
                # OrganisationRepository currently persists the unit as text.
                duration=Duration(Decimal("12"), "months"),
                investment_terms=InvestmentTerms(
                    money=Money(Decimal("0"), "USD"),
                    equity_percentage=Decimal("0"),
                ),
            )
        )
    else:
        # Incubator is explicitly modelled as classification-only at present.
        model = None
    if model is not None:
        identity.add_classification_model(classification, model)
    return identity


def _empty_properties(properties_type):
    if properties_type is None:
        return None
    assert is_dataclass(properties_type), (
        f"Expected dataclass property model, got {properties_type!r}"
    )
    required = [
        field.name
        for field in fields(properties_type)
        if field.default.__class__.__name__ == "_MISSING_TYPE"
        and field.default_factory.__class__.__name__ == "_MISSING_TYPE"
    ]
    assert not required, (
        f"{properties_type.__name__} has required fields: {required}; "
        "update this test's valid property factory"
    )
    return properties_type()


@pytest.fixture(scope="module")
def resolution_database():
    database_manager = DatabaseManager()
    repositories = {
        kind: repository_type()
        for kind, repository_type in _IDENTITY_REPOSITORY_TYPES.items()
    }
    relationship_repository = RelationshipRepository(
        person_repository=repositories[IdentityKind.PERSON],
        organisation_repository=repositories[IdentityKind.ORGANISATION],
        place_repository=repositories[IdentityKind.PLACE],
        industry_repository=repositories[IdentityKind.INDUSTRY],
        product_repository=repositories[IdentityKind.PRODUCT],
        technology_repository=repositories[IdentityKind.TECHNOLOGY],
    )
    identity_service = IdentityResolutionService(
        person_repository=repositories[IdentityKind.PERSON],
        organisation_repository=repositories[IdentityKind.ORGANISATION],
        place_repository=repositories[IdentityKind.PLACE],
        industry_repository=repositories[IdentityKind.INDUSTRY],
        product_repository=repositories[IdentityKind.PRODUCT],
        technology_repository=repositories[IdentityKind.TECHNOLOGY],
    )

    # The database records are unique to this fixture run. Relationships use
    # the existing registry to derive valid endpoint kinds and property types.
    run_id = uuid4().hex
    identities = {
        kind: _identity_for_kind(
            kind,
            f"Resolution Test {run_id} {kind.value}",
            alias=f"Resolution Alias {run_id} {kind.value}",
        )
        for kind in IdentityKind
    }
    classification_identities = {
        classification: _organisation_for_classification(
            f"Resolution Test {run_id} organisation {classification.value}",
            classification,
        )
        for classification in OrganisationClassification
    }
    identities_to_save = [*identities.values(), *classification_identities.values()]
    saved_relationships = []

    with database_manager.transaction() as connection:
        for identity in identities_to_save:
            repositories[identity.kind].save(identity, connection=connection)

        for relationship_type in RelationshipType:
            specification = specification_registry[relationship_type]
            source_kind = specification.allowed_source
            target_kind = specification.allowed_target
            relationship = Relationship(
                source=identities[source_kind],
                target=identities[target_kind],
                type=relationship_type,
                properties=_empty_properties(specification.properties_type),
            )
            relationship_repository.save(relationship, connection=connection)
            saved_relationships.append(relationship)

        # A separate acquisition with populated event fields exercises temporal
        # equivalence and ensures a different date remains a distinct event.
        historical_event = Relationship(
            source=classification_identities[OrganisationClassification.STARTUP],
            target=classification_identities[OrganisationClassification.INVESTOR],
            type=RelationshipType.ACQUIRED,
            properties=AcquisitionProperties(
                acquisition_date=date(2020, 1, 2),
                acquisition_amount=Decimal("100.0"),
                currency="USD",
                acquisition_type=AcquisitionType.FULL_ACQUISITION,
            ),
        )
        relationship_repository.save(historical_event, connection=connection)
        saved_relationships.append(historical_event)

    relationship_service = RelationshipResolutionService(
        relationship_repository=relationship_repository,
        identity_resolver=IdentityResolver(
            person_repository=repositories[IdentityKind.PERSON],
            organisation_repository=repositories[IdentityKind.ORGANISATION],
            place_repository=repositories[IdentityKind.PLACE],
            industry_repository=repositories[IdentityKind.INDUSTRY],
            product_repository=repositories[IdentityKind.PRODUCT],
            technology_repository=repositories[IdentityKind.TECHNOLOGY],
            database_manager=database_manager,
        ),
        require_persisted_endpoints=True,
    )
    person_create_service = PersonService(
        person_repository=repositories[IdentityKind.PERSON],
        database_manager=database_manager,
        identity_resolution_service=identity_service,
    )
    relationship_create_service = RelationshipService(
        relationship_repository=relationship_repository,
        database_manager=database_manager,
        relationship_resolution_service=relationship_service,
    )

    yield {
        "database_manager": database_manager,
        "repositories": repositories,
        "relationship_repository": relationship_repository,
        "identity_service": identity_service,
        "person_create_service": person_create_service,
        "relationship_service": relationship_service,
        "relationship_create_service": relationship_create_service,
        "identities": identities,
        "classification_identities": classification_identities,
        "relationships": tuple(saved_relationships),
        "relationships_to_save": saved_relationships,
        "identities_to_save": identities_to_save,
    }
    relationship_ids = [
        relationship.get_reference().value.bytes
        for relationship in saved_relationships
    ]
    identity_ids = [identity.reference.value.bytes for identity in identities_to_save]
    relationship_marks = ", ".join(["%s"] * len(relationship_ids))
    identity_marks = ", ".join(["%s"] * len(identity_ids))

    # Delete only rows created by this fixture, in child-before-parent order.
    with database_manager.transaction() as connection:
        with connection.cursor() as cursor:
            if relationship_ids:
                for table in _RELATIONSHIP_PROPERTY_TABLES:
                    cursor.execute(
                        f"DELETE FROM {table} "
                        f"WHERE relationship_id IN ({relationship_marks})",
                        relationship_ids,
                    )
                cursor.execute(
                    f"DELETE FROM relationships "
                    f"WHERE relationship_id IN ({relationship_marks})",
                    relationship_ids,
                )

            if identity_ids:
                cursor.execute(
                    f"DELETE FROM startup_models "
                    f"WHERE organisation_id IN ({identity_marks})",
                    identity_ids,
                )
                cursor.execute(
                    f"DELETE FROM investor_models "
                    f"WHERE organisation_id IN ({identity_marks})",
                    identity_ids,
                )
                cursor.execute(
                    f"DELETE FROM accelerator_programmes "
                    f"WHERE accelerator_id IN ({identity_marks})",
                    identity_ids,
                )
                cursor.execute(
                    f"DELETE FROM organisation_classifications "
                    f"WHERE organisation_id IN ({identity_marks})",
                    identity_ids,
                )
                cursor.execute(
                    f"DELETE FROM organisations "
                    f"WHERE identity_id IN ({identity_marks})",
                    identity_ids,
                )
                cursor.execute(
                    f"DELETE FROM places WHERE identity_id IN ({identity_marks})",
                    identity_ids,
                )
                cursor.execute(
                    f"DELETE FROM identity_aliases "
                    f"WHERE identity_id IN ({identity_marks})",
                    identity_ids,
                )
                cursor.execute(
                    f"DELETE FROM identities WHERE identity_id IN ({identity_marks})",
                    identity_ids,
                )


def _resolve_identity(resolution_database, request):
    with resolution_database["database_manager"].connection() as connection:
        return resolution_database["identity_service"].resolve(
            request,
            connection=connection,
        )


def _resolve_relationship(resolution_database, request):
    with resolution_database["database_manager"].connection() as connection:
        return resolution_database["relationship_service"].resolve(
            request,
            connection=connection,
        )


def test_identity_create_result_covers_create_exact_block_and_override(
    resolution_database,
):
    service = resolution_database["person_create_service"]
    canonical_name = f"Create outcome {uuid4().hex}"
    alias = f"Shared create alias {uuid4().hex}"

    created = service.create(canonical_name=canonical_name, aliases={alias})
    assert created.action.value == "created"
    assert created.outcome is ResolutionOutcome.NO_MATCH
    resolution_database["identities_to_save"].append(created.entity)

    exact = service.create(canonical_name=canonical_name, aliases={alias})
    assert exact.action.value == "returned_existing"
    assert exact.outcome is ResolutionOutcome.EXACT_MATCH
    assert exact.entity.reference == created.entity.reference

    possible_name = f"Different identity {uuid4().hex}"
    blocked = service.create(
        canonical_name=possible_name,
        aliases={alias},
    )
    assert blocked.action.value == "blocked"
    assert blocked.outcome is ResolutionOutcome.POSSIBLE_DUPLICATE
    assert blocked.entity is None

    overridden = service.create(
        canonical_name=possible_name,
        aliases={alias},
        allow_possible_duplicate=True,
    )
    assert overridden.action.value == "created"
    assert overridden.outcome is ResolutionOutcome.POSSIBLE_DUPLICATE
    assert overridden.override_applied is True
    resolution_database["identities_to_save"].append(overridden.entity)


def test_concurrent_identity_creates_serialize_on_resolution_key(
    resolution_database,
):
    service = resolution_database["person_create_service"]
    canonical_name = f"Concurrent create {uuid4().hex}"

    with ThreadPoolExecutor(max_workers=2) as executor:
        results = list(
            executor.map(
                lambda _: service.create(canonical_name=canonical_name),
                range(2),
            )
        )

    actions = sorted(result.action.value for result in results)
    assert actions == ["created", "returned_existing"]
    assert results[0].entity.reference == results[1].entity.reference
    created_entity = next(
        result.entity for result in results if result.action.value == "created"
    )
    resolution_database["identities_to_save"].append(created_entity)


def test_relationship_create_result_blocks_possible_and_allows_override(
    resolution_database,
):
    service = resolution_database["relationship_create_service"]
    source = resolution_database["classification_identities"][
        OrganisationClassification.STARTUP
    ]
    target = resolution_database["classification_identities"][
        OrganisationClassification.INVESTOR
    ]

    created = service.create(
        source=source,
        target=target,
        relationship_type=RelationshipType.PARTNERED_WITH,
        properties=PartnershipProperties(),
    )
    assert created.action.value == "created"
    assert created.outcome is RelationshipResolutionOutcome.NO_MATCH
    resolution_database["relationships_to_save"].append(created.entity)

    exact = service.create(
        source=source,
        target=target,
        relationship_type=RelationshipType.PARTNERED_WITH,
        properties=PartnershipProperties(),
    )
    assert exact.action.value == "returned_existing"
    assert exact.outcome is RelationshipResolutionOutcome.EXACT_MATCH
    assert exact.entity.get_reference() == created.entity.get_reference()

    possible = PartnershipProperties(partnership_status=PartnershipStatus.ACTIVE)
    blocked = service.create(
        source=source,
        target=target,
        relationship_type=RelationshipType.PARTNERED_WITH,
        properties=possible,
    )
    assert blocked.action.value == "blocked"
    assert blocked.outcome is RelationshipResolutionOutcome.POSSIBLE_DUPLICATE
    assert blocked.entity is None

    overridden = service.create(
        source=source,
        target=target,
        relationship_type=RelationshipType.PARTNERED_WITH,
        properties=possible,
        allow_possible_duplicate=True,
    )
    assert overridden.action.value == "created"
    assert overridden.override_applied is True
    resolution_database["relationships_to_save"].append(overridden.entity)


def test_concurrent_relationship_creates_serialize_on_endpoint_pair(
    resolution_database,
):
    service = resolution_database["relationship_create_service"]
    source = resolution_database["classification_identities"][
        OrganisationClassification.STARTUP
    ]
    target = resolution_database["classification_identities"][
        OrganisationClassification.INVESTOR
    ]

    with ThreadPoolExecutor(max_workers=2) as executor:
        results = list(
            executor.map(
                lambda _: service.create(
                    source=source,
                    target=target,
                    relationship_type=RelationshipType.INVESTED_IN,
                    properties=_empty_properties(
                        specification_registry[RelationshipType.INVESTED_IN].properties_type
                    ),
                ),
                range(2),
            )
        )

    actions = sorted(result.action.value for result in results)
    assert actions == ["created", "returned_existing"]
    assert (
        results[0].entity.get_reference()
        == results[1].entity.get_reference()
    )
    created_entity = next(
        result.entity for result in results if result.action.value == "created"
    )
    resolution_database["relationships_to_save"].append(created_entity)


@pytest.mark.parametrize("identity_kind", list(IdentityKind))
def test_identity_candidate_retrieval_and_canonical_exact_match(
    resolution_database,
    identity_kind,
):
    identity = resolution_database["identities"][identity_kind]
    repository = resolution_database["repositories"][identity_kind]
    request_identity = _identity_for_kind(
        identity_kind,
        identity.representations.canonical_name,
        alias=f"Request Alias {uuid4().hex}",
    )

    with resolution_database["database_manager"].connection() as connection:
        page = repository.find_candidates(
            request_identity,
            exclude_reference=request_identity.reference,
            connection=connection,
            limit=10,
        )
    assert [candidate.reference for candidate in page.items] == [identity.reference]

    result = _resolve_identity(
        resolution_database,
        IdentityResolutionRequest(request_identity),
    )
    assert result.outcome is ResolutionOutcome.EXACT_MATCH
    assert result.matches[0].kind is CandidateMatchKind.EXACT_MATCH
    assert result.matches[0].identity.reference == identity.reference


@pytest.mark.parametrize("identity_kind", list(IdentityKind))
def test_identity_canonical_name_matching_persisted_alias_is_exact(
    resolution_database,
    identity_kind,
):
    candidate = resolution_database["identities"][identity_kind]
    alias = next(iter(candidate.representations.aliases))
    query = _identity_for_kind(
        identity_kind,
        alias,
        alias=f"Unrelated query alias {uuid4().hex}",
    )
    result = _resolve_identity(resolution_database, IdentityResolutionRequest(query))
    assert result.outcome is ResolutionOutcome.EXACT_MATCH
    assert result.matches[0].identity.reference == candidate.reference


@pytest.mark.parametrize("identity_kind", list(IdentityKind))
def test_identity_name_normalization_retrieves_and_matches_candidate(
    resolution_database,
    identity_kind,
):
    candidate = resolution_database["identities"][identity_kind]
    query = _identity_for_kind(
        identity_kind,
        f"  {candidate.representations.canonical_name.upper()}   ",
        alias=f"Normalized query alias {uuid4().hex}",
    )
    result = _resolve_identity(resolution_database, IdentityResolutionRequest(query))
    assert result.outcome is ResolutionOutcome.EXACT_MATCH
    assert result.matches[0].identity.reference == candidate.reference


@pytest.mark.parametrize("identity_kind", list(IdentityKind))
def test_identity_alias_to_alias_is_possible_duplicate(
    resolution_database,
    identity_kind,
):
    candidate = resolution_database["identities"][identity_kind]
    shared_alias = next(iter(candidate.representations.aliases))
    query = _identity_for_kind(
        identity_kind,
        f"Different canonical {uuid4().hex}",
        alias=shared_alias,
    )
    result = _resolve_identity(resolution_database, IdentityResolutionRequest(query))
    assert result.outcome is ResolutionOutcome.POSSIBLE_DUPLICATE
    assert result.matches[0].kind is CandidateMatchKind.POSSIBLE_DUPLICATE


@pytest.mark.parametrize("identity_kind", list(IdentityKind))
def test_identity_unrelated_name_is_no_match(resolution_database, identity_kind):
    query = _identity_for_kind(
        identity_kind,
        f"No candidate {uuid4().hex}",
        alias=f"No candidate alias {uuid4().hex}",
    )
    result = _resolve_identity(resolution_database, IdentityResolutionRequest(query))
    assert result.outcome is ResolutionOutcome.NO_MATCH


@pytest.mark.parametrize(
    "classification",
    list(OrganisationClassification),
)
def test_organisation_classification_specific_strategy_is_registered_and_used(
    resolution_database,
    classification,
):
    candidate = resolution_database["classification_identities"][classification]
    query = _organisation_for_classification(
        candidate.representations.canonical_name,
        classification,
    )
    result = _resolve_identity(resolution_database, IdentityResolutionRequest(query))
    assert result.outcome is ResolutionOutcome.EXACT_MATCH
    assert result.matches[0].identity.reference == candidate.reference


def test_place_kind_conflict_is_reported_as_possible_duplicate(
    resolution_database,
):
    candidate = resolution_database["identities"][IdentityKind.PLACE]
    query = Place(
        representations=_representations(candidate.representations.canonical_name),
        place_kind=PlaceKind.COUNTRY,
    )
    result = _resolve_identity(resolution_database, IdentityResolutionRequest(query))
    assert result.outcome is ResolutionOutcome.POSSIBLE_DUPLICATE
    assert result.matches[0].kind is CandidateMatchKind.POSSIBLE_DUPLICATE


def test_startup_attribute_conflict_is_reported_as_possible_duplicate(
    resolution_database,
):
    candidate = resolution_database["classification_identities"][
        OrganisationClassification.STARTUP
    ]
    query = Organisation(
        representations=_representations(candidate.representations.canonical_name),
        classifications={OrganisationClassification.STARTUP},
    )
    query.add_classification_model(
        OrganisationClassification.STARTUP,
        Startup(2021, StartupStages.SERIES_A, StartupBusinessModels.B2C),
    )
    result = _resolve_identity(resolution_database, IdentityResolutionRequest(query))
    assert result.outcome is ResolutionOutcome.POSSIBLE_DUPLICATE


@pytest.mark.parametrize(
    "relationship_type",
    list(RelationshipType),
    ids=lambda item: item.value,
)
def test_every_registered_relationship_type_resolves_persisted_duplicate(
    resolution_database,
    relationship_type,
):
    persisted = next(
        relationship
        for relationship in resolution_database["relationships"]
        if relationship.get_type() is relationship_type
    )
    candidate_page = resolution_database["relationship_repository"].find_candidates(
        source_reference=persisted.get_source().reference,
        target_reference=persisted.get_target().reference,
        relationship_type=relationship_type,
        connection=(
            connection := resolution_database["database_manager"].connect()
        ),
        limit=10,
    )
    try:
        assert any(
            candidate.get_reference() == persisted.get_reference()
            for candidate in candidate_page.items
        )
    finally:
        connection.close()

    equivalent = Relationship(
        source=persisted.get_source(),
        target=persisted.get_target(),
        type=relationship_type,
        properties=persisted.get_properties(),
    )
    result = _resolve_relationship(
        resolution_database,
        RelationshipResolutionRequest(equivalent),
    )
    assert result.outcome is RelationshipResolutionOutcome.EXACT_MATCH
    assert result.matches[0].relationship.get_reference() == persisted.get_reference()


def test_acquisition_equivalent_amounts_match_but_distinct_event_date_does_not(
    resolution_database,
):
    persisted = next(
        relationship
        for relationship in resolution_database["relationships"]
        if relationship.get_type() is RelationshipType.ACQUIRED
        and relationship.get_source().reference
        == resolution_database["classification_identities"][
            OrganisationClassification.STARTUP
        ].reference
    )
    props = AcquisitionProperties(
        acquisition_date=date(2020, 1, 2),
        acquisition_amount=Decimal("100.00"),
        currency="USD",
        acquisition_type=AcquisitionType.FULL_ACQUISITION,
    )
    same_event = Relationship(
        source=persisted.get_source(),
        target=persisted.get_target(),
        type=RelationshipType.ACQUIRED,
        properties=props,
    )
    exact = _resolve_relationship(
        resolution_database,
        RelationshipResolutionRequest(same_event),
    )
    assert exact.outcome is RelationshipResolutionOutcome.EXACT_MATCH

    other_event = Relationship(
        source=persisted.get_source(),
        target=persisted.get_target(),
        type=RelationshipType.ACQUIRED,
        properties=AcquisitionProperties(
            acquisition_date=date(2021, 1, 2),
            acquisition_amount=Decimal("100.00"),
            currency="USD",
            acquisition_type=AcquisitionType.FULL_ACQUISITION,
        ),
    )
    no_match = _resolve_relationship(
        resolution_database,
        RelationshipResolutionRequest(other_event),
    )
    assert no_match.outcome is RelationshipResolutionOutcome.NO_MATCH


def test_missing_optional_relationship_properties_are_possible_duplicates(
    resolution_database,
):
    persisted = next(
        relationship
        for relationship in resolution_database["relationships"]
        if relationship.get_type() is RelationshipType.ACQUIRED
        and relationship.get_source().reference
        == resolution_database["classification_identities"][
            OrganisationClassification.STARTUP
        ].reference
    )
    less_specific = Relationship(
        source=persisted.get_source(),
        target=persisted.get_target(),
        type=RelationshipType.ACQUIRED,
        properties=AcquisitionProperties(
            acquisition_date=date(2020, 1, 2),
            acquisition_type=AcquisitionType.FULL_ACQUISITION,
        ),
    )
    result = _resolve_relationship(
        resolution_database,
        RelationshipResolutionRequest(less_specific),
    )
    assert result.outcome is RelationshipResolutionOutcome.POSSIBLE_DUPLICATE


def test_canonical_property_comparison_normalizes_decimal_scale():
    source = Organisation(
        representations=_representations("Canonical source"),
        classifications={OrganisationClassification.INCUBATOR},
    )
    target = Organisation(
        representations=_representations("Canonical target"),
        classifications={OrganisationClassification.INCUBATOR},
    )
    relationship_a = Relationship(
        source=source,
        target=target,
        type=RelationshipType.ACQUIRED,
        properties=AcquisitionProperties(
            acquisition_date=date(2022, 3, 4),
            acquisition_amount=Decimal("42.0"),
            currency="USD",
        ),
    )
    relationship_b = Relationship(
        source=source,
        target=target,
        type=RelationshipType.ACQUIRED,
        properties=AcquisitionProperties(
            acquisition_date=date(2022, 3, 4),
            acquisition_amount=Decimal("42.00"),
            currency="USD",
        ),
    )
    canonical_a = canonicalize_relationship_properties(relationship_a)
    canonical_b = canonicalize_relationship_properties(relationship_b)
    assert canonical_a == canonical_b
    assert compare_canonical_properties(canonical_a, canonical_b) == (False, ())


def test_relationship_resolution_rejects_unpersisted_endpoints_when_enabled(
    resolution_database,
):
    from application.services.identity_resolver import IdentityResolver
    from application.services.relationship_resolution_service import (
        RelationshipEndpointNotFoundError,
    )

    database_manager = resolution_database["database_manager"]
    repositories = resolution_database["repositories"]
    identity_resolver = IdentityResolver(
        person_repository=repositories[IdentityKind.PERSON],
        organisation_repository=repositories[IdentityKind.ORGANISATION],
        place_repository=repositories[IdentityKind.PLACE],
        industry_repository=repositories[IdentityKind.INDUSTRY],
        product_repository=repositories[IdentityKind.PRODUCT],
        technology_repository=repositories[IdentityKind.TECHNOLOGY],
        database_manager=database_manager,
    )
    persisted = resolution_database["relationships"][0]
    unpersisted_source = _identity_for_kind(
        persisted.get_source().kind,
        f"Missing endpoint {uuid4().hex}",
        alias=f"Missing alias {uuid4().hex}",
    )
    relationship = Relationship(
        source=unpersisted_source,
        target=persisted.get_target(),
        type=persisted.get_type(),
        properties=persisted.get_properties(),
    )
    strict_service = RelationshipResolutionService(
        relationship_repository=resolution_database["relationship_repository"],
        identity_resolver=identity_resolver,
        require_persisted_endpoints=True,
    )

    with database_manager.connection() as connection:
        with pytest.raises(RelationshipEndpointNotFoundError):
            strict_service.resolve(
                RelationshipResolutionRequest(relationship),
                connection=connection,
            )


def test_resolution_contract_rejects_invalid_candidate_limits():
    identity = Person(representations=_representations("Contract probe"))
    with pytest.raises(ValueError):
        IdentityResolutionRequest(identity, candidate_limit=0)
