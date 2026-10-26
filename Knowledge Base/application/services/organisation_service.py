from uuid import UUID

from domain_models.Identity_model.identity import IdentityRepresentations
from domain_models.Identity_model.Organisation_model.organisation import Organisation
from domain_models.Identity_model.Organisation_model.organisation_classification import (
    OrganisationClassification,
)

from domain_models.Identity_model.Organisation_model.classification_specific_domain_model.startup.start_up import (
    Startup,
    StartupBusinessModels,
    StartupStages,
)

from domain_models.Identity_model.Organisation_model.classification_specific_domain_model.investor.investor import (
    Investor,
    InvestmentTypes,
    InvestmentStage,
)
from repositories.organisation_repository import OrganisationRepository
from infrastructure.database.connection import DatabaseManager
from domain_models.Identity_model.Organisation_model.classification_specific_domain_model.accelerator.accelerator import (
    Accelerator,
)
from domain_models.Identity_model.Organisation_model.classification_specific_domain_model.accelerator.accelerator_programme import (
    AcceleratorProgramme,
)
from domain_models.Identity_model.identity import IdentityReference
from application.services.create_orchestration import resolve_and_create_identity
from application.services.identity_resolution_service import IdentityResolutionService
from application.resolution.create_result import CreateResult
from application.resolution.identity.contracts import IdentityResolutionResult


class OrganisationService:
    def __init__(
        self,
        *,
        organisation_repository: OrganisationRepository,
        database_manager: DatabaseManager,
        identity_resolution_service: IdentityResolutionService,
    ):
        self._organisation_repository = organisation_repository
        self._database_manager = database_manager
        self._identity_resolution_service = identity_resolution_service

    def create_startup(
        self,
        *,
        canonical_name: str,
        founding_year: int,
        stage: StartupStages,
        business_model: StartupBusinessModels,
        aliases: set[str] | None = None,
        allow_possible_duplicate: bool = False,
    ) -> CreateResult[Organisation, IdentityResolutionResult]:
        """
        Create and persist a complete Startup Organisation.

        Returns the persisted Organisation aggregate, including its
        generated IdentityReference and attached Startup model.
        """

        # 1. Construct the classification-specific Startup model.
        startup_model = Startup(
            founding_year=founding_year,
            stage=stage,
            business_model=business_model,
        )

        # 2. Construct the Organisation Identity.
        organisation = Organisation(
            representations=IdentityRepresentations(
                canonical_name=canonical_name,
                aliases=set(aliases or ()),
            ),
            classifications={OrganisationClassification.STARTUP},
        )

        # 3. Attach the model to its registered classification.
        organisation.add_classification_model(
            OrganisationClassification.STARTUP,
            startup_model,
        )

        # 4. Persist the complete aggregate atomically.
        return self._persist_organisation(
            organisation,
            allow_possible_duplicate=allow_possible_duplicate,
        )

    def create_investor(
        self,
        *,
        canonical_name: str,
        investor_type: InvestmentTypes,
        investment_stage: InvestmentStage,
        aliases: set[str] | None = None,
        allow_possible_duplicate: bool = False,
    ) -> CreateResult[Organisation, IdentityResolutionResult]:
        """
        Create and persist a complete Investor Organisation.

        Returns the persisted Organisation aggregate, including its
        generated IdentityReference and attached Investor model.
        """

        # 1. Construct the classification-specific Investor model.
        investor_model = Investor(
            investor_type=investor_type,
            investment_stage=investment_stage,
        )

        # 2. Construct the Organisation Identity.
        organisation = Organisation(
            representations=IdentityRepresentations(
                canonical_name=canonical_name,
                aliases=set(aliases or ()),
            ),
            classifications={OrganisationClassification.INVESTOR},
        )

        # 3. Attach the model to its registered classification.
        organisation.add_classification_model(
            OrganisationClassification.INVESTOR,
            investor_model,
        )

        # 4. Persist the complete aggregate atomically.
        return self._persist_organisation(
            organisation,
            allow_possible_duplicate=allow_possible_duplicate,
        )

    def _persist_organisation(
        self,
        organisation: Organisation,
        *,
        allow_possible_duplicate: bool = False,
    ) -> CreateResult[Organisation, IdentityResolutionResult]:
        """
        Persist a complete Organisation aggregate atomically.

        The repository performs persistence while this service owns
        the transaction boundary.
        """

        return resolve_and_create_identity(
            organisation,
            repository=self._organisation_repository,
            database_manager=self._database_manager,
            resolver=self._identity_resolution_service,
            allow_possible_duplicate=allow_possible_duplicate,
        )

    def create_accelerator(
        self,
        *,
        canonical_name: str,
        programmes: list[AcceleratorProgramme] | None = None,
        aliases: set[str] | None = None,
        allow_possible_duplicate: bool = False,
    ) -> CreateResult[Organisation, IdentityResolutionResult]:
        """
        Create and persist a complete Accelerator Organisation.

        Returns the persisted Organisation aggregate, including its
        generated IdentityReference and attached Accelerator model.
        """

        # 1. Construct the classification-specific Accelerator model.
        accelerator_model = Accelerator()

        if programmes:
            accelerator_model.programmes.extend(programmes)

        # 2. Construct the Organisation Identity.
        organisation = Organisation(
            representations=IdentityRepresentations(
                canonical_name=canonical_name,
                aliases=set(aliases or ()),
            ),
            classifications={
                OrganisationClassification.ACCELERATOR
            },
        )

        # 3. Attach the model to its registered classification.
        organisation.add_classification_model(
            OrganisationClassification.ACCELERATOR,
            accelerator_model,
        )

        # 4. Persist the complete aggregate atomically.
        return self._persist_organisation(
            organisation,
            allow_possible_duplicate=allow_possible_duplicate,
        )

    def create_incubator(
        self,
        *,
        canonical_name: str,
        aliases: set[str] | None = None,
        allow_possible_duplicate: bool = False,
    ) -> CreateResult[Organisation, IdentityResolutionResult]:
        """
        Create and persist an Incubator Organisation.

        Incubator currently has no classification-specific domain
        model or persistence data.
        """

        # 1. Construct the Organisation Identity.
        organisation = Organisation(
            representations=IdentityRepresentations(
                canonical_name=canonical_name,
                aliases=set(aliases or ()),
            ),
            classifications={
                OrganisationClassification.INCUBATOR
            },
        )

        # 2. No classification-specific model is attached because
        # Incubator currently has no additional domain model.

        # 3. Persist the complete aggregate atomically.
        return self._persist_organisation(
            organisation,
            allow_possible_duplicate=allow_possible_duplicate,
        )

    def get_organisation(
        self,
        identity_id: UUID | IdentityReference,
    ) -> Organisation | None:
        """
        Retrieve and reconstruct an Organisation by its identity ID.

        Returns None if the identity does not exist or is not
        an Organisation.
        """

        with self._database_manager.transaction() as connection:
            return self._organisation_repository.get_by_id(
                identity_id,
                connection=connection,
            )
