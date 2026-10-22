from decimal import Decimal
from uuid import UUID

from pymysql.connections import Connection

from domain_models.Identity_model.identity import IdentityKind, IdentityReference
from domain_models.Identity_model.Organisation_model.classification_specific_domain_model.investor.investor import InvestmentStage
from domain_models.Identity_model.Organisation_model.organisation import Organisation

from domain_models.relationship_models.relationship_types.relationship_types import (
    RelationshipType,
)
from domain_models.relationship_models.relationship_types.relationship_type_specification import (
    specification_registry,
)
from domain_models.relationship_models.relationship import (
    Relationship,
    RelationshipReference,
)

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

from domain_models.Identity_model.Organisation_model.classification_specific_domain_model.investor.investor import  (
    InvestmentStage,
)

from repositories.organisation_repository import (
    OrganisationRepository,
    RepositoryIntegrityError,
)

from repositories.person_repository import PersonRepository
from repositories.place_repository import PlaceRepository
from repositories.industry_repository import IndustryRepository
from repositories.product_repository import ProductRepository
from repositories.technology_repository import TechnologyRepository
from repositories.utils.candidate_page import CandidatePage

# Enums Imports
from domain_models.relationship_models.relationship_properties.properties.acquisitionProperties import (
    AcquisitionType,
)
from domain_models.relationship_models.relationship_properties.properties.founderProperties import (
    FoundingStage,
)
from domain_models.relationship_models.relationship_properties.properties.headquartersProperties import (
    HeadquartersLevel,
    HeadquartersFunction,
)
from domain_models.relationship_models.relationship_properties.properties.investmentProperties import (
    InvestmentProperties,
)
from domain_models.relationship_models.relationship_properties.properties.marketPresenceProperties import (
    OperatingStatus,
)
from domain_models.relationship_models.relationship_properties.properties.ownershipProperties import (
    OwnershipType,
)
from domain_models.relationship_models.relationship_properties.properties.partnershipProperties import (
    PartnershipStatus,
)
from domain_models.relationship_models.relationship_properties.properties.productAvailabilityProperties import (
    AvailabilityStatus,
)
from domain_models.relationship_models.relationship_properties.properties.productDevelopmentProperties import (
    DevelopmentStatus,
)
from domain_models.relationship_models.relationship_properties.properties.productOfferingProperties import (
    OfferingStatus,
)


def _identity_reference_bytes(reference: UUID | IdentityReference) -> bytes:
    if isinstance(reference, IdentityReference):
        return reference.value.bytes
    if isinstance(reference, UUID):
        return reference.bytes
    raise TypeError("identity reference must be UUID or IdentityReference")


