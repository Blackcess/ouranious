from datetime import date
from decimal import Decimal
from uuid import uuid4

from domain_models.Identity_model.identity import (
    IdentityReference,
    IdentityRepresentations,
)

from domain_models.Identity_model.Person_model.person import Person
from domain_models.Identity_model.Place_model.place import (
    Place,
    PlaceKind,
)
from domain_models.Identity_model.Industry_model.industry import Industry
from domain_models.Identity_model.Product_model.product import Product
from domain_models.Identity_model.Technology_model.technology import Technology

from domain_models.Identity_model.Organisation_model.organisation import Organisation
from domain_models.Identity_model.Organisation_model.organisation_classification import (
    OrganisationClassification,
)

from domain_models.Identity_model.Organisation_model.classification_specific_domain_model.startup.start_up import (
    Startup,
    StartupStages,
    StartupBusinessModels,
)

from domain_models.Identity_model.Organisation_model.classification_specific_domain_model.investor.investor import (
    Investor,
    InvestmentTypes,
    InvestmentStage,
)

from domain_models.relationship_models.relationship import (
    Relationship,
    RelationshipReference,
)

from domain_models.relationship_models.relationship_properties.properties.acquisitionProperties import (
    AcquisitionProperties,
    AcquisitionType,
)

from domain_models.relationship_models.relationship_properties.properties.founderProperties import (
    FounderProperties,
    FoundingStage,
)

from domain_models.relationship_models.relationship_properties.properties.headquartersProperties import (
    HeadquartersProperties,
    HeadquartersLevel,
    HeadquartersFunction,
)

from domain_models.relationship_models.relationship_properties.properties.industryParticipationProperties import (
    IndustryParticipationProperties,
)

from domain_models.relationship_models.relationship_properties.properties.investmentProperties import (
    InvestmentProperties,
)

from domain_models.relationship_models.relationship_properties.properties.leadershipProperties import (
    LeadershipProperties,
)

from domain_models.relationship_models.relationship_properties.properties.marketPresenceProperties import (
    MarketPresenceProperties,
    OperatingStatus,
)

from domain_models.relationship_models.relationship_properties.properties.ownershipProperties import (
    OwnershipProperties,
    OwnershipType,
)

from domain_models.relationship_models.relationship_properties.properties.partnershipProperties import (
    PartnershipProperties,
    PartnershipStatus,
)

from domain_models.relationship_models.relationship_properties.properties.productAvailabilityProperties import (
    ProductAvailabilityProperties,
    AvailabilityStatus,
)

from domain_models.relationship_models.relationship_properties.properties.productDevelopmentProperties import (
    ProductDevelopmentProperties,
    DevelopmentStatus,
)

from domain_models.relationship_models.relationship_properties.properties.productOfferingProperties import (
    ProductOfferingProperties,
    OfferingStatus,
)

from domain_models.relationship_models.relationship_properties.properties.productTechnologyProperties import (
    ProductTechnologyProperties,
)

from domain_models.relationship_models.relationship_properties.properties.residenceProperties import (
    ResidenceProperties,
)

from domain_models.relationship_models.relationship_properties.properties.technologyAdoptionProperties import (
    TechnologyAdoptionProperties,
)

from domain_models.relationship_models.relationship_types.relationship_types import (
    RelationshipType,
)

from repositories.organisation_repository import (
    OrganisationRepository,
)

from repositories.person_repository import (
    PersonRepository,
)

from repositories.place_repository import (
    PlaceRepository,
)

from repositories.industry_repository import (
    IndustryRepository,
)

from repositories.product_repository import (
    ProductRepository,
)

from repositories.technology_repository import (
    TechnologyRepository,
)

from repositories.relationship_repository import (
    RelationshipRepository,
)

from infrastructure.database.connection import DatabaseManager


