from pydantic import BaseModel, ConfigDict, Field, model_validator
from uuid import UUID
from datetime import date
from decimal import Decimal

from domain_models.Identity_model.Organisation_model.classification_specific_domain_model.startup.start_up import (
    StartupStages,
    StartupBusinessModels,
)
from domain_models.Identity_model.Organisation_model.organisation import Organisation
from domain_models.Identity_model.Organisation_model.organisation_classification import (
    OrganisationClassification,
)
from domain_models.Identity_model.Organisation_model.classification_specific_domain_model.investor.investor import (
    InvestmentTypes,
    InvestmentStage,
)
from domain_models.Identity_model.Organisation_model.classification_specific_domain_model.accelerator.accelerator_programme import (
    AcceleratorProgramme,
    InvestmentTerms,
)
from utils.representations import Money, Duration, DurationUnit

# ==================================
#  START UP DTOs
# ==================================

class CreateStartupRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")

    canonical_name: str = Field(
        min_length=1,
        max_length=255,
    )

    founding_year: int = Field(gt=0)

    stage: StartupStages

    business_model: StartupBusinessModels

    aliases: list[str] = Field(default_factory=list)


class StartupResponse(BaseModel):
    model_config = ConfigDict(extra="forbid")

    id: UUID
    canonical_name: str
    aliases: list[str]
    founding_year: int
    stage: StartupStages
    business_model: StartupBusinessModels



# ==========================================
# INVESTOR DTOs
# ==========================================

class CreateInvestorRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")

    canonical_name: str = Field(min_length=1, max_length=255)
    investor_type: InvestmentTypes
    investment_stage: InvestmentStage
    aliases: list[str] = Field(default_factory=list)


class InvestorResponse(BaseModel):
    model_config = ConfigDict(extra="forbid")

    id: UUID
    canonical_name: str
    aliases: list[str]
    investor_type: InvestmentTypes
    investment_stage: InvestmentStage

# =========================================================
# INCUBATOR DTOs
# =========================================================


class CreateIncubatorRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")

    canonical_name: str = Field(min_length=1, max_length=255)
    aliases: list[str] = Field(default_factory=list)


class IncubatorResponse(BaseModel):
    model_config = ConfigDict(extra="forbid")

    id: UUID
    canonical_name: str
    aliases: list[str]

# =========================================
# ACCELERATOR DTO
# ========================================

class MoneyDTO(BaseModel):
    model_config = ConfigDict(extra="forbid")

    amount: Decimal = Field(ge=0)
    currency: str = Field(min_length=3, max_length=3)


class DurationDTO(BaseModel):
    model_config = ConfigDict(extra="forbid")

    value: Decimal = Field(gt=0)
    unit: str = Field(min_length=1)
    start_date: date | None = None
    end_date: date | None = None

    @model_validator(mode="after")
    def validate_dates(self):
        if (
            self.start_date is not None
            and self.end_date is not None
            and self.end_date < self.start_date
        ):
            raise ValueError("end_date cannot precede start_date")

        return self


class InvestmentTermsDTO(BaseModel):
    model_config = ConfigDict(extra="forbid")

    money: MoneyDTO
    equity_percentage: Decimal = Field(ge=0, le=100)


class AcceleratorProgrammeDTO(BaseModel):
    model_config = ConfigDict(extra="forbid")

    name: str = Field(min_length=1, max_length=255)
    duration: DurationDTO
    investment_terms: InvestmentTermsDTO

class CreateAcceleratorRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")

    canonical_name: str = Field(min_length=1, max_length=255)
    aliases: list[str] = Field(default_factory=list)
    programmes: list[AcceleratorProgrammeDTO] = Field(
        default_factory=list
    )


class AcceleratorResponse(BaseModel):
    model_config = ConfigDict(extra="forbid")

    id: UUID
    canonical_name: str
    aliases: list[str]
    programmes: list[AcceleratorProgrammeDTO]

def to_accelerator_programme(
    dto: AcceleratorProgrammeDTO,
) -> AcceleratorProgramme:
    duration = Duration(
        value=dto.duration.value,
        unit=dto.duration.unit,
        start_date=dto.duration.start_date,
        end_date=dto.duration.end_date,
    )

    money = Money(
        amount=dto.investment_terms.money.amount,
        currency=dto.investment_terms.money.currency,
    )

    investment_terms = InvestmentTerms(
        money=money,
        equity_percentage=dto.investment_terms.equity_percentage,
    )

    return AcceleratorProgramme(
        name=dto.name,
        duration=duration,
        investment_terms=investment_terms,
    )

# ======================================
# ORGANISATION RETRIVAL RESPONSE DTO
# =====================================

class StartupDetailsResponse(BaseModel):
    founding_year: int
    stage: StartupStages
    business_model: StartupBusinessModels


class InvestorDetailsResponse(BaseModel):
    investor_type: InvestmentTypes
    investment_stage: InvestmentStage


class AcceleratorDetailsResponse(BaseModel):
    programmes: list[AcceleratorProgrammeDTO] = Field(
        default_factory=list
    )


class OrganisationResponse(BaseModel):
    model_config = ConfigDict(extra="forbid")

    id: UUID
    canonical_name: str
    aliases: list[str]
    classifications: list[OrganisationClassification]

    startup: StartupDetailsResponse | None = None
    investor: InvestorDetailsResponse | None = None
    accelerator: AcceleratorDetailsResponse | None = None
    incubator: bool = False