class RelationshipRepository:

    def __init__(
        self,
        *,
        organisation_repository: OrganisationRepository | None = None,
        person_repository: PersonRepository | None = None,
        place_repository: PlaceRepository | None = None,
        industry_repository: IndustryRepository | None = None,
        product_repository: ProductRepository | None = None,
        technology_repository: TechnologyRepository | None = None,
    ):
        self._organisation_repository = (
            organisation_repository or OrganisationRepository()
        )

        self._person_repository = (
            person_repository or PersonRepository()
        )

        self._place_repository = (
            place_repository or PlaceRepository()
        )

        self._industry_repository = (
            industry_repository or IndustryRepository()
        )

        self._product_repository = (
            product_repository or ProductRepository()
        )

        self._technology_repository = (
            technology_repository or TechnologyRepository()
        )

    def find_candidates(
        self,
        *,
        source_reference: UUID | IdentityReference,
        target_reference: UUID | IdentityReference,
        relationship_type: RelationshipType,
        limit: int = 100,
        connection: Connection,
    ) -> CandidatePage[Relationship]:
        """Return relationships matching the endpoint/type candidate key."""

        if not isinstance(relationship_type, RelationshipType):
            raise TypeError("relationship_type must be a RelationshipType")
        if isinstance(limit, bool) or not isinstance(limit, int):
            raise TypeError("limit must be an integer")
        if limit <= 0:
            raise ValueError("limit must be greater than zero")

        source_id = _identity_reference_bytes(source_reference)
        target_id = _identity_reference_bytes(target_reference)

        with connection.cursor() as cursor:
            cursor.execute(
                """
                SELECT relationship_id
                FROM relationships
                WHERE source_identity_id = %s
                  AND target_identity_id = %s
                  AND relationship_type = %s
                ORDER BY relationship_id
                LIMIT %s
                """,
                (
                    source_id,
                    target_id,
                    relationship_type.value,
                    limit + 1,
                ),
            )
            rows = cursor.fetchall()

        relationship_ids = [row["relationship_id"] for row in rows]
        truncated = len(relationship_ids) > limit
        relationships = tuple(
            relationship
            for relationship_id in relationship_ids[:limit]
            if (
                relationship := self.get_by_id(
                    UUID(bytes=relationship_id),
                    connection=connection,
                )
            ) is not None
        )
        return CandidatePage(relationships, truncated=truncated)

    # ============================================================
    # SAVE
    # ============================================================

    def save(
        self,
        relationship: Relationship,
        *,
        connection: Connection,
    ) -> None:
        """
        Persist a Relationship.

        The caller owns the transaction.
        This method does not commit or roll back.

        All currently supported relationship types can be persisted.
        """

        self._validate_relationship(relationship)

        relationship_id = (
            relationship.get_reference().value.bytes
        )

        source_id = (
            relationship.get_source().reference.value.bytes
        )

        target_id = (
            relationship.get_target().reference.value.bytes
        )

        relationship_type = relationship.get_type()

        with connection.cursor() as cursor:

            # ----------------------------------------------------
            # 1. Persist base relationship
            # ----------------------------------------------------

            cursor.execute(
                """
                INSERT INTO relationships (
                    relationship_id,
                    source_identity_id,
                    target_identity_id,
                    relationship_type
                )
                VALUES (%s, %s, %s, %s)
                """,
                (
                    relationship_id,
                    source_id,
                    target_id,
                    relationship_type.value,
                ),
            )

            # ----------------------------------------------------
            # 2. Persist relationship-specific properties
            # ----------------------------------------------------

            self._save_properties(
                relationship,
                relationship_id,
                cursor,
            )

    # ============================================================
    # GET
    # ============================================================

    def get_by_id(
        self,
        reference: UUID | RelationshipReference,
        *,
        connection: Connection,
    ) -> Relationship | None:
        """
        Retrieve a Relationship by UUID.

        Reconstruction is delegated to a relationship-specific
        reconstruction method.
        """

        if isinstance(reference, RelationshipReference):
            reference = reference.value

        if not isinstance(reference, UUID):
            raise TypeError(
                "reference must be UUID or RelationshipReference"
            )

        relationship_id = reference.bytes

        with connection.cursor() as cursor:

            cursor.execute(
                """
                SELECT
                    relationship_id,
                    source_identity_id,
                    target_identity_id,
                    relationship_type
                FROM relationships
                WHERE relationship_id = %s
                """,
                (relationship_id,),
            )

            record = cursor.fetchone()

        if record is None:
            return None

        relationship_type = RelationshipType(
            record["relationship_type"]
        )

        source_id = UUID(
            bytes=record["source_identity_id"]
        )

        target_id = UUID(
            bytes=record["target_identity_id"]
        )

        reconstruction_methods = {
            RelationshipType.FOUNDED: self._reconstruct_founded,
            RelationshipType.LEADS: self._reconstruct_leads,
            RelationshipType.OWNS: self._reconstruct_owns,
            RelationshipType.BORN_IN: self._reconstruct_born_in,
            RelationshipType.LIVES_IN: self._reconstruct_lives_in,
            RelationshipType.PARTNERED_WITH: self._reconstruct_partnered_with,
            RelationshipType.INVESTED_IN: self._reconstruct_invested_in,
            RelationshipType.ACQUIRED: self._reconstruct_acquired,
            RelationshipType.HEADQUARTERED_IN: self._reconstruct_headquartered_in,
            RelationshipType.OPERATES_IN: self._reconstruct_operates_in,
            RelationshipType.OPERATES_IN_INDUSTRY: (
                self._reconstruct_operates_in_industry
            ),
            RelationshipType.OFFERS: self._reconstruct_offers,
            RelationshipType.DEVELOPS: self._reconstruct_develops,
            RelationshipType.USES: self._reconstruct_uses,
            RelationshipType.BUILT_WITH: self._reconstruct_built_with,
            RelationshipType.AVAILABLE_IN: self._reconstruct_available_in,
            RelationshipType.LOCATED_IN: self._reconstruct_located_in,
            RelationshipType.PART_OF: self._reconstruct_part_of,
        }

        reconstruction_method = reconstruction_methods.get(
            relationship_type
        )

        if reconstruction_method is None:
            raise NotImplementedError(
                "Relationship reconstruction for "
                f"{relationship_type.value} is not implemented."
            )

        return reconstruction_method(
            relationship_id=relationship_id,
            source_id=source_id,
            target_id=target_id,
            connection=connection,
        )

    # ============================================================
    # PROPERTY DISPATCH
    # ============================================================

    def _save_properties(
        self,
        relationship: Relationship,
        relationship_id: bytes,
        cursor,
    ) -> None:

        relationship_type = relationship.get_type()
        properties = relationship.get_properties()

        # --------------------------------------------------------
        # FOUNDED
        # --------------------------------------------------------

        if relationship_type == RelationshipType.FOUNDED:

            self._save_founder_properties(
                relationship_id,
                properties,
                cursor,
            )

        # --------------------------------------------------------
        # LEADS
        # --------------------------------------------------------

        elif relationship_type == RelationshipType.LEADS:

            self._save_leadership_properties(
                relationship_id,
                properties,
                cursor,
            )

        # --------------------------------------------------------
        # OWNS
        # --------------------------------------------------------

        elif relationship_type == RelationshipType.OWNS:

            self._save_ownership_properties(
                relationship_id,
                properties,
                cursor,
            )

        # --------------------------------------------------------
        # BORN_IN
        # --------------------------------------------------------

        elif relationship_type == RelationshipType.BORN_IN:

            self._assert_no_properties(
                relationship_type,
                properties,
            )

        # --------------------------------------------------------
        # LIVES_IN
        # --------------------------------------------------------

        elif relationship_type == RelationshipType.LIVES_IN:

            self._save_residence_properties(
                relationship_id,
                properties,
                cursor,
            )

        # --------------------------------------------------------
        # PARTNERED_WITH
        # --------------------------------------------------------

        elif relationship_type == RelationshipType.PARTNERED_WITH:

            self._save_partnership_properties(
                relationship_id,
                properties,
                cursor,
            )

        # --------------------------------------------------------
        # INVESTED_IN
        # --------------------------------------------------------

        elif relationship_type == RelationshipType.INVESTED_IN:

            self._save_investment_properties(
                relationship_id,
                properties,
                cursor,
            )

        # --------------------------------------------------------
        # ACQUIRED
        # --------------------------------------------------------

        elif relationship_type == RelationshipType.ACQUIRED:

            self._save_acquisition_properties(
                relationship_id,
                properties,
                cursor,
            )

        # --------------------------------------------------------
        # HEADQUARTERED_IN
        # --------------------------------------------------------

        elif relationship_type == RelationshipType.HEADQUARTERED_IN:

            self._save_headquarters_properties(
                relationship_id,
                properties,
                cursor,
            )

        # --------------------------------------------------------
        # OPERATES_IN
        # --------------------------------------------------------

        elif relationship_type == RelationshipType.OPERATES_IN:

            self._save_market_presence_properties(
                relationship_id,
                properties,
                cursor,
            )

        # --------------------------------------------------------
        # OPERATES_IN_INDUSTRY
        # --------------------------------------------------------

        elif relationship_type == RelationshipType.OPERATES_IN_INDUSTRY:

            self._save_industry_participation_properties(
                relationship_id,
                properties,
                cursor,
            )

        # --------------------------------------------------------
        # OFFERS
        # --------------------------------------------------------

        elif relationship_type == RelationshipType.OFFERS:

            self._save_product_offering_properties(
                relationship_id,
                properties,
                cursor,
            )

        # --------------------------------------------------------
        # DEVELOPS
        # --------------------------------------------------------

        elif relationship_type == RelationshipType.DEVELOPS:

            self._save_product_development_properties(
                relationship_id,
                properties,
                cursor,
            )

        # --------------------------------------------------------
        # USES
        # --------------------------------------------------------

        elif relationship_type == RelationshipType.USES:

            self._save_technology_adoption_properties(
                relationship_id,
                properties,
                cursor,
            )

        # --------------------------------------------------------
        # BUILT_WITH
        # --------------------------------------------------------

        elif relationship_type == RelationshipType.BUILT_WITH:

            self._save_product_technology_properties(
                relationship_id,
                properties,
                cursor,
            )

        # --------------------------------------------------------
        # AVAILABLE_IN
        # --------------------------------------------------------

        elif relationship_type == RelationshipType.AVAILABLE_IN:

            self._save_product_availability_properties(
                relationship_id,
                properties,
                cursor,
            )

        # --------------------------------------------------------
        # LOCATED_IN
        # --------------------------------------------------------

        elif relationship_type == RelationshipType.LOCATED_IN:

            self._assert_no_properties(
                relationship_type,
                properties,
            )

        # --------------------------------------------------------
        # PART_OF
        # --------------------------------------------------------

        elif relationship_type == RelationshipType.PART_OF:

            self._assert_no_properties(
                relationship_type,
                properties,
            )

        else:
            raise NotImplementedError(
                f"Persistence for relationship type "
                f"{relationship_type.value} is not implemented."
            )

    # ============================================================
    # PROPERTY SAVE METHODS
    # ============================================================

    def _save_investment_properties(
        self,
        relationship_id: bytes,
        properties: InvestmentProperties,
        cursor,
    ) -> None:

        cursor.execute(
            """
            INSERT INTO relationship_investment_properties (
                relationship_id,
                relationship_type,
                investment_amount,
                currency,
                investment_date,
                funding_round,
                pre_money_valuation,
                post_money_valuation,
                equity_percentage,
                is_lead_investor
            )
            VALUES (
                %s, %s, %s, %s, %s,
                %s, %s, %s, %s, %s
            )
            """,
            (
                relationship_id,
                RelationshipType.INVESTED_IN.value,
                properties.investment_amount,
                properties.currency,
                properties.investment_date,
                (
                    properties.funding_round.value
                    if properties.funding_round is not None
                    else None
                ),
                properties.pre_money_valuation,
                properties.post_money_valuation,
                properties.equity_percentage,
                properties.is_lead_investor,
            ),
        )

    def _save_acquisition_properties(
        self,
        relationship_id: bytes,
        properties: AcquisitionProperties,
        cursor,
    ) -> None:

        cursor.execute(
            """
            INSERT INTO relationship_acquisition_properties (
                relationship_id,
                relationship_type,
                acquisition_date,
                acquisition_amount,
                currency,
                ownership_percentage_acquired,
                acquisition_type
            )
            VALUES (%s, %s, %s, %s, %s, %s, %s)
            """,
            (
                relationship_id,
                RelationshipType.ACQUIRED.value,
                properties.acquisition_date,
                properties.acquisition_amount,
                properties.currency,
                properties.ownership_percentage_acquired,
                (
                    properties.acquisition_type.value
                    if properties.acquisition_type is not None
                    else None
                ),
            ),
        )

    def _save_founder_properties(
        self,
        relationship_id: bytes,
        properties: FounderProperties,
        cursor,
    ) -> None:

        cursor.execute(
            """
            INSERT INTO relationship_founder_properties (
                relationship_id,
                relationship_type,
                founding_date,
                founder_role,
                founding_stage
            )
            VALUES (%s, %s, %s, %s, %s)
            """,
            (
                relationship_id,
                RelationshipType.FOUNDED.value,
                properties.founding_date,
                properties.founder_role,
                (
                    properties.founding_stage.value
                    if properties.founding_stage is not None
                    else None
                ),
            ),
        )

    def _save_headquarters_properties(
        self,
        relationship_id: bytes,
        properties: HeadquartersProperties,
        cursor,
    ) -> None:

        cursor.execute(
            """
            INSERT INTO relationship_headquarters_properties (
                relationship_id,
                relationship_type,
                headquarters_level,
                headquarters_function,
                start_date,
                end_date,
                is_current
            )
            VALUES (%s, %s, %s, %s, %s, %s, %s)
            """,
            (
                relationship_id,
                RelationshipType.HEADQUARTERED_IN.value,
                (
                    properties.headquarters_level.value
                    if properties.headquarters_level is not None
                    else None
                ),
                (
                    properties.headquarters_function.value
                    if properties.headquarters_function is not None
                    else None
                ),
                properties.start_date,
                properties.end_date,
                properties.is_current,
            ),
        )

    def _save_industry_participation_properties(
        self,
        relationship_id: bytes,
        properties: IndustryParticipationProperties,
        cursor,
    ) -> None:

        cursor.execute(
            """
            INSERT INTO relationship_industry_participation_properties (
                relationship_id,
                relationship_type,
                start_date,
                end_date,
                is_primary_industry
            )
            VALUES (%s, %s, %s, %s, %s)
            """,
            (
                relationship_id,
                RelationshipType.OPERATES_IN_INDUSTRY.value,
                properties.start_date,
                properties.end_date,
                properties.is_primary_industry,
            ),
        )

    def _save_leadership_properties(
        self,
        relationship_id: bytes,
        properties: LeadershipProperties,
        cursor,
    ) -> None:

        cursor.execute(
            """
            INSERT INTO relationship_leadership_properties (
                relationship_id,
                relationship_type,
                position,
                start_date,
                end_date,
                is_current
            )
            VALUES (%s, %s, %s, %s, %s, %s)
            """,
            (
                relationship_id,
                RelationshipType.LEADS.value,
                properties.position,
                properties.start_date,
                properties.end_date,
                properties.is_current,
            ),
        )

    def _save_market_presence_properties(
        self,
        relationship_id: bytes,
        properties: MarketPresenceProperties,
        cursor,
    ) -> None:

        cursor.execute(
            """
            INSERT INTO relationship_market_presence_properties (
                relationship_id,
                relationship_type,
                entry_date,
                exit_date,
                is_current,
                operating_status
            )
            VALUES (%s, %s, %s, %s, %s, %s)
            """,
            (
                relationship_id,
                RelationshipType.OPERATES_IN.value,
                properties.entry_date,
                properties.exit_date,
                properties.is_current,
                (
                    properties.operating_status.value
                    if properties.operating_status is not None
                    else None
                ),
            ),
        )

    def _save_ownership_properties(
        self,
        relationship_id: bytes,
        properties: OwnershipProperties,
        cursor,
    ) -> None:

        cursor.execute(
            """
            INSERT INTO relationship_ownership_properties (
                relationship_id,
                relationship_type,
                ownership_percentage,
                ownership_type,
                share_class,
                start_date,
                end_date,
                is_current
            )
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
            """,
            (
                relationship_id,
                RelationshipType.OWNS.value,
                properties.ownership_percentage,
                (
                    properties.ownership_type.value
                    if properties.ownership_type is not None
                    else None
                ),
                properties.share_class,
                properties.start_date,
                properties.end_date,
                properties.is_current,
            ),
        )

    def _save_partnership_properties(
        self,
        relationship_id: bytes,
        properties: PartnershipProperties,
        cursor,
    ) -> None:

        cursor.execute(
            """
            INSERT INTO relationship_partnership_properties (
                relationship_id,
                relationship_type,
                start_date,
                end_date,
                partnership_status
            )
            VALUES (%s, %s, %s, %s, %s)
            """,
            (
                relationship_id,
                RelationshipType.PARTNERED_WITH.value,
                properties.start_date,
                properties.end_date,
                (
                    properties.partnership_status.value
                    if properties.partnership_status is not None
                    else None
                ),
            ),
        )

    def _save_product_availability_properties(
        self,
        relationship_id: bytes,
        properties: ProductAvailabilityProperties,
        cursor,
    ) -> None:

        cursor.execute(
            """
            INSERT INTO relationship_product_availability_properties (
                relationship_id,
                relationship_type,
                launch_date,
                discontinuation_date,
                availability_status
            )
            VALUES (%s, %s, %s, %s, %s)
            """,
            (
                relationship_id,
                RelationshipType.AVAILABLE_IN.value,
                properties.launch_date,
                properties.discontinuation_date,
                (
                    properties.availability_status.value
                    if properties.availability_status is not None
                    else None
                ),
            ),
        )

    def _save_product_development_properties(
        self,
        relationship_id: bytes,
        properties: ProductDevelopmentProperties,
        cursor,
    ) -> None:

        cursor.execute(
            """
            INSERT INTO relationship_product_development_properties (
                relationship_id,
                relationship_type,
                development_start_date,
                release_date,
                development_status
            )
            VALUES (%s, %s, %s, %s, %s)
            """,
            (
                relationship_id,
                RelationshipType.DEVELOPS.value,
                properties.development_start_date,
                properties.release_date,
                (
                    properties.development_status.value
                    if properties.development_status is not None
                    else None
                ),
            ),
        )

    def _save_product_offering_properties(
        self,
        relationship_id: bytes,
        properties: ProductOfferingProperties,
        cursor,
    ) -> None:

        cursor.execute(
            """
            INSERT INTO relationship_product_offering_properties (
                relationship_id,
                relationship_type,
                launch_date,
                discontinuation_date,
                offering_status
            )
            VALUES (%s, %s, %s, %s, %s)
            """,
            (
                relationship_id,
                RelationshipType.OFFERS.value,
                properties.launch_date,
                properties.discontinuation_date,
                properties.offering_status,
            ),
        )

    def _save_product_technology_properties(
        self,
        relationship_id: bytes,
        properties: ProductTechnologyProperties,
        cursor,
    ) -> None:

        cursor.execute(
            """
            INSERT INTO relationship_product_technology_properties (
                relationship_id,
                relationship_type,
                adoption_date,
                is_core_technology
            )
            VALUES (%s, %s, %s, %s)
            """,
            (
                relationship_id,
                RelationshipType.BUILT_WITH.value,
                properties.adoption_date,
                properties.is_core_technology,
            ),
        )

    def _save_residence_properties(
        self,
        relationship_id: bytes,
        properties: ResidenceProperties,
        cursor,
    ) -> None:

        cursor.execute(
            """
            INSERT INTO relationship_residence_properties (
                relationship_id,
                relationship_type,
                start_date,
                end_date,
                is_current,
                residence_type
            )
            VALUES (%s, %s, %s, %s, %s, %s)
            """,
            (
                relationship_id,
                RelationshipType.LIVES_IN.value,
                properties.start_date,
                properties.end_date,
                properties.is_current,
                properties.residence_type,
            ),
        )

    def _save_technology_adoption_properties(
        self,
        relationship_id: bytes,
        properties: TechnologyAdoptionProperties,
        cursor,
    ) -> None:

        cursor.execute(
            """
            INSERT INTO relationship_technology_adoption_properties (
                relationship_id,
                relationship_type,
                adoption_date
            )
            VALUES (%s, %s, %s)
            """,
            (
                relationship_id,
                RelationshipType.USES.value,
                properties.adoption_date,
            ),
        )

    # ============================================================
    # VALIDATION
    # ============================================================

    def _validate_relationship(
        self,
        relationship: Relationship,
    ) -> None:

        if not isinstance(relationship, Relationship):
            raise TypeError(
                "Expected a Relationship instance."
            )

        relationship_type = relationship.get_type()

        specification = specification_registry.get(
            relationship_type
        )

        if specification is None:
            raise ValueError(
                f"Unsupported relationship type: "
                f"{relationship_type}"
            )

        source = relationship.get_source()
        target = relationship.get_target()

        if source.kind != specification.allowed_source:
            raise ValueError(
                f"Invalid source IdentityKind for "
                f"{relationship_type.value}: "
                f"expected {specification.allowed_source.value}, "
                f"got {source.kind.value}"
            )

        if target.kind != specification.allowed_target:
            raise ValueError(
                f"Invalid target IdentityKind for "
                f"{relationship_type.value}: "
                f"expected {specification.allowed_target.value}, "
                f"got {target.kind.value}"
            )

        expected_properties_type = (
            specification.properties_type
        )

        properties = relationship.get_properties()

        if expected_properties_type is None:

            if properties is not None:
                raise TypeError(
                    f"{relationship_type.value} does not accept "
                    "relationship properties."
                )

        else:

            if not isinstance(
                properties,
                expected_properties_type,
            ):
                raise TypeError(
                    f"{relationship_type.value} requires "
                    f"{expected_properties_type.__name__}."
                )

    def _get_organisation(
        self,
        identity_id: UUID,
        *,
        connection: Connection,
    ) -> Organisation:

        identity = self._organisation_repository.get_by_id(
            identity_id,
            connection=connection,
        )

        if identity is None:
            raise RepositoryIntegrityError(
                f"Relationship references identity "
                f"{identity_id} that is not a persisted Organisation."
            )

        return identity

    def _get_person(
        self,
        identity_id: UUID,
        *,
        connection: Connection,
    ):
        identity = self._person_repository.get_by_id(
            identity_id,
            connection=connection,
        )

        if identity is None:
            raise RepositoryIntegrityError(
                f"Relationship references identity "
                f"{identity_id} that is not a persisted Person."
            )

        return identity


    def _get_place(
        self,
        identity_id: UUID,
        *,
        connection: Connection,
    ):
        identity = self._place_repository.get_by_id(
            identity_id,
            connection=connection,
        )

        if identity is None:
            raise RepositoryIntegrityError(
                f"Relationship references identity "
                f"{identity_id} that is not a persisted Place."
            )

        return identity


    def _get_industry(
        self,
        identity_id: UUID,
        *,
        connection: Connection,
    ):
        identity = self._industry_repository.get_by_id(
            identity_id,
            connection=connection,
        )

        if identity is None:
            raise RepositoryIntegrityError(
                f"Relationship references identity "
                f"{identity_id} that is not a persisted Industry."
            )

        return identity


    def _get_product(
        self,
        identity_id: UUID,
        *,
        connection: Connection,
    ):
        identity = self._product_repository.get_by_id(
            identity_id,
            connection=connection,
        )

        if identity is None:
            raise RepositoryIntegrityError(
                f"Relationship references identity "
                f"{identity_id} that is not a persisted Product."
            )

        return identity


    def _get_technology(
        self,
        identity_id: UUID,
        *,
        connection: Connection,
    ):
        identity = self._technology_repository.get_by_id(
            identity_id,
            connection=connection,
        )

        if identity is None:
            raise RepositoryIntegrityError(
                f"Relationship references identity "
                f"{identity_id} that is not a persisted Technology."
            )

        return identity

    # ============================================================
    # RECONSTRUCTION LOGIC
    # ============================================================

    def _reconstruct_founded(
        self,
        *,
        relationship_id: bytes,
        source_id: UUID,
        target_id: UUID,
        connection: Connection,
    ) -> Relationship:

        source = self._get_person(
            source_id,
            connection=connection,
        )

        target = self._get_organisation(
            target_id,
            connection=connection,
        )

        with connection.cursor() as cursor:
            cursor.execute(
                """
                SELECT
                    founding_date,
                    founder_role,
                    founding_stage
                FROM relationship_founder_properties
                WHERE relationship_id = %s
                AND relationship_type = %s
                """,
                (
                    relationship_id,
                    RelationshipType.FOUNDED.value,
                ),
            )

            record = cursor.fetchone()

        if record is None:
            raise RepositoryIntegrityError(
                "FOUNDED relationship has no corresponding "
                "founder properties record."
            )

        properties = FounderProperties(
            founding_date=record["founding_date"],
            founder_role=record["founder_role"],
            founding_stage=(
                FoundingStage(record["founding_stage"])
                if record["founding_stage"] is not None
                else None
            ),
        )

        return Relationship(
            source=source,
            target=target,
            type=RelationshipType.FOUNDED,
            properties=properties,
            reference=RelationshipReference(
                value=UUID(bytes=relationship_id)
            ),
        )

    def _reconstruct_leads(
        self,
        *,
        relationship_id: bytes,
        source_id: UUID,
        target_id: UUID,
        connection: Connection,
    ) -> Relationship:

        source = self._get_person(
            source_id,
            connection=connection,
        )

        target = self._get_organisation(
            target_id,
            connection=connection,
        )

        with connection.cursor() as cursor:
            cursor.execute(
                """
                SELECT
                    position,
                    start_date,
                    end_date,
                    is_current
                FROM relationship_leadership_properties
                WHERE relationship_id = %s
                AND relationship_type = %s
                """,
                (
                    relationship_id,
                    RelationshipType.LEADS.value,
                ),
            )

            record = cursor.fetchone()

        if record is None:
            raise RepositoryIntegrityError(
                "LEADS relationship has no corresponding "
                "leadership properties record."
            )

        properties = LeadershipProperties(
            position=record["position"],
            start_date=record["start_date"],
            end_date=record["end_date"],
            is_current=(
                bool(record["is_current"])
                if record["is_current"] is not None
                else None
            ),
        )

        return Relationship(
            source=source,
            target=target,
            type=RelationshipType.LEADS,
            properties=properties,
            reference=RelationshipReference(
                value=UUID(bytes=relationship_id)
            ),
        )

    def _reconstruct_owns(
        self,
        *,
        relationship_id: bytes,
        source_id: UUID,
        target_id: UUID,
        connection: Connection,
    ) -> Relationship:

        source = self._get_person(
            source_id,
            connection=connection,
        )

        target = self._get_organisation(
            target_id,
            connection=connection,
        )

        with connection.cursor() as cursor:
            cursor.execute(
                """
                SELECT
                    ownership_percentage,
                    ownership_type,
                    share_class,
                    start_date,
                    end_date,
                    is_current
                FROM relationship_ownership_properties
                WHERE relationship_id = %s
                AND relationship_type = %s
                """,
                (
                    relationship_id,
                    RelationshipType.OWNS.value,
                ),
            )

            record = cursor.fetchone()

        if record is None:
            raise RepositoryIntegrityError(
                "OWNS relationship has no corresponding "
                "ownership properties record."
            )

        properties = OwnershipProperties(
            ownership_percentage=self._decimal_or_none(
                record["ownership_percentage"]
            ),
            ownership_type=(
                OwnershipType(record["ownership_type"])
                if record["ownership_type"] is not None
                else None
            ),
            share_class=record["share_class"],
            start_date=record["start_date"],
            end_date=record["end_date"],
            is_current=(
                bool(record["is_current"])
                if record["is_current"] is not None
                else None
            ),
        )

        return Relationship(
            source=source,
            target=target,
            type=RelationshipType.OWNS,
            properties=properties,
            reference=RelationshipReference(
                value=UUID(bytes=relationship_id)
            ),
        )

    def _reconstruct_born_in(
        self,
        *,
        relationship_id: bytes,
        source_id: UUID,
        target_id: UUID,
        connection: Connection,
    ) -> Relationship:

        source = self._get_person(
            source_id,
            connection=connection,
        )

        target = self._get_place(
            target_id,
            connection=connection,
        )

        return Relationship(
            source=source,
            target=target,
            type=RelationshipType.BORN_IN,
            properties=None,
            reference=RelationshipReference(
                value=UUID(bytes=relationship_id)
            ),
        )   

    def _reconstruct_lives_in(
        self,
        *,
        relationship_id: bytes,
        source_id: UUID,
        target_id: UUID,
        connection: Connection,
    ) -> Relationship:

        source = self._get_person(
            source_id,
            connection=connection,
        )

        target = self._get_place(
            target_id,
            connection=connection,
        )

        with connection.cursor() as cursor:
            cursor.execute(
                """
                SELECT
                    start_date,
                    end_date,
                    is_current,
                    residence_type
                FROM relationship_residence_properties
                WHERE relationship_id = %s
                AND relationship_type = %s
                """,
                (
                    relationship_id,
                    RelationshipType.LIVES_IN.value,
                ),
            )

            record = cursor.fetchone()

        if record is None:
            raise RepositoryIntegrityError(
                "LIVES_IN relationship has no corresponding "
                "residence properties record."
            )

        properties = ResidenceProperties(
            start_date=record["start_date"],
            end_date=record["end_date"],
            is_current=(
                bool(record["is_current"])
                if record["is_current"] is not None
                else None
            ),
            residence_type=record["residence_type"],
        )

        return Relationship(
            source=source,
            target=target,
            type=RelationshipType.LIVES_IN,
            properties=properties,
            reference=RelationshipReference(
                value=UUID(bytes=relationship_id)
            ),
        )

    def _reconstruct_partnered_with(
        self,
        *,
        relationship_id: bytes,
        source_id: UUID,
        target_id: UUID,
        connection: Connection,
    ) -> Relationship:

        source = self._get_organisation(
            source_id,
            connection=connection,
        )

        target = self._get_organisation(
            target_id,
            connection=connection,
        )

        with connection.cursor() as cursor:
            cursor.execute(
                """
                SELECT
                    start_date,
                    end_date,
                    partnership_status
                FROM relationship_partnership_properties
                WHERE relationship_id = %s
                AND relationship_type = %s
                """,
                (
                    relationship_id,
                    RelationshipType.PARTNERED_WITH.value,
                ),
            )

            record = cursor.fetchone()

        if record is None:
            raise RepositoryIntegrityError(
                "PARTNERED_WITH relationship has no corresponding "
                "partnership properties record."
            )

        properties = PartnershipProperties(
            start_date=record["start_date"],
            end_date=record["end_date"],
            partnership_status=(
                PartnershipStatus(record["partnership_status"])
                if record["partnership_status"] is not None
                else None
            ),
        )

        return Relationship(
            source=source,
            target=target,
            type=RelationshipType.PARTNERED_WITH,
            properties=properties,
            reference=RelationshipReference(
                value=UUID(bytes=relationship_id)
            ),
        )

    def _reconstruct_invested_in(
        self,
        *,
        relationship_id: bytes,
        source_id: UUID,
        target_id: UUID,
        connection: Connection,
    ) -> Relationship:

        source = self._get_organisation(
            source_id,
            connection=connection,
        )

        target = self._get_organisation(
            target_id,
            connection=connection,
        )

        with connection.cursor() as cursor:
            cursor.execute(
                """
                SELECT
                    investment_amount,
                    currency,
                    investment_date,
                    funding_round,
                    pre_money_valuation,
                    post_money_valuation,
                    equity_percentage,
                    is_lead_investor
                FROM relationship_investment_properties
                WHERE relationship_id = %s
                AND relationship_type = %s
                """,
                (
                    relationship_id,
                    RelationshipType.INVESTED_IN.value,
                ),
            )

            record = cursor.fetchone()

        if record is None:
            raise RepositoryIntegrityError(
                "INVESTED_IN relationship has no corresponding "
                "investment properties record."
            )

        properties = InvestmentProperties(
            investment_amount=self._decimal_or_none(
                record["investment_amount"]
            ),
            currency=record["currency"],
            investment_date=record["investment_date"],
            funding_round=(
                InvestmentStage(record["funding_round"])
                if record["funding_round"] is not None
                else None
            ),
            pre_money_valuation=self._decimal_or_none(
                record["pre_money_valuation"]
            ),
            post_money_valuation=self._decimal_or_none(
                record["post_money_valuation"]
            ),
            equity_percentage=self._decimal_or_none(
                record["equity_percentage"]
            ),
            is_lead_investor=(
                bool(record["is_lead_investor"])
                if record["is_lead_investor"] is not None
                else None
            ),
        )

        return Relationship(
            source=source,
            target=target,
            type=RelationshipType.INVESTED_IN,
            properties=properties,
            reference=RelationshipReference(
                value=UUID(bytes=relationship_id)
            ),
        )

    def _reconstruct_acquired(
        self,
        *,
        relationship_id: bytes,
        source_id: UUID,
        target_id: UUID,
        connection: Connection,
    ) -> Relationship:

        source = self._get_organisation(
            source_id,
            connection=connection,
        )

        target = self._get_organisation(
            target_id,
            connection=connection,
        )

        with connection.cursor() as cursor:
            cursor.execute(
                """
                SELECT
                    acquisition_date,
                    acquisition_amount,
                    currency,
                    ownership_percentage_acquired,
                    acquisition_type
                FROM relationship_acquisition_properties
                WHERE relationship_id = %s
                AND relationship_type = %s
                """,
                (
                    relationship_id,
                    RelationshipType.ACQUIRED.value,
                ),
            )

            record = cursor.fetchone()

        if record is None:
            raise RepositoryIntegrityError(
                "ACQUIRED relationship has no corresponding "
                "acquisition properties record."
            )

        properties = AcquisitionProperties(
            acquisition_date=record["acquisition_date"],
            acquisition_amount=self._decimal_or_none(
                record["acquisition_amount"]
            ),
            currency=record["currency"],
            ownership_percentage_acquired=self._decimal_or_none(
                record["ownership_percentage_acquired"]
            ),
            acquisition_type=(
                AcquisitionType(record["acquisition_type"])
                if record["acquisition_type"] is not None
                else None
            ),
        )

        return Relationship(
            source=source,
            target=target,
            type=RelationshipType.ACQUIRED,
            properties=properties,
            reference=RelationshipReference(
                value=UUID(bytes=relationship_id)
            ),
        )

    def _reconstruct_headquartered_in(
        self,
        *,
        relationship_id: bytes,
        source_id: UUID,
        target_id: UUID,
        connection: Connection,
    ) -> Relationship:

        source = self._get_organisation(
            source_id,
            connection=connection,
        )

        target = self._get_place(
            target_id,
            connection=connection,
        )

        with connection.cursor() as cursor:
            cursor.execute(
                """
                SELECT
                    headquarters_level,
                    headquarters_function,
                    start_date,
                    end_date,
                    is_current
                FROM relationship_headquarters_properties
                WHERE relationship_id = %s
                AND relationship_type = %s
                """,
                (
                    relationship_id,
                    RelationshipType.HEADQUARTERED_IN.value,
                ),
            )

            record = cursor.fetchone()

        if record is None:
            raise RepositoryIntegrityError(
                "HEADQUARTERED_IN relationship has no corresponding "
                "headquarters properties record."
            )

        properties = HeadquartersProperties(
            headquarters_level=(
                HeadquartersLevel(record["headquarters_level"])
                if record["headquarters_level"] is not None
                else None
            ),
            headquarters_function=(
                HeadquartersFunction(record["headquarters_function"])
                if record["headquarters_function"] is not None
                else None
            ),
            start_date=record["start_date"],
            end_date=record["end_date"],
            is_current=(
                bool(record["is_current"])
                if record["is_current"] is not None
                else None
            ),
        )

        return Relationship(
            source=source,
            target=target,
            type=RelationshipType.HEADQUARTERED_IN,
            properties=properties,
            reference=RelationshipReference(
                value=UUID(bytes=relationship_id)
            ),
        )

    def _reconstruct_operates_in(
        self,
        *,
        relationship_id: bytes,
        source_id: UUID,
        target_id: UUID,
        connection: Connection,
    ) -> Relationship:

        source = self._get_organisation(
            source_id,
            connection=connection,
        )

        target = self._get_place(
            target_id,
            connection=connection,
        )

        with connection.cursor() as cursor:
            cursor.execute(
                """
                SELECT
                    entry_date,
                    exit_date,
                    is_current,
                    operating_status
                FROM relationship_market_presence_properties
                WHERE relationship_id = %s
                AND relationship_type = %s
                """,
                (
                    relationship_id,
                    RelationshipType.OPERATES_IN.value,
                ),
            )

            record = cursor.fetchone()

        if record is None:
            raise RepositoryIntegrityError(
                "OPERATES_IN relationship has no corresponding "
                "market presence properties record."
            )

        properties = MarketPresenceProperties(
            entry_date=record["entry_date"],
            exit_date=record["exit_date"],
            is_current=(
                bool(record["is_current"])
                if record["is_current"] is not None
                else None
            ),
            operating_status=(
                OperatingStatus(record["operating_status"])
                if record["operating_status"] is not None
                else None
            ),
        )

        return Relationship(
            source=source,
            target=target,
            type=RelationshipType.OPERATES_IN,
            properties=properties,
            reference=RelationshipReference(
                value=UUID(bytes=relationship_id)
            ),
        )

    def _reconstruct_operates_in_industry(
        self,
        *,
        relationship_id: bytes,
        source_id: UUID,
        target_id: UUID,
        connection: Connection,
    ) -> Relationship:

        source = self._get_organisation(
            source_id,
            connection=connection,
        )

        target = self._get_industry(
            target_id,
            connection=connection,
        )

        with connection.cursor() as cursor:
            cursor.execute(
                """
                SELECT
                    start_date,
                    end_date,
                    is_primary_industry
                FROM relationship_industry_participation_properties
                WHERE relationship_id = %s
                AND relationship_type = %s
                """,
                (
                    relationship_id,
                    RelationshipType.OPERATES_IN_INDUSTRY.value,
                ),
            )

            record = cursor.fetchone()

        if record is None:
            raise RepositoryIntegrityError(
                "OPERATES_IN_INDUSTRY relationship has no corresponding "
                "industry participation properties record."
            )

        properties = IndustryParticipationProperties(
            start_date=record["start_date"],
            end_date=record["end_date"],
            is_primary_industry=(
                bool(record["is_primary_industry"])
                if record["is_primary_industry"] is not None
                else None
            ),
        )

        return Relationship(
            source=source,
            target=target,
            type=RelationshipType.OPERATES_IN_INDUSTRY,
            properties=properties,
            reference=RelationshipReference(
                value=UUID(bytes=relationship_id)
            ),
        )

    # OFFERS
    def _reconstruct_offers(
        self,
        *,
        relationship_id: bytes,
        source_id: UUID,
        target_id: UUID,
        connection: Connection,
    ) -> Relationship:

        source = self._get_organisation(
            source_id,
            connection=connection,
        )

        target = self._get_product(
            target_id,
            connection=connection,
        )

        with connection.cursor() as cursor:
            cursor.execute(
                """
                SELECT
                    launch_date,
                    discontinuation_date,
                    offering_status
                FROM relationship_product_offering_properties
                WHERE relationship_id = %s
                AND relationship_type = %s
                """,
                (
                    relationship_id,
                    RelationshipType.OFFERS.value,
                ),
            )

            record = cursor.fetchone()

        if record is None:
            raise RepositoryIntegrityError(
                "OFFERS relationship has no corresponding "
                "product offering properties record."
            )

        properties = ProductOfferingProperties(
            launch_date=record["launch_date"],
            discontinuation_date=record["discontinuation_date"],
            offering_status=(
                OfferingStatus(record["offering_status"])
                if record["offering_status"] is not None
                else None
            ),
        )

        return Relationship(
            source=source,
            target=target,
            type=RelationshipType.OFFERS,
            properties=properties,
            reference=RelationshipReference(
                value=UUID(bytes=relationship_id)
            ),
        )

    # DEVELOPS

    def _reconstruct_develops(
        self,
        *,
        relationship_id: bytes,
        source_id: UUID,
        target_id: UUID,
        connection: Connection,
    ) -> Relationship:

        source = self._get_organisation(
            source_id,
            connection=connection,
        )

        target = self._get_product(
            target_id,
            connection=connection,
        )

        with connection.cursor() as cursor:
            cursor.execute(
                """
                SELECT
                    development_start_date,
                    release_date,
                    development_status
                FROM relationship_product_development_properties
                WHERE relationship_id = %s
                AND relationship_type = %s
                """,
                (
                    relationship_id,
                    RelationshipType.DEVELOPS.value,
                ),
            )

            record = cursor.fetchone()

        if record is None:
            raise RepositoryIntegrityError(
                "DEVELOPS relationship has no corresponding "
                "product development properties record."
            )

        properties = ProductDevelopmentProperties(
            development_start_date=record["development_start_date"],
            release_date=record["release_date"],
            development_status=(
                DevelopmentStatus(record["development_status"])
                if record["development_status"] is not None
                else None
            ),
        )

        return Relationship(
            source=source,
            target=target,
            type=RelationshipType.DEVELOPS,
            properties=properties,
            reference=RelationshipReference(
                value=UUID(bytes=relationship_id)
            ),
        )

    # USES
    def _reconstruct_uses(
        self,
        *,
        relationship_id: bytes,
        source_id: UUID,
        target_id: UUID,
        connection: Connection,
    ) -> Relationship:

        source = self._get_organisation(
            source_id,
            connection=connection,
        )

        target = self._get_technology(
            target_id,
            connection=connection,
        )

        with connection.cursor() as cursor:
            cursor.execute(
                """
                SELECT
                    adoption_date
                FROM relationship_technology_adoption_properties
                WHERE relationship_id = %s
                AND relationship_type = %s
                """,
                (
                    relationship_id,
                    RelationshipType.USES.value,
                ),
            )

            record = cursor.fetchone()

        if record is None:
            raise RepositoryIntegrityError(
                "USES relationship has no corresponding "
                "technology adoption properties record."
            )

        properties = TechnologyAdoptionProperties(
            adoption_date=record["adoption_date"],
        )

        return Relationship(
            source=source,
            target=target,
            type=RelationshipType.USES,
            properties=properties,
            reference=RelationshipReference(
                value=UUID(bytes=relationship_id)
            ),
        )

    # BUILT_WITH

    def _reconstruct_built_with(
        self,
        *,
        relationship_id: bytes,
        source_id: UUID,
        target_id: UUID,
        connection: Connection,
    ) -> Relationship:

        source = self._get_product(
            source_id,
            connection=connection,
        )

        target = self._get_technology(
            target_id,
            connection=connection,
        )

        with connection.cursor() as cursor:
            cursor.execute(
                """
                SELECT
                    adoption_date,
                    is_core_technology
                FROM relationship_product_technology_properties
                WHERE relationship_id = %s
                AND relationship_type = %s
                """,
                (
                    relationship_id,
                    RelationshipType.BUILT_WITH.value,
                ),
            )

            record = cursor.fetchone()

        if record is None:
            raise RepositoryIntegrityError(
                "BUILT_WITH relationship has no corresponding "
                "product technology properties record."
            )

        properties = ProductTechnologyProperties(
            adoption_date=record["adoption_date"],
            is_core_technology=(
                bool(record["is_core_technology"])
                if record["is_core_technology"] is not None
                else None
            ),
        )

        return Relationship(
            source=source,
            target=target,
            type=RelationshipType.BUILT_WITH,
            properties=properties,
            reference=RelationshipReference(
                value=UUID(bytes=relationship_id)
            ),
        )

    # AVAILABLE_IN

    def _reconstruct_available_in(
        self,
        *,
        relationship_id: bytes,
        source_id: UUID,
        target_id: UUID,
        connection: Connection,
    ) -> Relationship:

        source = self._get_product(
            source_id,
            connection=connection,
        )

        target = self._get_place(
            target_id,
            connection=connection,
        )

        with connection.cursor() as cursor:
            cursor.execute(
                """
                SELECT
                    launch_date,
                    discontinuation_date,
                    availability_status
                FROM relationship_product_availability_properties
                WHERE relationship_id = %s
                AND relationship_type = %s
                """,
                (
                    relationship_id,
                    RelationshipType.AVAILABLE_IN.value,
                ),
            )

            record = cursor.fetchone()

        if record is None:
            raise RepositoryIntegrityError(
                "AVAILABLE_IN relationship has no corresponding "
                "product availability properties record."
            )

        properties = ProductAvailabilityProperties(
            launch_date=record["launch_date"],
            discontinuation_date=record["discontinuation_date"],
            availability_status=(
                AvailabilityStatus(record["availability_status"])
                if record["availability_status"] is not None
                else None
            ),
        )

        return Relationship(
            source=source,
            target=target,
            type=RelationshipType.AVAILABLE_IN,
            properties=properties,
            reference=RelationshipReference(
                value=UUID(bytes=relationship_id)
            ),
        )

    # LOCATED IN

    def _reconstruct_located_in(
        self,
        *,
        relationship_id: bytes,
        source_id: UUID,
        target_id: UUID,
        connection: Connection,
    ) -> Relationship:

        source = self._get_place(
            source_id,
            connection=connection,
        )

        target = self._get_place(
            target_id,
            connection=connection,
        )

        return Relationship(
            source=source,
            target=target,
            type=RelationshipType.LOCATED_IN,
            properties=None,
            reference=RelationshipReference(
                value=UUID(bytes=relationship_id)
            ),
        )

    # PART OF

    def _reconstruct_part_of(
        self,
        *,
        relationship_id: bytes,
        source_id: UUID,
        target_id: UUID,
        connection: Connection,
    ) -> Relationship:

        source = self._get_place(
            source_id,
            connection=connection,
        )

        target = self._get_place(
            target_id,
            connection=connection,
        )

        return Relationship(
            source=source,
            target=target,
            type=RelationshipType.PART_OF,
            properties=None,
            reference=RelationshipReference(
                value=UUID(bytes=relationship_id)
            ),
        )

    # ============================================================
    # HELPERS
    # ============================================================

    @staticmethod
    def _assert_no_properties(
        relationship_type: RelationshipType,
        properties,
    ) -> None:

        if properties is not None:
            raise TypeError(
                f"{relationship_type.value} does not accept "
                "relationship properties."
            )

    @staticmethod
    def _decimal_or_none(
        value,
    ) -> Decimal | None:

        if value is None:
            return None

        if isinstance(value, Decimal):
            return value

        return Decimal(value)
