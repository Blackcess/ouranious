from dataclasses import dataclass
from decimal import Decimal
from datetime import date
from enum import StrEnum

class FoundingStage(StrEnum):
    IDEA = "idea"                          # Organisation is being conceptualised; no operational business yet.
    PRE_SEED = "pre_seed"                  # Organization is in the early stages of development, typically before any significant funding has been raised.
    SEED = "seed"                          # Organization has received initial funding to develop its product or service and start building its team.
    EARLY_STAGE = "early_stage"            # Organization has a product or service in the market and is focused on scaling its operations and customer base.
    GROWTH_STAGE = "growth_stage"          # Organization is experiencing rapid growth in revenue, customers, and market share, and is focused on expanding its operations and market presence.
    LATE_STAGE = "late_stage"              # Organization is well-established and has a proven track record of success, with a focus on maintaining its market position and profitability.
    MATURE = "mature"                      # Organization has reached a stable and sustainable level of growth, with a focus on maintaining its market position and profitability.
    RESTART = "restart"                    # Organization has undergone a significant change or pivot in its business model, strategy, or leadership, and is focused on rebuilding and repositioning itself in the market.

@dataclass(frozen=True)
class FounderProperties:
    founding_date: date | None = None
    founder_role: str | None = None
    founding_stage: FoundingStage | None = None

    def __post_init__(self):
        # validate if founding date is datetime.date object
        if self.founding_date is not None and not isinstance(self.founding_date, date):
            raise TypeError("Founding date must be a datetime.date object.")
        # validate founding date is not in the future
        if self.founding_date is not None and self.founding_date > date.today():
            raise ValueError("Founding date cannot be in the future.")
        # validate founding stage is a valid option
        if self.founding_stage is not None and self.founding_stage not in FoundingStage:
            raise ValueError("Invalid founding stage.")