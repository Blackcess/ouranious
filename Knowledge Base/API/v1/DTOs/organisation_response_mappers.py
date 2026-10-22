from domain_models.Identity_model.Organisation_model.organisation import Organisation
from domain_models.Identity_model.Organisation_model.organisation_classification import (
    OrganisationClassification,
)
from domain_models.Identity_model.Organisation_model.classification_specific_domain_model.startup.start_up import Startup
from domain_models.Identity_model.Organisation_model.classification_specific_domain_model.accelerator.accelerator import Accelerator
from API.v1.DTOs.organisations_dtos import (
    InvestorResponse,
    IncubatorResponse, 
    AcceleratorResponse, 
    StartupResponse,
    AcceleratorProgrammeDTO, 
    DurationDTO, 
    InvestmentTermsDTO,
    MoneyDTO,
    OrganisationResponse,
    AcceleratorDetailsResponse,
    InvestorDetailsResponse,
    StartupDetailsResponse
)


def to_startup_response(
    organisation: Organisation,
) -> StartupResponse:
    startup = organisation.get_classification_model(
        OrganisationClassification.STARTUP
    )

    if startup is None:
        raise ValueError(
            "Organisation has no registered startup model."
        )

    return StartupResponse(
        id=organisation.reference.value,
        canonical_name=organisation.representations.canonical_name,
        aliases=sorted(organisation.representations.aliases),
        founding_year=startup.founding_year,
        stage=startup.stage,
        business_model=startup.business_model,
    )

def to_investor_response(
    organisation: Organisation,
) -> InvestorResponse:
    investor = organisation.get_classification_model(
        OrganisationClassification.INVESTOR
    )

    if investor is None:
        raise ValueError("Organisation has no investor model.")

    return InvestorResponse(
        id=organisation.reference.value,
        canonical_name=organisation.representations.canonical_name,
        aliases=sorted(organisation.representations.aliases),
        investor_type=investor.get_investor_type(),
        investment_stage=investor.get_investor_stage(),
    )


def to_incubator_response(
    organisation: Organisation,
) -> IncubatorResponse:
    if not organisation.has_classification(
        OrganisationClassification.INCUBATOR
    ):
        raise ValueError("Organisation is not classified as an incubator.")

    return IncubatorResponse(
        id=organisation.reference.value,
        canonical_name=organisation.representations.canonical_name,
        aliases=sorted(organisation.representations.aliases),
    )


def to_accelerator_response(
    organisation: Organisation,
) -> AcceleratorResponse:
    accelerator = organisation.get_classification_model(
        OrganisationClassification.ACCELERATOR
    )

    if accelerator is None:
        raise ValueError("Organisation has no accelerator model.")

    programmes = []

    for programme in accelerator.programmes:
        programmes.append(
            AcceleratorProgrammeDTO(
                name=programme.name,
                duration=DurationDTO(
                    value=programme.duration.value,
                    unit=programme.duration.unit,
                    start_date=programme.duration.start_date,
                    end_date=programme.duration.end_date,
                ),
                investment_terms=InvestmentTermsDTO(
                    money=MoneyDTO(
                        amount=programme.investment_terms.money.amount,
                        currency=programme.investment_terms.money.currency,
                    ),
                    equity_percentage=(
                        programme.investment_terms.equity_percentage
                    ),
                ),
            )
        )

    return AcceleratorResponse(
        id=organisation.reference.value,
        canonical_name=organisation.representations.canonical_name,
        aliases=sorted(organisation.representations.aliases),
        programmes=programmes,
    )



def to_organisation_response(
    organisation: Organisation,
) -> OrganisationResponse:
    classifications = organisation.get_classifications()

    startup_details = None
    investor_details = None
    accelerator_details = None

    if OrganisationClassification.STARTUP in classifications:
        startup: Startup = organisation.get_classification_model(
            OrganisationClassification.STARTUP
        )

        startup_details = StartupDetailsResponse(
            founding_year=startup.founding_year,
            stage=startup.stage,
            business_model=startup.business_model,
        )

    if OrganisationClassification.INVESTOR in classifications:
        investor = organisation.get_classification_model(
            OrganisationClassification.INVESTOR
        )

        investor_details = InvestorDetailsResponse(
            investor_type=investor.investor_type,
            investment_stage=investor.investment_stage,
        )

    if OrganisationClassification.ACCELERATOR in classifications:
        accelerator: Accelerator = (
            organisation.get_classification_model(
                OrganisationClassification.ACCELERATOR
            )
        )

        accelerator_details = AcceleratorDetailsResponse(
            programmes=[
                AcceleratorProgrammeDTO(
                    name=programme.name,
                    duration=DurationDTO(
                        value=programme.duration.value,
                        unit=programme.duration.unit,
                        start_date=programme.duration.start_date,
                        end_date=programme.duration.end_date,
                    ),
                    investment_terms=InvestmentTermsDTO(
                        money=MoneyDTO(
                            amount=programme.investment_terms.money.amount,
                            currency=programme.investment_terms.money.currency,
                        ),
                        equity_percentage=(
                            programme.investment_terms.equity_percentage
                        ),
                    ),
                )
                for programme in accelerator.programmes
            ]
        )

    return OrganisationResponse(
        id=organisation.reference.value,
        canonical_name=organisation.representations.canonical_name,
        aliases=sorted(organisation.representations.aliases),
        classifications=sorted(
            classifications,
            key=lambda classification: classification.value,
        ),
        startup=startup_details,
        investor=investor_details,
        accelerator=accelerator_details,
        incubator=(
            OrganisationClassification.INCUBATOR in classifications
        ),
    )
#