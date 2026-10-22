from datetime import date
from decimal import Decimal

from domain_models.relationship_models.relationship_types.relationship_types import (
    RelationshipType,
)
from API.v1.DTOs.relationship_properties import (
    serialize_relationship_properties,
)
from domain_models.relationship_models.relationship_properties.properties_merge import InvestmentProperties
from domain_models.Identity_model.Organisation_model.classification_specific_domain_model.investor.investor import InvestmentStage

def test_serialize_investment_properties():

    investment_properties = InvestmentProperties(
        investment_amount= Decimal(20000.00),
        currency="USD",
        investment_date=date(2026, 9, 12),
        funding_round= InvestmentStage.SEED,
        pre_money_valuation= None,
        post_money_valuation= None,
        equity_percentage= None,
        is_lead_investor=True
    )

    result = serialize_relationship_properties(
        RelationshipType.INVESTED_IN,
        investment_properties,
    )


    assert isinstance(result, dict)

    if investment_properties.investment_amount is not None:
        assert result["investment_amount"] == str(
            investment_properties.investment_amount
        )

    if investment_properties.investment_date is not None:
        assert result["investment_date"] == (
            investment_properties.investment_date.isoformat()
        )
