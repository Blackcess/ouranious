from datetime import date, datetime, timezone, timedelta
from decimal import Decimal
from uuid import uuid4

import pytest

from application.persistence.typed_value_codec import ValueCodecError, dumps, loads
from domain_models.Identity_model.identity import IdentityKind
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
from domain_models.relationship_models.relationship_properties.properties.founderProperties import FoundingStage
from domain_models.relationship_models.relationship_properties.properties.acquisitionProperties import AcquisitionType
from domain_models.relationship_models.relationship_properties.properties.headquartersProperties import HeadquartersFunction, HeadquartersLevel
from domain_models.relationship_models.relationship_properties.properties.marketPresenceProperties import OperatingStatus
from domain_models.relationship_models.relationship_properties.properties.ownershipProperties import OwnershipType
from domain_models.relationship_models.relationship_properties.properties.partnershipProperties import PartnershipStatus
from domain_models.relationship_models.relationship_properties.properties.productAvailabilityProperties import AvailabilityStatus
from domain_models.relationship_models.relationship_properties.properties.productDevelopmentProperties import DevelopmentStatus
from domain_models.relationship_models.relationship_properties.properties.productOfferingProperties import OfferingStatus
from utils.representations import Duration, DurationUnit, Money
from domain_models.Identity_model.Organisation_model.classification_specific_domain_model.accelerator.accelerator_programme import InvestmentTerms


@pytest.mark.parametrize(
    "value",
    [
        None,
        True,
        False,
        42,
        "value",
        2.5,
        Decimal("1234567890.0012300"),
        date(2025, 4, 3),
        datetime(2025, 4, 3, 12, 30, tzinfo=timezone(timedelta(hours=5, minutes=30))),
        uuid4(),
        Money(Decimal("999999999999.0001"), "USD"),
        Duration(Decimal("2.5"), DurationUnit.YEARS, date(2020, 1, 1), date(2022, 1, 1)),
        InvestmentTerms(Money(Decimal("250000.00"), "USD"), Decimal("12.50")),
        IdentityKind.PERSON,
        [1, "two", Decimal("3.00")],
        ("tuple", date(2020, 1, 1)),
        {"a", "b"},
        frozenset({1, 2}),
        {"nested": [Decimal("1.20"), {"date": date(2022, 2, 2)}]},
        FounderProperties(date(2010, 1, 2), "co-founder", FoundingStage.SEED),
        InvestmentProperties(investment_amount=Decimal("100.10"), currency="USD"),
    ],
)
def test_codec_round_trips_supported_values(value):
    result = loads(dumps(value))
    assert result == value
    if isinstance(value, datetime):
        assert result.tzinfo is not None
        assert result.utcoffset() == timedelta(0)


@pytest.mark.parametrize("value", [float("nan"), float("inf")])
def test_codec_rejects_non_finite_floats(value):
    with pytest.raises(ValueCodecError):
        dumps(value)


def test_codec_rejects_naive_datetime_and_unregistered_types():
    with pytest.raises(ValueCodecError, match="timezone-aware"):
        dumps(datetime(2025, 1, 1))
    with pytest.raises(ValueCodecError, match="Unsupported dataclass"):
        from dataclasses import dataclass

        @dataclass(frozen=True)
        class Unregistered:
            value: str

        dumps(Unregistered("x"))


@pytest.mark.parametrize(
    "payload",
    [
        "not json",
        '{"$type":"unknown"}',
        '{"$type":"enum","class":"os.system","value":"x"}',
        '{"$type":"dataclass","class":"os.system","fields":{}}',
        '{"$type":"decimal","value":"NaN"}',
    ],
)
def test_codec_rejects_malformed_or_untrusted_payloads(payload):
    with pytest.raises(ValueCodecError):
        loads(payload)


@pytest.mark.parametrize(
    "value",
    [
        FoundingStage.SEED,
        AcquisitionType.MERGER,
        HeadquartersFunction.REGISTERED,
        HeadquartersLevel.GLOBAL,
        OperatingStatus.ACTIVE,
        OwnershipType.EQUITY,
        PartnershipStatus.ACTIVE,
        AvailabilityStatus.AVAILABLE,
        DevelopmentStatus.COMPLETED,
        OfferingStatus.COMPLETED,
    ],
)
def test_codec_preserves_str_enum_types(value):
    actual = loads(dumps(value))
    assert type(actual) is type(value)
    assert actual is value


def test_codec_output_is_deterministic_for_mappings_and_sets():
    assert dumps({"b": 2, "a": 1}) == dumps({"a": 1, "b": 2})
    assert dumps({"b", "a"}) == dumps({"a", "b"})


@pytest.mark.parametrize(
    "value",
    [
        AcquisitionProperties(),
        FounderProperties(),
        HeadquartersProperties(),
        IndustryParticipationProperties(),
        InvestmentProperties(),
        LeadershipProperties(),
        MarketPresenceProperties(),
        OwnershipProperties(),
        PartnershipProperties(),
        ProductAvailabilityProperties(),
        ProductDevelopmentProperties(),
        ProductOfferingProperties(),
        ProductTechnologyProperties(),
        ResidenceProperties(),
        TechnologyAdoptionProperties(),
    ],
)
def test_codec_round_trips_every_registered_relationship_property_model(value):
    assert loads(dumps(value)) == value
