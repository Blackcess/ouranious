from decimal import Decimal
from uuid import UUID
from pymysql.connections import Connection
from domain_models.Identity_model.identity import (
    IdentityKind,
    IdentityReference,
    IdentityRepresentations,
    LifecycleState,
)
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
from domain_models.Identity_model.Organisation_model.classification_specific_domain_model.accelerator.accelerator import (
    Accelerator,
)
from domain_models.Identity_model.Organisation_model.classification_specific_domain_model.accelerator.accelerator_programme import (
    AcceleratorProgramme,
    InvestmentTerms,
)
from utils.representations import Money, Duration
from repositories.utils.errors import RepositoryIntegrityError
from repositories.utils.candidate_page import CandidatePage
from repositories.utils.identity_candidate_search import find_identity_candidate_ids






class OrganisationRepository:

    def find_candidates(
        self,
        identity: Organisation,
        *,
        exclude_reference: UUID | IdentityReference | None = None,
        include_retired: bool = False,
        limit: int = 100,
        connection: Connection,
    ) -> CandidatePage[Organisation]:
        """Return bounded same-kind candidates for exact/normalized names."""

        if not isinstance(identity, Organisation):
            raise TypeError("OrganisationRepository requires a Organisation identity.")

        id_page = find_identity_candidate_ids(
            kind=IdentityKind.ORGANISATION,
            canonical_name=identity.representations.canonical_name,
            aliases=identity.representations.aliases,
            exclude_reference=exclude_reference,
            include_retired=include_retired,
            limit=limit,
            connection=connection,
        )
        candidates = tuple(
            candidate
            for identity_id in id_page.items
            if (
                candidate := self.get_by_id(
                    UUID(bytes=identity_id),
                    connection=connection,
                )
            ) is not None
        )
        return CandidatePage(candidates, truncated=id_page.truncated)

    def save(
        self,
        organisation: Organisation,
        *,
        connection: Connection,
    ) -> None:
        """
        Persist an integrated Organisation.

        The caller owns the transaction.
        This method does not commit or roll back.
        """

        self._validate_organisation(organisation)

        identity_id = organisation.reference.value.bytes

        with connection.cursor() as cursor:

            # 1. Persist base Identity
            cursor.execute(
                """
                INSERT INTO identities (
                    identity_id,
                    kind,
                    lifecycle_state,
                    canonical_name
                )
                VALUES (%s, %s, %s, %s)
                """,
                (
                    identity_id,
                    organisation.kind.value,
                    organisation.lifecycle_state.value,
                    organisation.representations.canonical_name,
                ),
            )

            # 2. Persist aliases
            aliases = organisation.representations.aliases

            if aliases:
                cursor.executemany(
                    """
                    INSERT INTO identity_aliases (
                        identity_id,
                        alias
                    )
                    VALUES (%s, %s)
                    """,
                    [
                        (identity_id, alias)
                        for alias in aliases
                    ],
                )

            # 3. Persist Organisation subtype
            cursor.execute(
                """
                INSERT INTO organisations (
                    identity_id
                )
                VALUES (%s)
                """,
                (identity_id,),
            )

            # 4. Persist classifications
            classifications = organisation.get_classifications()

            cursor.executemany(
                """
                INSERT INTO organisation_classifications (
                    organisation_id,
                    classification
                )
                VALUES (%s, %s)
                """,
                [
                    (identity_id, classification.value)
                    for classification in classifications
                ],
            )

            # 5. Persist classification-specific models
            for classification in classifications:

                model = organisation.get_classification_model(
                    classification
                )

                if classification == OrganisationClassification.STARTUP:
                    self._save_startup_model(
                        identity_id,
                        model,
                        cursor,
                    )

                elif classification == OrganisationClassification.INVESTOR:
                    self._save_investor_model(
                        identity_id,
                        model,
                        cursor,
                    )

                elif classification == OrganisationClassification.ACCELERATOR:
                    self._save_accelerator_model(
                        identity_id,
                        model,
                        cursor,
                    )

                elif classification == OrganisationClassification.INCUBATOR:
                    # Incubator currently has no classification specific model to persist.
                    pass

                else:
                    raise NotImplementedError(
                        f"Persistence for {classification.value} "
                        "is not implemented yet."
                    )

    def get_by_id(
        self,
        identity_id: UUID | IdentityReference,
        *,
        connection: Connection,
    ) -> Organisation | None:
        """
        Retrieve and reconstruct an Organisation.

        Returns None if the identity does not exist
        or is not an Organisation.
        """

        if isinstance(identity_id, IdentityReference):
            identity_id = identity_id.value

        if not isinstance(identity_id, UUID):
            raise TypeError("identity_id must be UUID or IdentityReference")

        binary_id = identity_id.bytes

        with connection.cursor() as cursor:

            # 1. Retrieve base Identity
            cursor.execute(
                """
                SELECT
                    identity_id,
                    kind,
                    lifecycle_state,
                    canonical_name
                FROM identities
                WHERE identity_id = %s
                """,
                (binary_id,),
            )

            identity_record = cursor.fetchone()

            if identity_record is None:
                return None

            if identity_record["kind"] != IdentityKind.ORGANISATION.value:
                return None

            # 2. Retrieve aliases
            cursor.execute(
                """
                SELECT alias
                FROM identity_aliases
                WHERE identity_id = %s
                """,
                (binary_id,),
            )

            aliases = {
                row["alias"]
                for row in cursor.fetchall()
            }

            # 3. Retrieve Organisation subtype
            cursor.execute(
                """
                SELECT identity_id
                FROM organisations
                WHERE identity_id = %s
                """,
                (binary_id,),
            )

            organisation_record = cursor.fetchone()

            if organisation_record is None:
                raise RepositoryIntegrityError(
                    "Identity is marked as an Organisation "
                    "but has no corresponding organisations record."
                )

            # 4. Retrieve classifications
            cursor.execute(
                """
                SELECT classification
                FROM organisation_classifications
                WHERE organisation_id = %s
                """,
                (binary_id,),
            )

            classification_records = cursor.fetchall()

            classifications = {
                OrganisationClassification(row["classification"])
                for row in classification_records
            }

            # 5. Reconstruct Organisation
            organisation = Organisation(
                representations=IdentityRepresentations(
                    canonical_name=identity_record["canonical_name"],
                    aliases=aliases,
                ),
                classifications=classifications,
                reference=IdentityReference(
                    value=UUID(bytes=identity_record["identity_id"])
                ),
                lifecycle_state=LifecycleState(
                    identity_record["lifecycle_state"]
                ),
            )

            # 6. Reconstruct classification-specific models
            for classification in classifications:

                if classification == OrganisationClassification.STARTUP:

                    startup_model = self._get_startup_model(
                        binary_id,
                        cursor,
                    )

                    if startup_model is None:
                        raise RepositoryIntegrityError(
                            "Organisation has STARTUP classification "
                            "but no corresponding startup_models record."
                        )

                    organisation.add_classification_model(
                        classification,
                        startup_model,
                    )

                elif classification == OrganisationClassification.INVESTOR:

                    investor_model = self._get_investor_model(
                        binary_id,
                        cursor,
                    )

                    if investor_model is None:
                        raise RepositoryIntegrityError(
                            "Organisation has INVESTOR classification "
                            "but no corresponding investor_models record."
                        )

                    organisation.add_classification_model(
                        classification,
                        investor_model,
                    )

                elif classification == OrganisationClassification.ACCELERATOR:

                    accelerator_model = self._get_accelerator_model(
                        binary_id,
                        cursor,
                    )

                    if accelerator_model is None:
                        raise RepositoryIntegrityError(
                            "Organisation has ACCELERATOR classification "
                            "but no corresponding Accelerator model."
                        )

                    organisation.add_classification_model(
                        classification,
                        accelerator_model,
                    )

                elif classification == OrganisationClassification.INCUBATOR:

                    # Incubator currently has no classification-specific
                    # domain model or persistence data.
                    pass

                else:
                    raise NotImplementedError(
                        f"Reconstruction for {classification.value} "
                        "is not implemented yet."
                    )

            return organisation

    def _save_startup_model(
        self,
        organisation_id: bytes,
        model: Startup,
        cursor,
    ) -> None:

        cursor.execute(
            """
            INSERT INTO startup_models (
                organisation_id,
                classification,
                founding_year,
                stage,
                business_model
            )
            VALUES (%s, %s, %s, %s, %s)
            """,
            (
                organisation_id,
                OrganisationClassification.STARTUP.value,
                model.founding_year,
                model.stage.value,
                model.business_model.value,
            ),
        )

    def _get_startup_model(
        self,
        organisation_id: bytes,
        cursor,
    ) -> Startup | None:

        cursor.execute(
            """
            SELECT
                founding_year,
                stage,
                business_model
            FROM startup_models
            WHERE organisation_id = %s
            """,
            (organisation_id,),
        )

        record = cursor.fetchone()

        if record is None:
            return None

        return Startup(
            founding_year=record["founding_year"],
            stage=StartupStages(record["stage"]),
            business_model=StartupBusinessModels(
                record["business_model"]
            ),
        )

    def _save_investor_model(
        self,
        organisation_id: bytes,
        model: Investor,
        cursor,
    ) -> None:

        cursor.execute(
            """
            INSERT INTO investor_models (
                organisation_id,
                classification,
                investor_type,
                investment_stage
            )
            VALUES (%s, %s, %s, %s)
            """,
            (
                organisation_id,
                OrganisationClassification.INVESTOR.value,
                model.get_investor_type().value,
                model.get_investor_stage().value,
            ),
        )

    def _get_investor_model(
        self,
        organisation_id: bytes,
        cursor,
    ) -> Investor | None:

        cursor.execute(
            """
            SELECT
                investor_type,
                investment_stage
            FROM investor_models
            WHERE organisation_id = %s
            """,
            (organisation_id,),
        )

        record = cursor.fetchone()

        if record is None:
            return None

        return Investor(
            investor_type=InvestmentTypes(
                record["investor_type"]
            ),
            investment_stage=InvestmentStage(
                record["investment_stage"]
            ),
        )

    def _save_accelerator_model(
        self,
        organisation_id: bytes,
        model: Accelerator,
        cursor,
    ) -> None:

        for programme in model.programmes:

            duration = programme.duration
            investment_terms = programme.investment_terms
            money = investment_terms.money

            cursor.execute(
                """
                INSERT INTO accelerator_programmes (
                    accelerator_id,
                    classification,
                    programme_name,
                    duration_value,
                    duration_unit,
                    duration_start_date,
                    duration_end_date,
                    investment_amount,
                    investment_currency,
                    equity_percentage
                )
                VALUES (
                    %s, %s, %s, %s, %s,
                    %s, %s, %s, %s, %s
                )
                """,
                (
                    organisation_id,
                    OrganisationClassification.ACCELERATOR.value,
                    programme.name,
                    duration.value,
                    duration.unit,
                    duration.start_date,
                    duration.end_date,
                    money.amount,
                    money.currency,
                    investment_terms.equity_percentage,
                ),
            )

    def _get_accelerator_model(
        self,
        organisation_id: bytes,
        cursor,
    ) -> Accelerator | None:

        cursor.execute(
            """
            SELECT
                programme_name,
                duration_value,
                duration_unit,
                duration_start_date,
                duration_end_date,
                investment_amount,
                investment_currency,
                equity_percentage
            FROM accelerator_programmes
            WHERE accelerator_id = %s
            ORDER BY programme_id
            """,
            (organisation_id,),
        )

        records = cursor.fetchall()

        if not records:
            return None

        accelerator = Accelerator()

        for record in records:

            money = Money(
                amount=record["investment_amount"],
                currency=record["investment_currency"],
            )

            duration = Duration(
                value=Decimal(record["duration_value"]),
                unit=record["duration_unit"],
                start_date=record["duration_start_date"],
                end_date=record["duration_end_date"],
            )

            investment_terms = InvestmentTerms(
                money=money,
                equity_percentage=Decimal(record["equity_percentage"]),
            )

            programme = AcceleratorProgramme(
                name=record["programme_name"],
                duration=duration,
                investment_terms=investment_terms,
            )

            accelerator.programmes.append(programme)

        return accelerator

    def _validate_organisation(
        self,
        organisation: Organisation,
    ) -> None:
        """
        Validate persistence requirements before issuing SQL.
        """

        if not isinstance(organisation, Organisation):
            raise TypeError("Expected an Organisation instance.")

        if organisation.kind != IdentityKind.ORGANISATION:
            raise ValueError("Invalid Organisation identity kind.")

        representations = organisation.representations

        if len(representations.canonical_name) > 255:
            raise ValueError(
                "Canonical name exceeds the database limit of 255 characters."
            )

        for alias in representations.aliases:
            if not isinstance(alias, str):
                raise TypeError("Identity aliases must be strings.")

            if len(alias) > 255:
                raise ValueError(
                    "Identity alias exceeds 255 characters."
                )

        classifications = organisation.get_classifications()

        if not classifications:
            raise ValueError(
                "An Organisation must have at least one classification."
            )

        for classification in classifications:

            model = organisation.get_classification_model(classification)

            if model is None and classification != OrganisationClassification.INCUBATOR:
                raise ValueError(
                    f"Missing classification model for {classification.value}."
                )

            if classification == OrganisationClassification.STARTUP:

                if not isinstance(model, Startup):
                    raise TypeError(
                        "STARTUP classification requires a Startup model."
                    )

                if not isinstance(model.founding_year, int):
                    raise TypeError("founding_year must be an integer.")

                if not 0 <= model.founding_year <= 65535:
                    raise ValueError(
                        "founding_year is outside the MySQL SMALLINT UNSIGNED range."
                    )

                if not isinstance(model.stage, StartupStages):
                    raise TypeError("Invalid Startup stage.")

                if not isinstance(
                    model.business_model,
                    StartupBusinessModels,
                ):
                    raise TypeError("Invalid Startup business model.")

            elif classification == OrganisationClassification.INVESTOR:

                if not isinstance(model, Investor):
                    raise TypeError(
                        "INVESTOR classification requires an Investor model."
                    )

                if not isinstance(
                    model.get_investor_type(),
                    InvestmentTypes,
                ):
                    raise TypeError("Invalid Investor type.")

                if not isinstance(
                    model.get_investor_stage(),
                    InvestmentStage,
                ):
                    raise TypeError("Invalid Investor investment stage.")

            elif classification == OrganisationClassification.ACCELERATOR:

                if not isinstance(model, Accelerator):
                    raise TypeError(
                        "ACCELERATOR classification requires an Accelerator model."
                    )

                if not isinstance(model.programmes, list):
                    raise TypeError(
                        "Accelerator programmes must be stored in a list."
                    )

                for programme in model.programmes:

                    if not isinstance(programme, AcceleratorProgramme):
                        raise TypeError(
                            "Accelerator programmes must be "
                            "AcceleratorProgramme instances."
                        )

                    if not isinstance(programme.name, str):
                        raise TypeError(
                            "Accelerator programme name must be a string."
                        )

                    if len(programme.name) > 255:
                        raise ValueError(
                            "Accelerator programme name exceeds "
                            "the database limit of 255 characters."
                        )

                    if not isinstance(programme.duration, Duration):
                        raise TypeError(
                            "Accelerator programme duration must be a Duration object."
                        )

                    if programme.duration.value is not None:
                        if len(str(programme.duration.value)) > 50:
                            raise ValueError(
                                "Accelerator programme duration value exceeds "
                                "the database limit of 50 characters."
                            )

                    if programme.duration.unit is not None:
                        if not isinstance(programme.duration.unit, str):
                            raise TypeError(
                                "Duration unit must be a string."
                            )

                        if len(programme.duration.unit) > 30:
                            raise ValueError(
                                "Duration unit exceeds the database limit of 30 characters."
                            )

                    if not isinstance(
                        programme.investment_terms,
                        InvestmentTerms,
                    ):
                        raise TypeError(
                            "Accelerator programme investment terms must "
                            "be an InvestmentTerms object."
                        )

                    if not isinstance(
                        programme.investment_terms.money,
                        Money,
                    ):
                        raise TypeError(
                            "Investment terms money must be a Money object."
                        )

                    if not isinstance(
                        programme.investment_terms.equity_percentage,
                        Decimal,
                    ):
                        raise TypeError(
                            "Equity percentage must be Decimal."
                        )

                    if not programme.investment_terms.equity_percentage.is_finite():
                        raise ValueError(
                            "Equity percentage must be finite."
                        )

                    if not (
                        Decimal("0")
                        <= programme.investment_terms.equity_percentage
                        <= Decimal("100")
                    ):
                        raise ValueError(
                            "Equity percentage must be between 0 and 100."
                        )
            elif classification == OrganisationClassification.INCUBATOR:
                # Incubator currently has no classification-specific model to validate.
                pass

            else:
                raise NotImplementedError(
                    f"Persistence for {classification.value} "
                    "is not implemented yet."
                )