def test_complete_virtual_ecosystem_round_trip(database_manager):

    # ============================================================
    # REPOSITORIES
    # ============================================================

    organisation_repository = OrganisationRepository()
    person_repository = PersonRepository()
    place_repository = PlaceRepository()
    industry_repository = IndustryRepository()
    product_repository = ProductRepository()
    technology_repository = TechnologyRepository()

    relationship_repository = RelationshipRepository(
        organisation_repository=organisation_repository,
        person_repository=person_repository,
        place_repository=place_repository,
        industry_repository=industry_repository,
        product_repository=product_repository,
        technology_repository=technology_repository,
    )

    # ============================================================
    # ORGANISATIONS
    # ============================================================

    mobiflow = Organisation(
        representations=IdentityRepresentations(
            canonical_name="MobiFlow Technologies",
            aliases={"MobiFlow"},
        ),
        classifications={
            OrganisationClassification.STARTUP,
        },
        reference=IdentityReference(
            value=uuid4()
        ),
    )

    mobiflow.add_classification_model(
        OrganisationClassification.STARTUP,
        Startup(
            founding_year=2021,
            stage=StartupStages.SEED,
            business_model=StartupBusinessModels.B2B2C,
        ),
    )

    kudu_ventures = Organisation(
        representations=IdentityRepresentations(
            canonical_name="Kudu Ventures",
            aliases={"Kudu"},
        ),
        classifications={
            OrganisationClassification.INVESTOR,
        },
        reference=IdentityReference(
            value=uuid4()
        ),
    )

    kudu_ventures.add_classification_model(
        OrganisationClassification.INVESTOR,
        Investor(
            investor_type=InvestmentTypes.VENTURE_CAPITAL,
            investment_stage=InvestmentStage.SEED,
        ),
    )

    zambezi_capital = Organisation(
        representations=IdentityRepresentations(
            canonical_name="Zambezi Capital",
            aliases={"Zambezi"},
        ),
        classifications={
            OrganisationClassification.INVESTOR,
        },
        reference=IdentityReference(
            value=uuid4()
        ),
    )

    zambezi_capital.add_classification_model(
        OrganisationClassification.INVESTOR,
        Investor(
            investor_type=InvestmentTypes.VENTURE_CAPITAL,
            investment_stage=InvestmentStage.SEED,
        ),
    )

    paylink = Organisation(
        representations=IdentityRepresentations(
            canonical_name="PayLink Africa",
            aliases={"PayLink"},
        ),
        classifications={
            OrganisationClassification.STARTUP,
        },
        reference=IdentityReference(
            value=uuid4()
        ),
    )

    paylink.add_classification_model(
        OrganisationClassification.STARTUP,
        Startup(
            founding_year=2020,
            stage=StartupStages.PRE_SEED,
            business_model=StartupBusinessModels.B2B,
        ),
    )

    # ============================================================
    # PEOPLE
    # ============================================================

    tendai = Person(
        representations=IdentityRepresentations(
            canonical_name="Tendai Moyo",
            aliases={"Tendai"},
        ),
        reference=IdentityReference(
            value=uuid4()
        ),
    )

    farai = Person(
        representations=IdentityRepresentations(
            canonical_name="Farai Chikore",
            aliases={"Farai"},
        ),
        reference=IdentityReference(
            value=uuid4()
        ),
    )

    # ============================================================
    # PLACES
    # ============================================================

    harare = Place(
        representations=IdentityRepresentations(
            canonical_name="Harare",
            aliases={"Harare City"},
        ),
        place_kind=PlaceKind.CITY,
        reference=IdentityReference(
            value=uuid4()
        ),
    )

    bulawayo = Place(
        representations=IdentityRepresentations(
            canonical_name="Bulawayo",
            aliases={"Bulawayo City"},
        ),
        place_kind=PlaceKind.CITY,
        reference=IdentityReference(
            value=uuid4()
        ),
    )

    zimbabwe = Place(
        representations=IdentityRepresentations(
            canonical_name="Zimbabwe",
            aliases={"Republic of Zimbabwe"},
        ),
        place_kind=PlaceKind.COUNTRY,
        reference=IdentityReference(
            value=uuid4()
        ),
    )

    south_africa = Place(
        representations=IdentityRepresentations(
            canonical_name="South Africa",
            aliases={"Republic of South Africa"},
        ),
        place_kind=PlaceKind.COUNTRY,
        reference=IdentityReference(
            value=uuid4()
        ),
    )

    # ============================================================
    # INDUSTRY
    # ============================================================

    fintech = Industry(
        representations=IdentityRepresentations(
            canonical_name="Financial Technology",
            aliases={"Fintech"},
        ),
        reference=IdentityReference(
            value=uuid4()
        ),
    )

    # ============================================================
    # PRODUCTS
    # ============================================================

    mobipay = Product(
        representations=IdentityRepresentations(
            canonical_name="MobiPay",
            aliases={"MobiPay Platform"},
        ),
        reference=IdentityReference(
            value=uuid4()
        ),
    )

    mobiflow_api = Product(
        representations=IdentityRepresentations(
            canonical_name="MobiFlow API",
            aliases={"MobiFlow Developer API"},
        ),
        reference=IdentityReference(
            value=uuid4()
        ),
    )

    # ============================================================
    # TECHNOLOGIES
    # ============================================================

    python = Technology(
        representations=IdentityRepresentations(
            canonical_name="Python",
            aliases={"Python Programming Language"},
        ),
        reference=IdentityReference(
            value=uuid4()
        ),
    )

    cloud = Technology(
        representations=IdentityRepresentations(
            canonical_name="Cloud Infrastructure",
            aliases={"Cloud Computing"},
        ),
        reference=IdentityReference(
            value=uuid4()
        ),
    )

    # ============================================================
    # RELATIONSHIPS
    # ============================================================

    relationships = []

    # ------------------------------------------------------------
    # TENDai → MOBIFLOW
    # ------------------------------------------------------------

    tendai_founded = Relationship(
        source=tendai,
        target=mobiflow,
        type=RelationshipType.FOUNDED,
        properties=FounderProperties(
            founding_date=date(2021, 3, 10),
            founder_role="Co-Founder",
            founding_stage=FoundingStage.SEED,
        ),
        reference=RelationshipReference(value=uuid4()),
    )

    relationships.append(tendai_founded)

    tendai_leads = Relationship(
        source=tendai,
        target=mobiflow,
        type=RelationshipType.LEADS,
        properties=LeadershipProperties(
            position="Chief Executive Officer",
            start_date=date(2021, 3, 10),
            end_date=None,
            is_current=True,
        ),
        reference=RelationshipReference(value=uuid4()),
    )

    relationships.append(tendai_leads)

    tendai_owns = Relationship(
        source=tendai,
        target=mobiflow,
        type=RelationshipType.OWNS,
        properties=OwnershipProperties(
            ownership_percentage=Decimal("32.500000"),
            ownership_type=OwnershipType.EQUITY,
            share_class="Ordinary",
            start_date=date(2021, 3, 10),
            end_date=None,
            is_current=True,
        ),
        reference=RelationshipReference(value=uuid4()),
    )

    relationships.append(tendai_owns)

    tendai_born = Relationship(
        source=tendai,
        target=harare,
        type=RelationshipType.BORN_IN,
        properties=None,
        reference=RelationshipReference(value=uuid4()),
    )

    relationships.append(tendai_born)

    tendai_lives = Relationship(
        source=tendai,
        target=harare,
        type=RelationshipType.LIVES_IN,
        properties=ResidenceProperties(
            start_date=date(2021, 1, 1),
            end_date=None,
            is_current=True,
            residence_type="Primary Residence",
        ),
        reference=RelationshipReference(value=uuid4()),
    )

    relationships.append(tendai_lives)

    # ------------------------------------------------------------
    # FARAI → MOBIFLOW
    # ------------------------------------------------------------

    farai_founded = Relationship(
        source=farai,
        target=mobiflow,
        type=RelationshipType.FOUNDED,
        properties=FounderProperties(
            founding_date=date(2021, 3, 10),
            founder_role="Co-Founder",
            founding_stage=FoundingStage.SEED,
        ),
        reference=RelationshipReference(value=uuid4()),
    )

    relationships.append(farai_founded)

    farai_leads = Relationship(
        source=farai,
        target=mobiflow,
        type=RelationshipType.LEADS,
        properties=LeadershipProperties(
            position="Chief Technology Officer",
            start_date=date(2021, 3, 10),
            end_date=None,
            is_current=True,
        ),
        reference=RelationshipReference(value=uuid4()),
    )

    relationships.append(farai_leads)

    farai_owns = Relationship(
        source=farai,
        target=mobiflow,
        type=RelationshipType.OWNS,
        properties=OwnershipProperties(
            ownership_percentage=Decimal("17.500000"),
            ownership_type=OwnershipType.EQUITY,
            share_class="Ordinary",
            start_date=date(2021, 3, 10),
            end_date=None,
            is_current=True,
        ),
        reference=RelationshipReference(value=uuid4()),
    )

    relationships.append(farai_owns)

    farai_born = Relationship(
        source=farai,
        target=bulawayo,
        type=RelationshipType.BORN_IN,
        properties=None,
        reference=RelationshipReference(value=uuid4()),
    )

    relationships.append(farai_born)

    farai_lives = Relationship(
        source=farai,
        target=harare,
        type=RelationshipType.LIVES_IN,
        properties=ResidenceProperties(
            start_date=date(2021, 3, 10),
            end_date=None,
            is_current=True,
            residence_type="Primary Residence",
        ),
        reference=RelationshipReference(value=uuid4()),
    )

    relationships.append(farai_lives)

    # ------------------------------------------------------------
    # INVESTMENT
    # ------------------------------------------------------------

    kudu_invests = Relationship(
        source=kudu_ventures,
        target=mobiflow,
        type=RelationshipType.INVESTED_IN,
        properties=InvestmentProperties(
            investment_amount=Decimal("750000.00"),
            currency="USD",
            investment_date=date(2025, 6, 15),
            funding_round=InvestmentStage.SEED,
            pre_money_valuation=Decimal("2500000.00"),
            post_money_valuation=Decimal("3250000.00"),
            equity_percentage=Decimal("23.076923"),
            is_lead_investor=True,
        ),
        reference=RelationshipReference(value=uuid4()),
    )

    relationships.append(kudu_invests)

    # ------------------------------------------------------------
    # INVESTOR PARTNERSHIP
    # ------------------------------------------------------------

    investor_partnership = Relationship(
        source=kudu_ventures,
        target=zambezi_capital,
        type=RelationshipType.PARTNERED_WITH,
        properties=PartnershipProperties(
            start_date=date(2025, 1, 1),
            end_date=None,
            partnership_status=PartnershipStatus.ACTIVE,
        ),
        reference=RelationshipReference(value=uuid4()),
    )

    relationships.append(investor_partnership)

    # ------------------------------------------------------------
    # ACQUISITION
    # ------------------------------------------------------------

    acquisition = Relationship(
        source=mobiflow,
        target=paylink,
        type=RelationshipType.ACQUIRED,
        properties=AcquisitionProperties(
            acquisition_date=date(2026, 2, 20),
            acquisition_amount=Decimal("1200000.00"),
            currency="USD",
            ownership_percentage_acquired=Decimal("100.000000"),
            acquisition_type=AcquisitionType.FULL_ACQUISITION,
        ),
        reference=RelationshipReference(value=uuid4()),
    )

    relationships.append(acquisition)

    # ------------------------------------------------------------
    # HEADQUARTERS
    # ------------------------------------------------------------

    headquarters = Relationship(
        source=mobiflow,
        target=harare,
        type=RelationshipType.HEADQUARTERED_IN,
        properties=HeadquartersProperties(
            headquarters_level=HeadquartersLevel.GLOBAL,
            headquarters_function=HeadquartersFunction.OPERATIONAL,
            start_date=date(2021, 3, 10),
            end_date=None,
            is_current=True,
        ),
        reference=RelationshipReference(value=uuid4()),
    )

    relationships.append(headquarters)

    # ------------------------------------------------------------
    # MARKET PRESENCE
    # ------------------------------------------------------------

    operates_zimbabwe = Relationship(
        source=mobiflow,
        target=zimbabwe,
        type=RelationshipType.OPERATES_IN,
        properties=MarketPresenceProperties(
            entry_date=date(2021, 3, 10),
            exit_date=None,
            is_current=True,
            operating_status=OperatingStatus.ACTIVE,
        ),
        reference=RelationshipReference(value=uuid4()),
    )

    relationships.append(operates_zimbabwe)

    operates_south_africa = Relationship(
        source=mobiflow,
        target=south_africa,
        type=RelationshipType.OPERATES_IN,
        properties=MarketPresenceProperties(
            entry_date=date(2025, 9, 1),
            exit_date=None,
            is_current=True,
            operating_status=OperatingStatus.ACTIVE,
        ),
        reference=RelationshipReference(value=uuid4()),
    )

    relationships.append(operates_south_africa)

    # ------------------------------------------------------------
    # INDUSTRY
    # ------------------------------------------------------------

    operates_fintech = Relationship(
        source=mobiflow,
        target=fintech,
        type=RelationshipType.OPERATES_IN_INDUSTRY,
        properties=IndustryParticipationProperties(
            start_date=date(2021, 3, 10),
            end_date=None,
            is_primary_industry=True,
        ),
        reference=RelationshipReference(value=uuid4()),
    )

    relationships.append(operates_fintech)

    # ------------------------------------------------------------
    # PRODUCT OFFERING
    # ------------------------------------------------------------

    offers_mobipay = Relationship(
        source=mobiflow,
        target=mobipay,
        type=RelationshipType.OFFERS,
        properties=ProductOfferingProperties(
            launch_date=date(2022, 5, 1),
            discontinuation_date=None,
            offering_status=OfferingStatus.COMPLETED,
        ),
        reference=RelationshipReference(value=uuid4()),
    )

    relationships.append(offers_mobipay)

    # ------------------------------------------------------------
    # PRODUCT DEVELOPMENT
    # ------------------------------------------------------------

    develops_api = Relationship(
        source=mobiflow,
        target=mobiflow_api,
        type=RelationshipType.DEVELOPS,
        properties=ProductDevelopmentProperties(
            development_start_date=date(2025, 1, 15),
            release_date=date(2025, 8, 1),
            development_status=DevelopmentStatus.COMPLETED,
        ),
        reference=RelationshipReference(value=uuid4()),
    )

    relationships.append(develops_api)

    # ------------------------------------------------------------
    # TECHNOLOGY ADOPTION
    # ------------------------------------------------------------

    uses_python = Relationship(
        source=mobiflow,
        target=python,
        type=RelationshipType.USES,
        properties=TechnologyAdoptionProperties(
            adoption_date=date(2021, 3, 10),
        ),
        reference=RelationshipReference(value=uuid4()),
    )

    relationships.append(uses_python)

    # ------------------------------------------------------------
    # PRODUCT TECHNOLOGY
    # ------------------------------------------------------------

    api_built_with_cloud = Relationship(
        source=mobiflow_api,
        target=cloud,
        type=RelationshipType.BUILT_WITH,
        properties=ProductTechnologyProperties(
            adoption_date=date(2025, 1, 15),
            is_core_technology=True,
        ),
        reference=RelationshipReference(value=uuid4()),
    )

    relationships.append(api_built_with_cloud)

    # ------------------------------------------------------------
    # PRODUCT AVAILABILITY
    # ------------------------------------------------------------

    mobipay_available = Relationship(
        source=mobipay,
        target=zimbabwe,
        type=RelationshipType.AVAILABLE_IN,
        properties=ProductAvailabilityProperties(
            launch_date=date(2022, 5, 1),
            discontinuation_date=None,
            availability_status=AvailabilityStatus.AVAILABLE,
        ),
        reference=RelationshipReference(value=uuid4()),
    )

    relationships.append(mobipay_available)

    # ------------------------------------------------------------
    # PLACE HIERARCHY
    # ------------------------------------------------------------

    harare_located_in = Relationship(
        source=harare,
        target=zimbabwe,
        type=RelationshipType.LOCATED_IN,
        properties=None,
        reference=RelationshipReference(value=uuid4()),
    )

    relationships.append(harare_located_in)

    harare_part_of = Relationship(
        source=harare,
        target=zimbabwe,
        type=RelationshipType.PART_OF,
        properties=None,
        reference=RelationshipReference(value=uuid4()),
    )

    relationships.append(harare_part_of)

    bulawayo_located_in = Relationship(
        source=bulawayo,
        target=zimbabwe,
        type=RelationshipType.LOCATED_IN,
        properties=None,
        reference=RelationshipReference(value=uuid4()),
    )

    relationships.append(bulawayo_located_in)

    # ============================================================
    # PERSIST EVERYTHING
    # ============================================================

    identities = [
        mobiflow,
        kudu_ventures,
        zambezi_capital,
        paylink,

        tendai,
        farai,

        harare,
        bulawayo,
        zimbabwe,
        south_africa,

        fintech,

        mobipay,
        mobiflow_api,

        python,
        cloud,
    ]

    with database_manager.transaction() as connection:

        # Organisations
        organisation_repository.save(
            mobiflow,
            connection=connection,
        )

        organisation_repository.save(
            kudu_ventures,
            connection=connection,
        )

        organisation_repository.save(
            zambezi_capital,
            connection=connection,
        )

        organisation_repository.save(
            paylink,
            connection=connection,
        )

        # People
        person_repository.save(
            tendai,
            connection=connection,
        )

        person_repository.save(
            farai,
            connection=connection,
        )

        # Places
        place_repository.save(
            harare,
            connection=connection,
        )

        place_repository.save(
            bulawayo,
            connection=connection,
        )

        place_repository.save(
            zimbabwe,
            connection=connection,
        )

        place_repository.save(
            south_africa,
            connection=connection,
        )

        # Industry
        industry_repository.save(
            fintech,
            connection=connection,
        )

        # Products
        product_repository.save(
            mobipay,
            connection=connection,
        )

        product_repository.save(
            mobiflow_api,
            connection=connection,
        )

        # Technologies
        technology_repository.save(
            python,
            connection=connection,
        )

        technology_repository.save(
            cloud,
            connection=connection,
        )

        # Relationships
        for relationship in relationships:

            relationship_repository.save(
                relationship,
                connection=connection,
            )

    # ============================================================
    # RETRIEVE EVERYTHING
    # ============================================================

    with database_manager.connection() as connection:

        retrieved_relationships = []

        for relationship in relationships:

            retrieved = relationship_repository.get_by_id(
                relationship.get_reference(),
                connection=connection,
            )

            retrieved_relationships.append(
                retrieved
            )

        # ============================================================
        # VERIFY RELATIONSHIP COUNT
        # ============================================================

        assert len(retrieved_relationships) == len(
            relationships
        )

        # ============================================================
        # VERIFY EVERY RELATIONSHIP
        # ============================================================

        for original, retrieved in zip(
            relationships,
            retrieved_relationships,
        ):

            assert retrieved is not None

            assert (
                retrieved.get_reference().value
                == original.get_reference().value
            )

            assert (
                retrieved.get_source().reference.value
                == original.get_source().reference.value
            )

            assert (
                retrieved.get_target().reference.value
                == original.get_target().reference.value
            )

            assert (
                retrieved.get_type()
                == original.get_type()
            )

            assert (
                retrieved.get_properties()
                == original.get_properties()
            )

        # ============================================================
        # VERIFY ALL RELATIONSHIP TYPES WERE TESTED
        # ============================================================

        relationship_types = {
            relationship.get_type()
            for relationship in relationships
        }

        expected_relationship_types = {
            RelationshipType.FOUNDED,
            RelationshipType.LEADS,
            RelationshipType.OWNS,
            RelationshipType.BORN_IN,
            RelationshipType.LIVES_IN,
            RelationshipType.PARTNERED_WITH,
            RelationshipType.INVESTED_IN,
            RelationshipType.ACQUIRED,
            RelationshipType.HEADQUARTERED_IN,
            RelationshipType.OPERATES_IN,
            RelationshipType.OPERATES_IN_INDUSTRY,
            RelationshipType.OFFERS,
            RelationshipType.DEVELOPS,
            RelationshipType.USES,
            RelationshipType.BUILT_WITH,
            RelationshipType.AVAILABLE_IN,
            RelationshipType.LOCATED_IN,
            RelationshipType.PART_OF,
        }

        assert relationship_types == expected_relationship_types

        # ============================================================
        # VERIFY THE VIRTUAL ECOSYSTEM'S IDENTITY ENDPOINTS
        # ============================================================

        assert len(identities) == 15

        for identity in identities:

            identity_id = identity.reference.value

            if isinstance(identity, Organisation):

                retrieved_identity = (
                    organisation_repository.get_by_id(
                        identity_id,
                        connection=connection,
                    )
                )

            elif isinstance(identity, Person):

                retrieved_identity = (
                    person_repository.get_by_id(
                        identity_id,
                        connection=connection,
                    )
                )

            elif isinstance(identity, Place):

                retrieved_identity = (
                    place_repository.get_by_id(
                        identity_id,
                        connection=connection,
                    )
                )

            elif isinstance(identity, Industry):

                retrieved_identity = (
                    industry_repository.get_by_id(
                        identity_id,
                        connection=connection,
                    )
                )

            elif isinstance(identity, Product):

                retrieved_identity = (
                    product_repository.get_by_id(
                        identity_id,
                        connection=connection,
                    )
                )

            elif isinstance(identity, Technology):

                retrieved_identity = (
                    technology_repository.get_by_id(
                        identity_id,
                        connection=connection,
                    )
                )

            else:

                raise AssertionError(
                    f"Unsupported identity type: "
                    f"{type(identity).__name__}"
                )

            assert retrieved_identity is not None

            assert (
                retrieved_identity.reference.value
                == identity.reference.value
            )

            assert (
                retrieved_identity.representations.canonical_name
                == identity.representations.canonical_name
            )

            assert (
                retrieved_identity.representations.aliases
                == identity.representations.aliases
            )

    print(
        "TEST PASSED: "
        "test_complete_virtual_ecosystem_round_trip"
    )

    return retrieved_relationships


relationships = test_complete_virtual_ecosystem_round_trip(
    DatabaseManager()
)

import time

for rel in relationships:
    print(f"{rel.get_source().representations.canonical_name} ---{rel.get_type()}---> {rel.get_target().representations.canonical_name} \n")
    time.sleep(1)
