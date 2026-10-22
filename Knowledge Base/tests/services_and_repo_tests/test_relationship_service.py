

from datetime import date
from decimal import Decimal

from application.services.identity_relationship_service import RelationshipService
from application.services.organisation_service import OrganisationCreationService
from domain_models.Identity_model.Organisation_model.classification_specific_domain_model.investor.investor import InvestmentStage
from infrastructure.database.connection import DatabaseManager
from domain_models.relationship_models.relationship_properties.properties.investmentProperties import InvestmentProperties
from domain_models.relationship_models.relationship_types.relationship_types import RelationshipType
from repositories.organisation_repository import OrganisationRepository
from repositories.relationship_repository import RelationshipRepository
from domain_models.relationship_models.relationship import Relationship

def test_invested_in_relationship_service_round_trip():
    database_manager = DatabaseManager()

    organisation_repository = OrganisationRepository()
    relationship_repository = RelationshipRepository()

    organisation_service = OrganisationCreationService(
        organisation_repository=organisation_repository,
        database_manager=database_manager,
    )

    relationship_service = RelationshipService(
        relationship_repository=relationship_repository,
        database_manager=database_manager,
    )

    investor = organisation_service.create_incubator(
        canonical_name="Test Investment Fund",
        aliases={"TIF"},
    )

    startup = organisation_service.create_incubator(
        canonical_name="Test Startup",
        aliases={"TS"},
    )

    properties = InvestmentProperties(
        investment_amount=Decimal("250000.00"),
        currency="USD",
        investment_date=date(2026, 9, 15),
        funding_round=InvestmentStage.SEED,
        pre_money_valuation=Decimal("2000000.00"),
        post_money_valuation=Decimal("2250000.00"),
        equity_percentage=Decimal("11.111111"),
        is_lead_investor=True,
    )

    relationship = relationship_service.create(
        source=investor,
        target=startup,
        relationship_type=RelationshipType.INVESTED_IN,
        properties=properties,
    )

    retrieved = relationship_service.get_by_id(
        relationship.get_reference()
    )

    assert retrieved is not None
    assert retrieved.get_reference() == relationship.get_reference()
    assert retrieved.get_type() == RelationshipType.INVESTED_IN
    assert retrieved.get_source().reference == investor.reference
    assert retrieved.get_target().reference == startup.reference

    print("TEST PASSED: test_invested_in_relationship_service_round_trip")

test_invested_in_relationship_service_round_trip()