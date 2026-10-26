

from datetime import date
from decimal import Decimal

from domain_models.Identity_model.Organisation_model.classification_specific_domain_model.investor.investor import InvestmentStage
from domain_models.relationship_models.relationship_properties.properties.investmentProperties import InvestmentProperties
from domain_models.relationship_models.relationship_types.relationship_types import RelationshipType
from uuid import uuid4

def test_invested_in_relationship_service_round_trip(service_environment):
    organisation_service = service_environment["organisation"]
    relationship_service = service_environment["relationship"]

    investor_result = organisation_service.create_incubator(
        canonical_name=f"Test Investment Fund {uuid4().hex}",
        aliases={f"TIF {uuid4().hex}"},
    )
    investor = investor_result.entity
    service_environment["track_identity"](investor)

    startup_result = organisation_service.create_incubator(
        canonical_name=f"Test Startup {uuid4().hex}",
        aliases={f"TS {uuid4().hex}"},
    )
    startup = startup_result.entity
    service_environment["track_identity"](startup)

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

    relationship_result = relationship_service.create(
        source=investor,
        target=startup,
        relationship_type=RelationshipType.INVESTED_IN,
        properties=properties,
    )
    relationship = relationship_result.entity
    service_environment["track_relationship"](relationship)
    assert relationship_result.action.value == "created"

    retrieved = relationship_service.get_by_id(
        relationship.get_reference()
    )

    assert retrieved is not None
    assert retrieved.get_reference() == relationship.get_reference()
    assert retrieved.get_type() == RelationshipType.INVESTED_IN
    assert retrieved.get_source().reference == investor.reference
    assert retrieved.get_target().reference == startup.reference
